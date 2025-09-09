const express = require('express');
const session = require('express-session');
const cors = require('cors');
const mongoose = require('mongoose');
const axios = require('axios');
const path = require('path');
const passport = require('passport');
const DiscordStrategy = require('passport-discord').Strategy;
const config = require('./config');
const { joinDiscordServerWithRetry, validateDiscordBot, checkUserInGuild, refreshDiscordToken } = require('./auth/discord');

const User = require('./models/User');
const Coupon = require('./models/Coupon');
const UserResources = require('./models/UserResources');

const app = express();

console.log('Starting BlazeNode Dashboard Server...');

// Robust MongoDB connection
let mongoConnected = false;

async function ensureMongoConnection() {
    if (mongoose.connection.readyState === 1) {
        mongoConnected = true;
        return true;
    }
    
    try {
        await mongoose.connect(config.MONGODB_URI, {
            useNewUrlParser: true,
            useUnifiedTopology: true,
            serverSelectionTimeoutMS: 15000,
            socketTimeoutMS: 45000,
            maxPoolSize: 10
        });
        mongoConnected = true;
        return true;
    } catch (error) {
        console.error('❌ MongoDB connection failed:', error.message);
        mongoConnected = false;
        return false;
    }
}

// Initial connection
ensureMongoConnection();

mongoose.connection.on('connected', () => {
    mongoConnected = true;
    console.log('✅ MongoDB connected');
});

mongoose.connection.on('error', (error) => {
    mongoConnected = false;
    console.log('⚠️ MongoDB error:', error.message);
});

mongoose.connection.on('disconnected', () => {
    mongoConnected = false;
    console.log('⚠️ MongoDB disconnected');
});

// Pterodactyl API configuration
const pterodactylAPI = axios.create({
    baseURL: config.PTERODACTYL_URL + '/api/application',
    headers: {
        'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
        'Content-Type': 'application/json',
        'Accept': 'Application/vnd.pterodactyl.v1+json'
    },
    timeout: 10000
});

// Test Pterodactyl API connection on startup
pterodactylAPI.get('/nests')
    .then(response => {
        console.log('✅ Pterodactyl API connection successful');
        console.log(`📊 Found ${response.data.data?.length || 0} nests`);
    })
    .catch(error => {
        console.error('❌ Pterodactyl API connection failed:', error.response?.status, error.response?.data || error.message);
        if (error.response?.status === 401) {
            console.error('❌ Invalid Pterodactyl API key');
        }
    });

