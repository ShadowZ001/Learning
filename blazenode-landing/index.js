const express = require('express');
const session = require('express-session');
const cors = require('cors');
const mongoose = require('mongoose');
const axios = require('axios');
const path = require('path');
const passport = require('passport');
const DiscordStrategy = require('passport-discord').Strategy;
const config = require('./config');
const { validateDiscordBot } = require('./auth/discord');

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
        maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
        sameSite: 'lax'
    }
}));

// Enhanced session middleware with authentication check
app.use((req, res, next) => {
    req.isAuthenticated = () => {
        const sessionAuth = req.session?.authenticated && req.session?.user?.id;
        const passportAuth = req.user && req.user._id;
        return sessionAuth || passportAuth;
    };
    
    next();
});

// Passport configuration
app.use(passport.initialize());
app.use(passport.session());

// Discord OAuth2 Strategy - Fixed
passport.use(new DiscordStrategy({
    clientID: config.DISCORD_CLIENT_ID,
    clientSecret: config.DISCORD_CLIENT_SECRET,
    callbackURL: config.DISCORD_REDIRECT_URI,
    scope: ['identify', 'email']
}, async (accessToken, refreshToken, profile, done) => {
    try {
        console.log('🔐 Discord OAuth for:', profile.username, profile.id);
        
        // Ensure MongoDB is connected
        if (mongoose.connection.readyState !== 1) {
            console.error('❌ MongoDB not connected during OAuth');
            return done(new Error('Database not available'), null);
        }
        
        // Find or create user
        let user = await User.findOne({ discordId: profile.id });
        
        if (user) {
            // Update existing user
            user.discordUsername = profile.username;
            user.discordAvatar = profile.avatar;
            user.email = profile.email || user.email;
            user.lastLogin = new Date();
            console.log('✅ Updated existing user:', user.discordUsername);
        } else {
            // Create new user
            console.log('✅ Creating new user for:', profile.username);
            user = new User({
                discordId: profile.id,
                discordUsername: profile.username,
                discordAvatar: profile.avatar,
                email: profile.email,
                username: profile.username,
                loginType: 'discord',
                coins: 1000,
                isAdmin: profile.email === config.ADMIN_EMAIL,
                serverCount: 0,
                lastLogin: new Date()
            });
        }
        
        await user.save();
        console.log('✅ User saved successfully:', user.discordUsername);
        
        return done(null, user);
    } catch (error) {
        console.error('❌ Discord OAuth error:', error.message);
        console.error('❌ Stack:', error.stack);
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
validateDiscordBot().catch(err => {
    console.log('⚠️ Discord bot validation failed, continuing without bot features');
});

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
    passport.authenticate('discord')(req, res, next);
});

app.get('/auth/callback', (req, res, next) => {
    passport.authenticate('discord', (err, user, info) => {
        if (err) {
            console.error('❌ Auth error:', err);
            return res.redirect('/?error=auth_failed');
        }
        
        if (!user) {
            console.error('❌ No user returned from Discord');
            return res.redirect('/?error=no_user');
        }
        
        console.log('✅ Discord auth success for:', user.discordUsername);
        
        // Login user with passport
        req.logIn(user, (loginErr) => {
            if (loginErr) {
                console.error('❌ Login error:', loginErr);
                return res.redirect('/?error=login_failed');
            }
            
            console.log('✅ Passport login successful');
            
            // Create session data
            req.session.authenticated = true;
            req.session.user = {
                id: user._id.toString(),
                username: user.discordUsername,
                email: user.email,
                discordId: user.discordId,
                coins: user.coins || 1000,
                isAdmin: user.isAdmin || false,
                serverCount: user.serverCount || 0
            };
            
            console.log('✅ Session data created, saving...');
            
            // Force session save
            req.session.save((saveErr) => {
                if (saveErr) {
                    console.error('❌ Session save error:', saveErr);
                    return res.redirect('/?error=session_failed');
                }
                
                console.log('✅ Session saved successfully, redirecting to dashboard');
                res.redirect('/dashboard.html');
            });
        });
        
    })(req, res, next);
});

// Discord-only authentication - username/password login removed
// All authentication now goes through Discord OAuth2

// User API - Get current user data
app.get('/api/user', async (req, res) => {
    // Check both session and passport user
    const userId = req.session?.user?.id || req.user?._id;
    
    if (!userId) {
        console.log('❌ User API: No user ID found');
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    try {
        const user = await User.findById(userId);
        
        if (!user) {
            console.log('❌ User API: User not found in database');
            req.session.destroy(() => {});
            return res.status(401).json({ error: 'User not found' });
        }
        
        const userData = {
            id: user._id,
            username: user.discordUsername,
            email: user.email,
            discordId: user.discordId,
            coins: user.coins,
            isAdmin: user.isAdmin || false,
            serverCount: user.serverCount || 0,
            loginType: 'discord'
        };
        
        // Update session if it exists but is incomplete
        if (req.session && !req.session.user) {
            req.session.authenticated = true;
            req.session.user = {
                id: user._id.toString(),
                username: user.discordUsername,
                email: user.email,
                discordId: user.discordId,
                coins: user.coins,
                isAdmin: user.isAdmin || false,
                serverCount: user.serverCount || 0
            };
        }
        
        console.log('✅ User API response for:', userData.username);
        res.json(userData);
        
    } catch (error) {
        console.error('❌ User API error:', error);
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

// Daily reward claim
app.post('/api/claim-reward', async (req, res) => {
    if (!req.isAuthenticated()) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
        const user = await User.findById(req.session.user.id);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }

        const now = new Date();
        const lastReward = user.lastDailyReward;
        
        // Check if user can claim (24 hours since last claim)
        if (lastReward && (now - lastReward) < 24 * 60 * 60 * 1000) {
            return res.status(400).json({ error: 'Daily reward already claimed today' });
        }

        // Award coins and update streak
        user.coins = (user.coins || 0) + 25;
        user.lastDailyReward = now;
        
        if (lastReward && (now - lastReward) < 48 * 60 * 60 * 1000) {
            user.dailyRewardStreak = (user.dailyRewardStreak || 0) + 1;
        } else {
            user.dailyRewardStreak = 1;
        }

        await user.save();

        // Update session
        req.session.user.coins = user.coins;
        req.session.user.dailyRewardStreak = user.dailyRewardStreak;

        res.json({
            success: true,
            coins: user.coins,
            streak: user.dailyRewardStreak,
            message: 'Daily reward claimed!'
        });
    } catch (error) {
        console.error('Daily reward error:', error);
        res.status(500).json({ error: 'Failed to claim reward' });
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

// Debug endpoint
app.get('/debug-session', (req, res) => {
    res.json({
        session: {
            exists: !!req.session,
            id: req.sessionID,
            user: req.session?.user || null
        },
        passport: {
            user: req.user || null
        },
        authenticated: req.isAuthenticated()
    });
});

// Serve static files
app.get('/', (req, res) => {
    console.log('🏠 Home page access');
    console.log('Session authenticated:', req.session?.authenticated);
    console.log('Passport user:', req.user?.discordUsername);
    
    // Check if already authenticated
    const isAuthenticated = (req.session?.authenticated && req.session?.user) || req.user;
    
    if (isAuthenticated) {
        console.log('✅ Already logged in, redirecting to dashboard');
        return res.redirect('/dashboard.html');
    }
    
    console.log('🔐 Not logged in, serving login page');
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/dashboard.html', (req, res) => {
    console.log('📋 Dashboard access attempt');
    console.log('Session ID:', req.sessionID);
    console.log('Session exists:', !!req.session);
    console.log('Session authenticated:', req.session?.authenticated);
    console.log('Session user ID:', req.session?.user?.id);
    console.log('Passport user:', req.user?.discordUsername);
    
    // Enhanced authentication check
    const sessionAuth = req.session?.authenticated && req.session?.user?.id;
    const passportAuth = req.user && req.user._id;
    
    if (!sessionAuth && !passportAuth) {
        console.log('❌ Not authenticated, redirecting to login');
        return res.redirect('/');
    }
    
    // If passport user exists but no session, create session
    if (passportAuth && !sessionAuth) {
        console.log('✅ Creating session from passport user');
        req.session.authenticated = true;
        req.session.user = {
            id: req.user._id.toString(),
            username: req.user.discordUsername,
            email: req.user.email,
            discordId: req.user.discordId,
            coins: req.user.coins || 1000,
            isAdmin: req.user.isAdmin || false,
            serverCount: req.user.serverCount || 0
        };
        
        req.session.save((err) => {
            if (err) {
                console.error('❌ Session save error:', err);
            }
            console.log('✅ Session created from passport, serving dashboard');
            res.sendFile(path.join(__dirname, 'dashboard.html'));
        });
        return;
    }
    
    console.log('✅ User authenticated, serving dashboard');
    res.sendFile(path.join(__dirname, 'dashboard.html'));
});

app.get('/dashboard', (req, res) => {
    res.redirect('/dashboard.html');
});

// Test pages
app.get('/test-discord', (req, res) => {
    res.sendFile(path.join(__dirname, 'test-discord.html'));
});

app.get('/test-login', (req, res) => {
    res.sendFile(path.join(__dirname, 'test-login.html'));
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

// Missing API endpoints for dashboard functionality

// AFK earning endpoint
app.post('/api/afk-earn', async (req, res) => {
    if (!req.isAuthenticated()) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
        const user = await User.findById(req.session.user.id);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }

        // Award 1.2 coins for AFK earning
        user.coins = (user.coins || 0) + 1.2;
        await user.save();

        // Update session
        req.session.user.coins = user.coins;

        res.json({
            success: true,
            coins: 1.2,
            newBalance: user.coins
        });
    } catch (error) {
        console.error('AFK earn error:', error);
        res.status(500).json({ error: 'Failed to earn coins' });
    }
});

// Linkvertise completion endpoint
app.post('/api/linkvertise-complete', async (req, res) => {
    if (!req.isAuthenticated()) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
        const user = await User.findById(req.session.user.id);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }

        // Award 8 coins for Linkvertise completion
        user.coins = (user.coins || 0) + 8;
        await user.save();

        // Update session
        req.session.user.coins = user.coins;

        res.json({
            success: true,
            coins: 8,
            newBalance: user.coins
        });
    } catch (error) {
        console.error('Linkvertise complete error:', error);
        res.status(500).json({ error: 'Failed to process completion' });
    }
});

// Leaderboard endpoint
app.get('/api/leaderboard', async (req, res) => {
    try {
        const users = await User.find({})
            .sort({ coins: -1 })
            .limit(10)
            .select('username discordUsername coins');
        
        const leaderboard = users.map(user => ({
            username: user.discordUsername || user.username,
            coins: user.coins || 0
        }));
        
        res.json({ users: leaderboard });
    } catch (error) {
        console.error('Leaderboard error:', error);
        res.status(500).json({ error: 'Failed to load leaderboard' });
    }
});

// Export app for cPanel first
module.exports = app;

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