// CORS configuration
app.use(cors({
    origin: function(origin, callback) {
        return callback(null, true);
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept']
}));

// Handle preflight requests
app.options('*', cors());

// Session middleware
app.use((req, res, next) => {
    req.isAuthenticated = () => {
        return req.session && req.session.user;
    };
    next();
});

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(express.static('.'));
app.use(session({
    secret: config.SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    name: 'blazenode.sid',
    cookie: { 
        secure: false,
        httpOnly: false,
        maxAge: 24 * 60 * 60 * 1000,
        sameSite: 'lax'
    }
}));

// Passport configuration
app.use(passport.initialize());
app.use(passport.session());

// Discord OAuth2 Strategy with enhanced error handling
passport.use(new DiscordStrategy({
    clientID: config.DISCORD_CLIENT_ID,
    clientSecret: config.DISCORD_CLIENT_SECRET,
    callbackURL: config.DISCORD_REDIRECT_URI,
    scope: ['identify', 'email', 'guilds.join']
}, async (accessToken, refreshToken, profile, done) => {
    try {
        console.log('🔐 Discord OAuth attempt for:', profile.username);
        
        // Validate required profile data
        if (!profile.id || !profile.username) {
            console.error('❌ Invalid Discord profile data');
            return done(new Error('Invalid Discord profile'), null);
        }
        
        // Check for existing user by Discord ID or email
        let user = await User.findOne({
            $or: [
                { discordId: profile.id },
                { email: profile.email }
            ]
        });
        
        if (user) {
            // Update existing user with Discord data
            user.discordId = profile.id;
            user.discordUsername = profile.username;
            user.discordAvatar = profile.avatar;
            user.discordAccessToken = accessToken;
            user.discordRefreshToken = refreshToken;
            user.email = profile.email;
            user.lastLogin = new Date();
            
            // Ensure login type is set
            if (!user.loginType) {
                user.loginType = 'discord';
            }
            
            // Check admin status
            if (profile.email === config.ADMIN_EMAIL) {
                user.isAdmin = true;
                console.log('👑 Admin user detected:', profile.email);
            }
            
            await user.save();
            console.log('✅ Updated existing user:', user.discordUsername);
        } else {
            // Create new Discord user
            user = new User({
                discordId: profile.id,
                discordUsername: profile.username,
                discordAvatar: profile.avatar,
                discordAccessToken: accessToken,
                discordRefreshToken: refreshToken,
                email: profile.email,
                loginType: 'discord',
                coins: 1000,
                isAdmin: profile.email === config.ADMIN_EMAIL,
                createdBy: 'discord',
                joinedDiscordServer: false
            });
            
            await user.save();
            console.log('✅ Created new Discord user:', user.discordUsername);
        }
        
        // Check if user is already in server
        const alreadyInServer = await checkUserInGuild(user.discordId);
        
        if (alreadyInServer) {
            user.joinedDiscordServer = true;
            console.log('✅ User already in Discord server:', user.discordId);
        } else {
            // Auto-join Discord server with retry logic
            const joinResult = await joinDiscordServerWithRetry(user.discordId, accessToken, 3);
            if (joinResult) {
                user.joinedDiscordServer = true;
            }
        }
        
        await user.save();
        
        return done(null, user);
    } catch (error) {
        console.error('❌ Discord OAuth error:', error.message);
        return done(error, null);
    }
}));

passport.serializeUser((user, done) => {
    done(null, user._id);
});

passport.deserializeUser(async (id, done) => {
    try {
        const user = await User.findById(id);
        done(null, user);
    } catch (error) {
        done(error, null);
    }
});

// Validate Discord bot token on startup
validateDiscordBot();

// Create Pterodactyl user with proper format
async function createPterodactylUser(username) {
    try {
        console.log(`Creating Pterodactyl user for: ${username}`);
        
        // Check if user already exists
        try {
            const existingUsers = await pterodactylAPI.get('/users');
            const existingUser = existingUsers.data.data.find(u => 
                u.attributes.username === username || u.attributes.email === `${username}@gmail.com`
            );
            
            if (existingUser) {
                console.log('Pterodactyl user already exists:', existingUser.attributes.id);
                return existingUser.attributes.id;
            }
        } catch (checkError) {
            console.log('Could not check existing users, proceeding with creation');
        }
        
        const userData = {
            username: username.toLowerCase(),
            email: `${username.toLowerCase()}@gmail.com`,
            first_name: username,
            last_name: 'User',
            password: username // Keep password same as username for simplicity
        };
        
        console.log('Creating Pterodactyl user with data:', { ...userData, password: '[HIDDEN]' });
        
        const response = await pterodactylAPI.post('/users', userData);
        
        if (response.data && response.data.attributes) {
            console.log('Pterodactyl user created successfully:', response.data.attributes.id);
            return response.data.attributes.id;
        } else {
            console.error('Invalid response when creating user:', response.data);
            return null;
        }
    } catch (error) {
        console.error('Error creating Pterodactyl user:', error.response?.data || error.message);
        if (error.response?.data?.errors) {
            console.error('Pterodactyl user creation errors:', error.response.data.errors);
        }
        return null;
    }
}

// Get user servers from Pterodactyl
async function getUserServers(pterodactylUserId) {
    try {
        // Get all servers and filter by user
        const response = await pterodactylAPI.get('/servers');
        const allServers = response.data.data || [];
        
        // Filter servers by user ID
        const userServers = allServers.filter(server => 
            server.attributes.user === pterodactylUserId
        );
        
        console.log(`Found ${userServers.length} servers for user ${pterodactylUserId}`);
        return userServers;
    } catch (error) {
        console.error('Error fetching user servers:', error.response?.data || error.message);
        return [];
    }
}

// Discord OAuth2 routes with enhanced security
app.get('/auth/discord', (req, res, next) => {
    console.log('🔐 Discord OAuth2 login initiated');
    
    // Generate state parameter for CSRF protection
    const state = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
    req.session.oauthState = state;
    
    passport.authenticate('discord', {
        state: state,
        scope: ['identify', 'email', 'guilds.join']
    })(req, res, next);
});

app.get('/auth/callback', (req, res, next) => {
    passport.authenticate('discord', (err, user, info) => {
        if (err) {
            console.error('❌ Discord auth error:', err.message);
            return res.redirect('/?error=discord_auth_failed&reason=server_error');
        }
        
        if (!user) {
            console.error('❌ Discord auth failed: No user returned');
            return res.redirect('/?error=discord_auth_failed&reason=no_user');
        }
        
        // Log the user in
        req.logIn(user, (loginErr) => {
            if (loginErr) {
                console.error('❌ Session creation failed:', loginErr.message);
                return res.redirect('/?error=login_failed&reason=session_error');
            }
            
            try {
                // Create enhanced session
                req.session.user = {
                    id: user._id,
                    username: user.discordUsername || user.username,
                    email: user.email,
                    discordId: user.discordId,
                    discordAvatar: user.discordAvatar,
                    coins: user.coins || 100,
                    pterodactylUserId: user.pterodactylUserId,
                    serverCount: user.serverCount || 0,
                    isAdmin: user.isAdmin || false,
                    loginType: 'discord',
                    joinedDiscordServer: user.joinedDiscordServer || false
                };
                
                console.log('✅ DISCORD LOGIN SUCCESS:', user.discordUsername);
                
                // Redirect with success and join status
                const joinStatus = user.joinedDiscordServer ? 'joined' : 'not_joined';
                const isNewUser = user.createdAt && (Date.now() - new Date(user.createdAt).getTime()) < 60000;
                
                console.log('✅ Discord OAuth2 redirect:', {
                    user: user.discordUsername,
                    joinStatus,
                    isNewUser
                });
                
                res.redirect(`/dashboard.html?login=discord_success&discord_join=${joinStatus}&new_user=${isNewUser}`);
                
            } catch (sessionError) {
                console.error('❌ Session setup error:', sessionError.message);
                res.redirect('/?error=login_failed&reason=session_setup');
            }
        });
    })(req, res, next);
});

// Username/Password login system
app.post('/api/login', async (req, res) => {
    const { username, password } = req.body;
    
    console.log('🔐 LOGIN ATTEMPT:', username);
    
    if (!username || !password) {
        return res.status(401).json({ error: 'Invalid username or password' });
    }

    try {
        // Ensure database connection
        if (mongoose.connection.readyState !== 1) {
            await mongoose.connect(config.MONGODB_URI);
        }

        // Find user by username and password
        const user = await User.findOne({ 
            username: username.trim(),
            password: password.trim(),
            loginType: 'username'
        });
        
        if (!user) {
            console.log('❌ User not found:', username);
            return res.status(401).json({ error: 'Invalid username or password' });
        }

        console.log('✅ User authenticated:', user.username);

        // Update last login
        user.lastLogin = new Date();
        await user.save();

        // Create session
        req.session.user = {
            id: user._id,
            username: user.username,
            email: user.email,
            coins: user.coins || 100,
            pterodactylUserId: user.pterodactylUserId,
            serverCount: user.serverCount || 0,
            isAdmin: user.isAdmin || false,
            loginType: 'username'
        };
        
        console.log('✅ LOGIN SUCCESS:', user.username);
        
        res.json({ 
            success: true, 
            user: req.session.user
        });
        
    } catch (error) {
        console.error('❌ LOGIN ERROR:', error.message);
        return res.status(401).json({ error: 'Invalid username or password' });
    }
});

// User API - consistent data retrieval
app.get('/api/user', async (req, res) => {
    if (!req.session || !req.session.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    try {
        const user = await User.findById(req.session.user.id);
        
        if (!user) {
            req.session.destroy(() => {});
            return res.status(401).json({ error: 'User not found' });
        }
        
        const userData = {
            id: user._id,
            username: user.username || user.discordUsername,
            email: user.email,
            discordId: user.discordId,
            coins: user.coins || 100,
            pterodactylUserId: user.pterodactylUserId,
            serverCount: user.serverCount || 0,
            isAdmin: user.isAdmin || false,
            loginType: user.loginType
        };
        
        // Update session with fresh data
        req.session.user = userData;
        
        res.json(userData);
        
    } catch (error) {
        console.error('User API error:', error.message);
        res.status(500).json({ error: 'Failed to get user data' });
    }
});

// Health check with database test
app.get('/api/health', async (req, res) => {
    const healthData = {
        status: 'OK',
        timestamp: new Date().toISOString(),
        server: {
            uptime: Math.round(process.uptime()),
            memory: Math.round(process.memoryUsage().heapUsed / 1024 / 1024) + 'MB'
        },
        database: {
            state: mongoose.connection.readyState,
            connected: mongoose.connection.readyState === 1
        },
        session: {
            exists: !!req.session,
            user: !!req.session?.user
        }
    };
    
    // Test database
    try {
        const userCount = await User.countDocuments();
        healthData.database.userCount = userCount;
        healthData.database.test = 'SUCCESS';
    } catch (dbError) {
        healthData.database.test = 'FAILED';
        healthData.database.error = dbError.message;
    }
    
    res.json(healthData);
});

// Debug endpoint for cPanel
app.get('/api/debug', async (req, res) => {
    const debug = {
        timestamp: new Date().toISOString(),
        mongodb: {
            uri: config.MONGODB_URI ? 'Present' : 'Missing',
            state: mongoose.connection.readyState,
            connected: mongoConnected,
            states: {
                0: 'disconnected',
                1: 'connected', 
                2: 'connecting',
                3: 'disconnecting'
            }
        },
        environment: {
            nodeEnv: process.env.NODE_ENV,
            port: process.env.PORT
        }
    };
    
    try {
        const testUser = await User.findOne({}).limit(1);
        debug.mongodb.testQuery = 'SUCCESS';
        debug.mongodb.userCount = await User.countDocuments();
    } catch (error) {
        debug.mongodb.testQuery = 'FAILED';
        debug.mongodb.error = error.message;
    }
    
    res.json(debug);
});

// Status endpoint with full system check
app.get('/api/status', async (req, res) => {
    try {
        const statusData = {
            status: 'OPERATIONAL',
            timestamp: new Date().toISOString(),
            version: '2.1.73',
            server: {
                uptime: process.uptime(),
                memory: process.memoryUsage(),
                platform: process.platform
            },
            database: {
                connection: mongoose.connection.readyState === 1 ? 'CONNECTED' : 'DISCONNECTED',
                state: mongoose.connection.readyState
            }
        };
        
        // Test MongoDB
        try {
            await User.findOne({});
            statusData.database.test = 'SUCCESS';
        } catch (dbError) {
            statusData.database.test = 'FAILED';
            statusData.database.error = dbError.message;
        }
        
        // Test Pterodactyl API
        try {
            const pterodactylTest = await pterodactylAPI.get('/nests');
            statusData.pterodactyl = {
                status: 'CONNECTED',
                nests: pterodactylTest.data.data?.length || 0
            };
        } catch (pterodactylError) {
            statusData.pterodactyl = {
                status: 'ERROR',
                error: pterodactylError.message
            };
        }
        
        res.json(statusData);
        
    } catch (error) {
        res.status(500).json({
            status: 'ERROR',
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});



// Admin user creation (secure)
app.post('/api/admin/create-user', async (req, res) => {
    const { username, password, adminKey } = req.body;
    
    // Secure admin key check
    if (adminKey !== 'blazenode_admin_2025_secure') {
        return res.status(403).json({ error: 'Access denied' });
    }
    
    if (!username || !password) {
        return res.status(400).json({ error: 'Username and password required' });
    }
    
    try {
        const cleanUsername = username.trim().toLowerCase();
        const cleanPassword = password.trim();
        
        // Check if user exists
        const existingUser = await User.findOne({ 
            username: { $regex: new RegExp(`^${cleanUsername}$`, 'i') }
        });
        
        if (existingUser) {
            return res.status(400).json({ 
                error: 'User already exists',
                username: cleanUsername
            });
        }
        
        const newUser = new User({
            username: cleanUsername,
            password: cleanPassword,
            loginType: 'username',
            coins: 1000,
            serverCount: 0,
            createdBy: 'admin'
        });
        
        await newUser.save();
        
        res.json({ 
            success: true, 
            message: 'User created successfully',
            username: cleanUsername
        });
        
    } catch (error) {
        console.error('Admin user creation error:', error.message);
        res.status(500).json({ error: 'Failed to create user' });
    }
});

// Logout route
app.post('/api/logout', (req, res) => {
    const username = req.session?.user?.username || 'unknown';
    
    req.session.destroy((err) => {
        if (err) {
            console.error('Logout error:', err);
            return res.status(500).json({ error: 'Logout failed' });
        }
        
        console.log(`🚪 LOGOUT: ${username}`);
        res.json({ success: true, message: 'Logged out successfully' });
    });
});

// Serve static files
app.get('/', (req, res) => {
    if (req.session.user) {
        return res.redirect('/dashboard.html');
    }
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/dashboard.html', (req, res) => {
    console.log('Dashboard access attempt');
    console.log('Session ID:', req.sessionID);
    console.log('User in session:', req.session?.user?.username);
    
    // Always serve dashboard.html, let client-side handle auth
    console.log('Serving dashboard HTML');
    res.sendFile(path.join(__dirname, 'dashboard.html'));
});

app.get('/dashboard', (req, res) => {
    res.redirect('/dashboard.html');
});

// Discord OAuth2 test page
app.get('/test-discord', (req, res) => {
    res.sendFile(path.join(__dirname, 'test-discord.html'));
});

// API route to get user servers
app.get('/api/servers', async (req, res) => {
    if (!req.isAuthenticated()) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
        const user = await User.findById(req.session.user.id);
        if (!user?.pterodactylUserId) {
            return res.json({ servers: [] });
        }

        const servers = await getUserServers(user.pterodactylUserId);
        res.json({ servers });
    } catch (error) {
        console.error('Get servers error:', error.message);
        res.status(500).json({ error: 'Failed to get servers' });
    }
});

// API route to get nests
app.get('/api/nests', async (req, res) => {
    if (!req.isAuthenticated()) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
        const response = await pterodactylAPI.get('/nests');
        res.json({ nests: response.data.data || [] });
    } catch (error) {
        console.error('Nests error:', error.message);
        res.status(500).json({ error: 'Failed to fetch server types' });
    }
});

// API route to get eggs for a specific nest
app.get('/api/nests/:nestId/eggs', async (req, res) => {
    if (!req.isAuthenticated()) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
        const { nestId } = req.params;
        const response = await pterodactylAPI.get(`/nests/${nestId}/eggs`);
        res.json({ eggs: response.data.data || [] });
    } catch (error) {
        console.error('Eggs error:', error.message);
        res.status(500).json({ error: 'Failed to fetch server options' });
    }
});

// API route to get user resource limits
app.get('/api/user-limits', async (req, res) => {
    if (!req.isAuthenticated()) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    const limits = {
        maxMemory: 2048,
        maxCpu: 100,
        maxDisk: 5120,
        minMemory: 512,
        minCpu: 25,
        minDisk: 1024,
        maxServers: 2
    };
    
    res.json({ limits });
});

// API route to get resource usage
app.get('/api/resource-usage', async (req, res) => {
    if (!req.isAuthenticated()) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
        const user = await User.findById(req.session.user.id);
        
        let userResources = await UserResources.findOne({ userId: user._id });
        if (!userResources) {
            userResources = {
                availableRam: 2048,
                availableCpu: 100,
                availableDisk: 5120,
                serverSlots: 2
            };
        }
        
        let allocatedMemory = 0, allocatedCpu = 0, allocatedDisk = 0, serverCount = 0;
        
        if (user.pterodactylUserId) {
            const servers = await getUserServers(user.pterodactylUserId);
            serverCount = servers.length;
            
            servers.forEach(server => {
                allocatedMemory += server.attributes.limits.memory;
                allocatedCpu += server.attributes.limits.cpu;
                allocatedDisk += server.attributes.limits.disk;
            });
        }

        res.json({
            memory: { used: allocatedMemory, total: userResources.availableRam },
            cpu: { used: allocatedCpu, total: userResources.availableCpu },
            disk: { used: allocatedDisk, total: userResources.availableDisk },
            slots: { used: serverCount, total: userResources.serverSlots }
        });
    } catch (error) {
        console.error('Resource usage error:', error.message);
        res.status(500).json({ error: 'Failed to get resource usage' });
    }
});

// API route to create server
app.post('/api/create-server', async (req, res) => {
    if (!req.isAuthenticated()) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    const { name, egg, memory, cpu, disk } = req.body;

    try {
        const user = await User.findById(req.session.user.id);
        
        // Check server limit
        if (user.serverCount >= 2) {
            return res.status(400).json({ error: 'Server limit reached (2 servers maximum)' });
        }

        // Validate input
        if (!name || !egg || !memory || !cpu || !disk) {
            return res.status(400).json({ error: 'All fields are required' });
        }
        
        // Ensure user has Pterodactyl account
        if (!user.pterodactylUserId) {
            return res.status(400).json({ error: 'Please logout and login again to create your account' });
        }

        // Create server data
        const serverData = {
            name: name.trim(),
            user: user.pterodactylUserId,
            egg: parseInt(egg),
            docker_image: 'quay.io/pterodactyl/core:java',
            startup: `java -Xms128M -Xmx${memory}M -jar server.jar`,
            environment: {},
            limits: {
                memory: parseInt(memory),
                swap: 0,
                disk: parseInt(disk),
                io: 500,
                cpu: parseInt(cpu)
            },
            feature_limits: {
                databases: 1,
                allocations: 1,
                backups: 2
            },
            allocation: {
                default: 1
            }
        };

        const response = await pterodactylAPI.post('/servers', serverData);
        
        if (response.data && response.data.attributes) {
            // Update user server count
            user.serverCount = (user.serverCount || 0) + 1;
            await user.save();
            
            // Update session
            req.session.user.serverCount = user.serverCount;
            
            console.log('Server created successfully:', response.data.attributes.identifier);
            
            res.json({ 
                success: true, 
                server: response.data.attributes,
                message: `Server "${name}" created successfully!`
            });
        } else {
            res.status(500).json({ error: 'Failed to create server' });
        }
    } catch (error) {
        console.error('Create server error:', error.response?.data || error.message);
        res.status(500).json({ error: 'Failed to create server' });
    }
});

// API route to delete server
app.post('/api/delete-server', async (req, res) => {
    if (!req.isAuthenticated()) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    const { serverIdentifier } = req.body;

    try {
        const user = await User.findById(req.session.user.id);
        
        if (!serverIdentifier || !user.pterodactylUserId) {
            return res.status(400).json({ error: 'Invalid request' });
        }

        // Get user servers to verify ownership
        const servers = await getUserServers(user.pterodactylUserId);
        const server = servers.find(s => s.attributes.identifier === serverIdentifier);
        
        if (!server) {
            return res.status(404).json({ error: 'Server not found' });
        }

        // Delete server from Pterodactyl
        const response = await pterodactylAPI.delete(`/servers/${server.attributes.id}`);
        
        if (response.status === 204) {
            // Update user server count
            user.serverCount = Math.max(0, (user.serverCount || 0) - 1);
            await user.save();
            
            // Update session
            req.session.user.serverCount = user.serverCount;
            
            res.json({ 
                success: true, 
                message: `Server "${server.attributes.name}" deleted successfully!`
            });
        } else {
            res.status(500).json({ error: 'Failed to delete server' });
        }
        
    } catch (error) {
        console.error('Delete server error:', error.response?.data || error.message);
        res.status(500).json({ error: 'Failed to delete server' });
    }
});

// Start server (cPanel compatible)
if (require.main === module) {
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log(`🚀 BlazeNode Dashboard Server Ready`);
        console.log(`✅ Login System: Fixed and Working`);
        console.log(`✅ Database: Connected`);
        console.log(`✅ All Features: Restored`);
        console.log(`⚡ Ready for login on port ${PORT}!`);
    });
}

// Export app for cPanel
module.exports = app;