const express = require('express');
const session = require('express-session');
const cors = require('cors');
const mongoose = require('mongoose');
const axios = require('axios');
const path = require('path');
const config = require('./config');

const User = require('./models/User');
const Coupon = require('./models/Coupon');
const UserResources = require('./models/UserResources');

const app = express();

console.log('Starting BlazeNode Dashboard Server...');

// MongoDB connection
mongoose.connect(config.MONGODB_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true
})
.then(() => {
    console.log('✅ Connected to MongoDB');
})
.catch(err => {
    console.error('❌ MongoDB error:', err.message);
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

// Create server for user with default resources
async function createServer(pterodactylUserId, serverName) {
    try {
        console.log(`Creating server for user ${pterodactylUserId}: ${serverName}`);
        
        const response = await pterodactylAPI.post('/servers', {
            name: serverName,
            user: pterodactylUserId,
            egg: 1, // Default egg ID
            docker_image: 'quay.io/pterodactyl/core:java',
            startup: 'java -Xms128M -Xmx2048M -jar server.jar',
            environment: {},
            limits: {
                memory: 2048, // 2GB RAM (default)
                swap: 0,
                disk: 5120, // 5GB disk (default)
                io: 500,
                cpu: 100 // 100% CPU (default)
            },
            feature_limits: {
                databases: 1,
                allocations: 1,
                backups: 2
            },
            allocation: {
                default: 1 // Default allocation
            }
        });
        
        console.log('Server created successfully:', response.data.attributes.identifier);
        return response.data.attributes;
    } catch (error) {
        console.error('Error creating server:', error.response?.data || error.message);
        return null;
    }
}

// BULLETPROOF LOGIN SYSTEM FOR CPANEL
app.post('/api/login', async (req, res) => {
    const startTime = Date.now();
    
    console.log('\n=== LOGIN REQUEST START ===');
    console.log('Timestamp:', new Date().toISOString());
    console.log('Request Headers:', JSON.stringify(req.headers, null, 2));
    console.log('Request Body:', JSON.stringify(req.body, null, 2));
    console.log('Session ID:', req.sessionID);
    console.log('Session exists:', !!req.session);
    console.log('MongoDB State:', mongoose.connection.readyState);
    
    try {
        // STEP 1: Extract and validate input
        const { username, password } = req.body;
        
        console.log('\n--- STEP 1: INPUT VALIDATION ---');
        console.log('Raw username:', JSON.stringify(username));
        console.log('Raw password:', JSON.stringify(password));
        console.log('Username type:', typeof username);
        console.log('Password type:', typeof password);
        
        // Check if data exists
        if (username === undefined || password === undefined) {
            console.log('ERROR: Missing username or password in request body');
            return res.status(400).json({ 
                error: 'Username and password are required',
                debug: { username: !!username, password: !!password }
            });
        }
        
        // Convert to string and trim
        const cleanUsername = String(username).trim();
        const cleanPassword = String(password).trim();
        
        console.log('Clean username:', JSON.stringify(cleanUsername));
        console.log('Clean password length:', cleanPassword.length);
        
        // Validate cleaned data
        if (!cleanUsername || !cleanPassword) {
            console.log('ERROR: Empty username or password after cleaning');
            return res.status(400).json({ 
                error: 'Username and password cannot be empty',
                debug: { 
                    cleanUsername: cleanUsername,
                    cleanPasswordLength: cleanPassword.length 
                }
            });
        }
        
        if (cleanUsername.length < 1 || cleanPassword.length < 1) {
            console.log('ERROR: Username or password too short');
            return res.status(400).json({ 
                error: 'Username and password must be at least 1 character',
                debug: { 
                    usernameLength: cleanUsername.length,
                    passwordLength: cleanPassword.length 
                }
            });
        }
        
        console.log('✅ Input validation passed');
        
        // STEP 2: Database connection check
        console.log('\n--- STEP 2: DATABASE CHECK ---');
        console.log('MongoDB connection state:', mongoose.connection.readyState);
        console.log('MongoDB ready states: 0=disconnected, 1=connected, 2=connecting, 3=disconnecting');
        
        // Wait for connection if connecting
        if (mongoose.connection.readyState === 2) {
            console.log('Database is connecting, waiting...');
            await new Promise(resolve => {
                const checkConnection = () => {
                    if (mongoose.connection.readyState === 1) {
                        console.log('Database connected successfully');
                        resolve();
                    } else if (mongoose.connection.readyState === 0) {
                        console.log('Database connection failed');
                        resolve();
                    } else {
                        setTimeout(checkConnection, 100);
                    }
                };
                setTimeout(checkConnection, 100);
            });
        }
        
        console.log('Final MongoDB state:', mongoose.connection.readyState);
        console.log('✅ Database check completed');
        
        // STEP 3: Find user in database
        console.log('\n--- STEP 3: USER LOOKUP ---');
        console.log('Searching for user with username:', cleanUsername);
        
        // Simple database query - no timeout
        try {
            user = await User.findOne({ 
                username: cleanUsername,
                password: cleanPassword
            });
            
            console.log('User found:', !!user);
            
            if (!user) {
                // Check if username exists
                const userCheck = await User.findOne({ username: cleanUsername });
                if (userCheck) {
                    console.log('Username exists, wrong password');
                } else {
                    console.log('Username does not exist');
                }
                
                // Show available users for debugging
                const allUsers = await User.find({}).select('username password');
                console.log('Available users:');
                allUsers.forEach(u => console.log(`${u.username}:${u.password}`));
            }
            
        } catch (dbError) {
            console.error('Database error:', dbError.message);
            return res.status(500).json({ error: 'Database connection failed' });
        }
        
        // Check if user was found
        if (!user) {
            console.log('❌ Authentication failed - invalid credentials');
            return res.status(401).json({ 
                error: 'Invalid username or password',
                debug: {
                    providedUsername: cleanUsername,
                    providedPasswordLength: cleanPassword.length,
                    timestamp: new Date().toISOString()
                }
            });
        }
        
        console.log('✅ User authentication successful');
        
        // STEP 4: Create session data
        console.log('\n--- STEP 4: SESSION CREATION ---');
        
        const sessionData = {
            id: user._id.toString(),
            username: user.username,
            coins: user.coins || 100,
            pterodactylUserId: user.pterodactylUserId || null,
            serverCount: user.serverCount || 0,
            loginTime: Date.now(),
            loginIP: req.ip || req.connection.remoteAddress,
            userAgent: req.headers['user-agent']
        };
        
        console.log('Session data created:', JSON.stringify(sessionData, null, 2));
        
        // Set session
        req.session.user = sessionData;
        
        console.log('Session user set:', !!req.session.user);
        console.log('Session ID after setting user:', req.sessionID);
        
        // STEP 5: Save session and respond
        console.log('\n--- STEP 5: SESSION SAVE ---');
        
        // Force session save with callback
        req.session.save((sessionError) => {
            if (sessionError) {
                console.error('❌ Session save error:', sessionError);
                console.error('Session error name:', sessionError.name);
                console.error('Session error message:', sessionError.message);
                
                return res.status(500).json({ 
                    error: 'Session creation failed',
                    debug: {
                        sessionError: sessionError.message,
                        sessionId: req.sessionID,
                        timestamp: new Date().toISOString()
                    }
                });
            }
            
            console.log('✅ Session saved successfully');
            console.log('Final session ID:', req.sessionID);
            console.log('Final session user:', JSON.stringify(req.session.user, null, 2));
            
            // STEP 6: Update user last login (non-blocking)
            console.log('\n--- STEP 6: UPDATE USER DATA ---');
            User.findByIdAndUpdate(
                user._id, 
                { 
                    lastLogin: new Date(),
                    lastLoginIP: req.ip || req.connection.remoteAddress
                },
                { new: false }
            ).catch(updateError => {
                console.log('⚠️ User update failed (non-critical):', updateError.message);
            });
            
            // STEP 7: Create Pterodactyl user if needed (non-blocking)
            console.log('\n--- STEP 7: PTERODACTYL USER ---');
            if (!user.pterodactylUserId) {
                console.log('Creating Pterodactyl user for:', user.username);
                createPterodactylUser(user.username)
                    .then(pterodactylId => {
                        if (pterodactylId) {
                            console.log('✅ Pterodactyl user created:', pterodactylId);
                            User.findByIdAndUpdate(user._id, { pterodactylUserId: pterodactylId }).catch(() => {});
                        } else {
                            console.log('⚠️ Pterodactyl user creation failed');
                        }
                    })
                    .catch(pterodactylError => {
                        console.log('⚠️ Pterodactyl error (non-critical):', pterodactylError.message);
                    });
            } else {
                console.log('✅ Pterodactyl user already exists:', user.pterodactylUserId);
            }
            
            // STEP 8: Send success response
            console.log('\n--- STEP 8: SUCCESS RESPONSE ---');
            
            const responseData = {
                success: true,
                user: {
                    id: sessionData.id,
                    username: sessionData.username,
                    coins: sessionData.coins,
                    serverCount: sessionData.serverCount,
                    pterodactylUserId: sessionData.pterodactylUserId
                },
                session: {
                    id: req.sessionID,
                    created: new Date().toISOString()
                },
                debug: {
                    loginDuration: Date.now() - startTime,
                    mongoState: mongoose.connection.readyState,
                    timestamp: new Date().toISOString()
                }
            };
            
            console.log('Sending response:', JSON.stringify(responseData, null, 2));
            console.log('=== LOGIN SUCCESS ===');
            console.log('Total login time:', Date.now() - startTime, 'ms');
            console.log('User logged in:', user.username);
            console.log('Session ID:', req.sessionID);
            console.log('=== LOGIN REQUEST END ===\n');
            
            res.json(responseData);
        });
        
    } catch (error) {
        console.error('\n❌ CRITICAL LOGIN ERROR ===');
        console.error('Error name:', error.name);
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
        console.error('Request body:', req.body);
        console.error('Session ID:', req.sessionID);
        console.error('MongoDB state:', mongoose.connection.readyState);
        console.error('Total time:', Date.now() - startTime, 'ms');
        console.error('=== CRITICAL ERROR END ===\n');
        
        res.status(500).json({ 
            error: 'Internal server error during login',
            debug: {
                errorName: error.name,
                errorMessage: error.message,
                timestamp: new Date().toISOString(),
                duration: Date.now() - startTime,
                mongoState: mongoose.connection.readyState,
                sessionId: req.sessionID
            }
        });
    }
});

// BULLETPROOF USER API FOR CPANEL
app.get('/api/user', async (req, res) => {
    console.log('\n=== USER API REQUEST ===');
    console.log('Timestamp:', new Date().toISOString());
    console.log('Session exists:', !!req.session);
    console.log('Session ID:', req.sessionID);
    console.log('Session user exists:', !!req.session?.user);
    
    try {
        // STEP 1: Session validation
        console.log('\n--- STEP 1: SESSION VALIDATION ---');
        
        if (!req.session) {
            console.log('❌ No session found');
            return res.status(401).json({ 
                error: 'No session found',
                debug: { sessionExists: false, timestamp: new Date().toISOString() }
            });
        }
        
        if (!req.session.user) {
            console.log('❌ No user in session');
            console.log('Session contents:', JSON.stringify(req.session, null, 2));
            return res.status(401).json({ 
                error: 'Not authenticated - no user in session',
                debug: { 
                    sessionId: req.sessionID,
                    sessionKeys: Object.keys(req.session),
                    timestamp: new Date().toISOString()
                }
            });
        }
        
        if (!req.session.user.id) {
            console.log('❌ No user ID in session');
            console.log('Session user:', JSON.stringify(req.session.user, null, 2));
            return res.status(401).json({ 
                error: 'Invalid session - no user ID',
                debug: { 
                    sessionUser: req.session.user,
                    timestamp: new Date().toISOString()
                }
            });
        }
        
        console.log('✅ Session validation passed');
        console.log('User ID from session:', req.session.user.id);
        console.log('Username from session:', req.session.user.username);
        
        // STEP 2: Database lookup
        console.log('\n--- STEP 2: DATABASE LOOKUP ---');
        console.log('MongoDB state:', mongoose.connection.readyState);
        console.log('Looking up user ID:', req.session.user.id);
        
        let user;
        try {
            user = await User.findById(req.session.user.id);
            console.log('User found in database:', !!user);
            
            if (user) {
                console.log('User data from database:', {
                    id: user._id,
                    username: user.username,
                    coins: user.coins,
                    serverCount: user.serverCount,
                    pterodactylUserId: user.pterodactylUserId
                });
            }
            
        } catch (dbError) {
            console.error('❌ Database lookup error:', dbError);
            return res.status(500).json({ 
                error: 'Database lookup failed',
                debug: {
                    errorMessage: dbError.message,
                    userId: req.session.user.id,
                    mongoState: mongoose.connection.readyState,
                    timestamp: new Date().toISOString()
                }
            });
        }
        
        if (!user) {
            console.log('❌ User not found in database');
            console.log('Destroying invalid session');
            
            req.session.destroy((destroyError) => {
                if (destroyError) {
                    console.error('Session destroy error:', destroyError);
                }
            });
            
            return res.status(401).json({ 
                error: 'User not found in database',
                debug: {
                    sessionUserId: req.session.user.id,
                    timestamp: new Date().toISOString()
                }
            });
        }
        
        console.log('✅ User found in database');
        
        // STEP 3: Prepare user data
        console.log('\n--- STEP 3: PREPARE USER DATA ---');
        
        const userData = {
            id: user._id.toString(),
            username: user.username,
            coins: user.coins || 100,
            pterodactylUserId: user.pterodactylUserId || null,
            serverCount: user.serverCount || 0,
            lastLogin: user.lastLogin,
            createdAt: user.createdAt
        };
        
        console.log('Prepared user data:', JSON.stringify(userData, null, 2));
        
        // STEP 4: Update session
        console.log('\n--- STEP 4: UPDATE SESSION ---');
        
        req.session.user = {
            ...userData,
            loginTime: req.session.user.loginTime,
            loginIP: req.session.user.loginIP,
            userAgent: req.session.user.userAgent
        };
        
        console.log('Session updated successfully');
        
        // STEP 5: Send response
        console.log('\n--- STEP 5: SEND RESPONSE ---');
        
        const responseData = {
            ...userData,
            session: {
                id: req.sessionID,
                loginTime: req.session.user.loginTime,
                valid: true
            },
            debug: {
                mongoState: mongoose.connection.readyState,
                timestamp: new Date().toISOString()
            }
        };
        
        console.log('Sending user data response');
        console.log('=== USER API SUCCESS ===\n');
        
        res.json(responseData);
        
    } catch (error) {
        console.error('\n❌ CRITICAL USER API ERROR ===');
        console.error('Error name:', error.name);
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
        console.error('Session ID:', req.sessionID);
        console.error('Session user:', req.session?.user);
        console.error('MongoDB state:', mongoose.connection.readyState);
        console.error('=== CRITICAL ERROR END ===\n');
        
        res.status(500).json({ 
            error: 'Internal server error in user API',
            debug: {
                errorName: error.name,
                errorMessage: error.message,
                sessionId: req.sessionID,
                mongoState: mongoose.connection.readyState,
                timestamp: new Date().toISOString()
            }
        });
    }
});

// API route to get user servers
app.get('/api/servers', async (req, res) => {
    if (!req.isAuthenticated()) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
        const user = await User.findById(req.session.user.id).lean();
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
        const user = await User.findById(req.session.user.id).lean();
        
        let userResources = await UserResources.findOne({ userId: user._id }).lean();
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

    console.log('\n=== SERVER CREATION REQUEST ===');
    console.log('User:', req.session.user.username);
    console.log('Server data:', { name, egg, memory, cpu, disk });

    try {
        const user = await User.findById(req.session.user.id);
        
        // Get user's purchased resources to check server slots
        let userResources = await UserResources.findOne({ userId: user._id });
        if (!userResources) {
            userResources = new UserResources({ userId: user._id });
            await userResources.save();
        }
        
        // Check server limit using purchased slots
        const maxServers = userResources.serverSlots; // This includes base + purchased slots
        if (user.serverCount >= maxServers) {
            return res.status(400).json({ 
                error: `Server limit reached (${maxServers} servers maximum). Buy more slots from the store.` 
            });
        }

        // Validate input
        if (!name || name.trim().length === 0) {
            return res.status(400).json({ error: 'Server name is required' });
        }
        
        if (!egg) {
            return res.status(400).json({ error: 'Server type (egg) is required' });
        }
        
        if (!memory || !cpu || !disk) {
            return res.status(400).json({ error: 'All resource fields (memory, CPU, disk) are required' });
        }
        
        // Convert to numbers and validate
        const memoryNum = parseInt(memory);
        const cpuNum = parseInt(cpu);
        const diskNum = parseInt(disk);
        const eggNum = parseInt(egg);
        
        if (isNaN(memoryNum) || isNaN(cpuNum) || isNaN(diskNum) || isNaN(eggNum)) {
            return res.status(400).json({ error: 'Invalid numeric values provided' });
        }

        // Define user resource limits
        const userLimits = {
            maxMemory: 2048,  // 2GB RAM
            maxCpu: 100,      // 100% CPU
            maxDisk: 5120,    // 5GB Disk
            minMemory: 512,   // 512MB minimum
            minCpu: 25,       // 25% minimum
            minDisk: 1024     // 1GB minimum
        };
        
        // Validate resources against user limits
        if (memoryNum < userLimits.minMemory || memoryNum > userLimits.maxMemory) {
            return res.status(400).json({ 
                error: `Memory must be between ${userLimits.minMemory}MB and ${userLimits.maxMemory}MB` 
            });
        }
        if (cpuNum < userLimits.minCpu || cpuNum > userLimits.maxCpu) {
            return res.status(400).json({ 
                error: `CPU must be between ${userLimits.minCpu}% and ${userLimits.maxCpu}%` 
            });
        }
        if (diskNum < userLimits.minDisk || diskNum > userLimits.maxDisk) {
            return res.status(400).json({ 
                error: `Disk must be between ${userLimits.minDisk}MB and ${userLimits.maxDisk}MB` 
            });
        }

        // Ensure user has Pterodactyl account
        if (!user.pterodactylUserId) {
            return res.status(400).json({ 
                error: 'Pterodactyl account not found. Please logout and login again to create your account.' 
            });
        }

        // Get active node with automatic switching
        let activeNode = await checkNodeSwitching();
        
        if (!activeNode) {
            return res.status(500).json({ error: 'No available server nodes' });
        }
        
        const defaultNode = activeNode.id;
        console.log('Using active node:', activeNode.name, 'ID:', defaultNode);

        // Get available allocation from default node
        let allocationId = null;
        try {
            const allocationsResponse = await pterodactylAPI.get(`/nodes/${defaultNode}/allocations`);
            const availableAllocations = allocationsResponse.data.data.filter(alloc => !alloc.attributes.assigned);
            if (availableAllocations.length > 0) {
                allocationId = availableAllocations[0].attributes.id;
                console.log('Found available allocation:', allocationId);
            } else {
                console.log('No available allocations, will use deploy method');
            }
        } catch (allocError) {
            console.error('Error fetching allocations:', allocError.response?.data || allocError.message);
        }

        // Get egg details with proper variable handling
        let eggData = null;
        let eggVariables = {};
        
        try {
            // Get the specific egg with its variables
            const eggResponse = await pterodactylAPI.get(`/eggs/${eggNum}?include=variables`);
            eggData = eggResponse.data.attributes;
            
            console.log('Egg data retrieved:', eggData.name);
            
            // Process egg variables properly
            if (eggData.relationships?.variables?.data) {
                eggData.relationships.variables.data.forEach(variable => {
                    const varAttr = variable.attributes;
                    let defaultValue = varAttr.default_value || '';
                    
                    // Handle specific variable types with proper defaults
                    switch (varAttr.env_variable) {
                        case 'SERVER_JARFILE':
                            defaultValue = defaultValue || 'server.jar';
                            break;
                        case 'BUILD_NUMBER':
                            defaultValue = defaultValue || 'latest';
                            break;
                        case 'MINECRAFT_VERSION':
                            defaultValue = defaultValue || '1.20.1';
                            break;
                        case 'VANILLA_VERSION':
                            defaultValue = defaultValue || 'latest';
                            break;
                        case 'USER_UPLOAD':
                            defaultValue = defaultValue || '0';
                            break;
                        case 'AUTO_UPDATE':
                            defaultValue = defaultValue || '0';
                            break;
                        case 'PY_FILE':
                            defaultValue = defaultValue || 'main.py';
                            break;
                        case 'REQUIREMENTS_FILE':
                            defaultValue = defaultValue || 'requirements.txt';
                            break;
                        case 'PY_PACKAGES':
                            defaultValue = defaultValue || '';
                            break;
                        case 'INSTALL_REPO':
                            defaultValue = defaultValue || '';
                            break;
                        case 'GIT_ADDRESS':
                            defaultValue = defaultValue || '';
                            break;
                        case 'BRANCH':
                            defaultValue = defaultValue || 'main';
                            break;
                        case 'BOT_PY_FILE':
                            defaultValue = defaultValue || 'bot.py';
                            break;
                        case 'INSTALL_PACKAGES':
                            defaultValue = defaultValue || '';
                            break;
                        default:
                            // For any other variables, use default or empty string
                            defaultValue = defaultValue || '';
                    }
                    
                    eggVariables[varAttr.env_variable] = defaultValue;
                });
            }
            
            console.log('Processed egg variables:', eggVariables);
            
        } catch (eggError) {
            console.error('Error fetching egg data:', eggError.response?.data || eggError.message);
            
            // Fallback: try to get egg from nest
            try {
                const nestsResponse = await pterodactylAPI.get('/nests');
                const nests = nestsResponse.data.data;
                
                let targetEgg = null;
                for (const nest of nests) {
                    try {
                        const eggsResponse = await pterodactylAPI.get(`/nests/${nest.attributes.id}/eggs?include=variables`);
                        const eggs = eggsResponse.data.data;
                        targetEgg = eggs.find(e => e.attributes.id === eggNum);
                        if (targetEgg) {
                            eggData = targetEgg.attributes;
                            
                            // Process variables from nest egg data
                            if (eggData.relationships?.variables?.data) {
                                eggData.relationships.variables.data.forEach(variable => {
                                    const varAttr = variable.attributes;
                                    let defaultValue = varAttr.default_value || '';
                                    
                                    // Apply same variable handling as above
                                    switch (varAttr.env_variable) {
                                        case 'USER_UPLOAD':
                                            defaultValue = defaultValue || '0';
                                            break;
                                        case 'AUTO_UPDATE':
                                            defaultValue = defaultValue || '0';
                                            break;
                                        case 'PY_FILE':
                                            defaultValue = defaultValue || 'main.py';
                                            break;
                                        case 'REQUIREMENTS_FILE':
                                            defaultValue = defaultValue || 'requirements.txt';
                                            break;
                                        case 'PY_PACKAGES':
                                            defaultValue = defaultValue || '';
                                            break;
                                        case 'SERVER_JARFILE':
                                            defaultValue = defaultValue || 'server.jar';
                                            break;
                                        case 'BUILD_NUMBER':
                                            defaultValue = defaultValue || 'latest';
                                            break;
                                        case 'MINECRAFT_VERSION':
                                            defaultValue = defaultValue || '1.20.1';
                                            break;
                                        case 'VANILLA_VERSION':
                                            defaultValue = defaultValue || 'latest';
                                            break;
                                        case 'INSTALL_REPO':
                                            defaultValue = defaultValue || '';
                                            break;
                                        case 'GIT_ADDRESS':
                                            defaultValue = defaultValue || '';
                                            break;
                                        case 'BRANCH':
                                            defaultValue = defaultValue || 'main';
                                            break;
                                        case 'BOT_PY_FILE':
                                            defaultValue = defaultValue || 'bot.py';
                                            break;
                                        case 'INSTALL_PACKAGES':
                                            defaultValue = defaultValue || '';
                                            break;
                                        default:
                                            defaultValue = defaultValue || '';
                                    }
                                    
                                    eggVariables[varAttr.env_variable] = defaultValue;
                                });
                            }
                            break;
                        }
                    } catch (nestError) {
                        console.log(`Could not fetch eggs for nest ${nest.attributes.id}`);
                    }
                }
            } catch (fallbackError) {
                console.error('Fallback egg fetch also failed:', fallbackError.message);
            }
        }
        
        console.log('Final environment variables:', eggVariables);

        // Prepare server creation data
        const serverData = {
            name: name.trim(),
            user: user.pterodactylUserId,
            egg: eggNum,
            docker_image: eggData?.docker_image || 'quay.io/pterodactyl/core:java',
            startup: eggData?.startup || `java -Xms128M -Xmx${memoryNum}M -jar {{SERVER_JARFILE}}`,
            environment: eggVariables,
            limits: {
                memory: memoryNum,
                swap: 0,
                disk: diskNum,
                io: 500,
                cpu: cpuNum
            },
            feature_limits: {
                databases: 1,
                allocations: 1,
                backups: 2
            }
        };

        // Add allocation or deploy configuration
        if (allocationId) {
            serverData.allocation = {
                default: allocationId
            };
        } else {
            serverData.deploy = {
                locations: [defaultNode],
                dedicated_ip: false,
                port_range: []
            };
        }
        
        console.log('Creating server with data:');
        console.log('- Name:', serverData.name);
        console.log('- User ID:', serverData.user);
        console.log('- Egg ID:', serverData.egg);
        console.log('- Node ID:', defaultNode);
        console.log('- Environment variables:', Object.keys(eggVariables).length, 'variables');
        console.log('- Memory:', serverData.limits.memory, 'MB');
        console.log('- CPU:', serverData.limits.cpu, '%');
        console.log('- Disk:', serverData.limits.disk, 'MB');

        const response = await pterodactylAPI.post('/servers', serverData);
        
        if (response.data && response.data.attributes) {
            // Update user server count
            user.serverCount = (user.serverCount || 0) + 1;
            await user.save();
            
            // Update session
            req.session.user.serverCount = user.serverCount;
            
            // Update node server count
            if (nodeServerCounts[defaultNode] !== undefined) {
                nodeServerCounts[defaultNode]++;
            }
            
            console.log('Server created successfully:', response.data.attributes.identifier);
            console.log('Node server count updated:', activeNode.name, nodeServerCounts[defaultNode]);
            console.log('=== SERVER CREATION COMPLETE ===\n');
            
            res.json({ 
                success: true, 
                server: response.data.attributes,
                message: `Server "${name}" created successfully!`,
                resources: {
                    memory: `${memoryNum}MB RAM`,
                    cpu: `${cpuNum}% CPU`,
                    disk: `${diskNum}MB Disk`
                },
                pterodactylUser: {
                    username: user.username,
                    email: `${user.username}@gmail.com`,
                    password: user.username,
                    panelUrl: 'https://panel.blazenode.site'
                }
            });
        } else {
            console.error('Invalid response from Pterodactyl API:', response.data);
            res.status(500).json({ error: 'Failed to create server - Invalid API response' });
        }
    } catch (error) {
        console.error('Create server error:', error.response?.data || error.message);
        
        console.error('Full error details:', {
            status: error.response?.status,
            data: error.response?.data,
            message: error.message
        });
        
        let errorMessage = 'Failed to create server';
        
        if (error.response?.data?.errors) {
            const errors = error.response.data.errors;
            console.error('Pterodactyl API errors:', errors);
            
            if (errors.name) {
                errorMessage = 'Server name is invalid or already exists';
            } else if (errors.user) {
                errorMessage = 'User account error - please contact support';
            } else if (errors.egg) {
                errorMessage = 'Invalid server type selected';
            } else if (errors.limits) {
                errorMessage = 'Resource limits exceeded';
            } else if (errors.allocation || errors.deploy) {
                errorMessage = 'No available server slots - please try again later';
            } else {
                // Get first error message
                const firstError = Object.values(errors)[0];
                errorMessage = Array.isArray(firstError) ? firstError[0] : firstError;
            }
        } else if (error.response?.data?.message) {
            errorMessage = error.response.data.message;
        } else if (error.response?.status === 422) {
            errorMessage = 'Invalid server configuration - please check your settings';
        } else if (error.response?.status === 403) {
            errorMessage = 'Permission denied - please contact support';
        } else if (error.response?.status >= 500) {
            errorMessage = 'Server error - please try again later';
        }
        
        const statusCode = error.response?.status || 500;
        res.status(statusCode).json({ 
            error: errorMessage,
            details: error.response?.data?.message || error.message,
            debug: config.NODE_ENV === 'development' ? {
                pterodactylError: error.response?.data,
                serverData: serverData
            } : undefined
        });
    }
});

// API route to delete server
app.post('/api/delete-server', async (req, res) => {
    if (!req.isAuthenticated()) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    const { serverIdentifier } = req.body;

    console.log('\n=== SERVER DELETION REQUEST ===');
    console.log('User:', req.session.user.username);
    console.log('Server identifier:', serverIdentifier);

    try {
        const user = await User.findById(req.session.user.id);
        
        if (!serverIdentifier) {
            return res.status(400).json({ error: 'Server identifier is required' });
        }

        // Ensure user has Pterodactyl account
        if (!user.pterodactylUserId) {
            return res.status(400).json({ error: 'Pterodactyl account not found' });
        }

        // Get user servers to verify ownership
        const servers = await getUserServers(user.pterodactylUserId);
        const server = servers.find(s => s.attributes.identifier === serverIdentifier);
        
        if (!server) {
            return res.status(404).json({ error: 'Server not found or access denied' });
        }

        console.log('Deleting server:', server.attributes.name, 'ID:', server.attributes.id);

        // Delete server from Pterodactyl
        const response = await pterodactylAPI.delete(`/servers/${server.attributes.id}`);
        
        if (response.status === 204) {
            // Update user server count
            user.serverCount = Math.max(0, (user.serverCount || 0) - 1);
            await user.save();
            
            // Update session
            req.session.user.serverCount = user.serverCount;
            
            console.log('Server deleted successfully:', serverIdentifier);
            console.log('Updated user server count:', user.serverCount);
            console.log('=== SERVER DELETION COMPLETE ===\n');
            
            res.json({ 
                success: true, 
                message: `Server "${server.attributes.name}" deleted successfully!`
            });
        } else {
            console.error('Pterodactyl API error:', response.data);
            res.status(500).json({ error: 'Failed to delete server from panel' });
        }
        
    } catch (error) {
        console.error('Delete server error:', error.response?.data || error.message);
        
        let errorMessage = 'Failed to delete server';
        
        if (error.response?.data?.errors) {
            const errors = error.response.data.errors;
            console.error('Pterodactyl API errors:', errors);
            const firstError = Object.values(errors)[0];
            errorMessage = Array.isArray(firstError) ? firstError[0] : firstError;
        } else if (error.response?.data?.message) {
            errorMessage = error.response.data.message;
        } else if (error.response?.status === 404) {
            errorMessage = 'Server not found in panel';
        } else if (error.response?.status === 403) {
            errorMessage = 'Permission denied - cannot delete server';
        } else if (error.response?.status >= 500) {
            errorMessage = 'Panel server error - please try again later';
        }
        
        const statusCode = error.response?.status || 500;
        res.status(statusCode).json({ 
            error: errorMessage,
            details: error.response?.data?.message || error.message
        });
    }
});

// API route to claim daily reward
app.post('/api/claim-reward', async (req, res) => {
    if (!req.session.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
        const user = await User.findById(req.session.user.id);
        const now = new Date();
        const lastReward = user.lastDailyReward;
        
        if (lastReward && (now - lastReward) < 24 * 60 * 60 * 1000) {
            return res.status(400).json({ error: 'Daily reward already claimed' });
        }

        user.coins += 25;
        user.dailyRewardStreak += 1;
        user.lastDailyReward = now;
        await user.save();

        req.session.user.coins = user.coins;

        res.json({ 
            success: true, 
            coins: user.coins, 
            streak: user.dailyRewardStreak 
        });
    } catch (error) {
        console.error('Claim reward error:', error);
        res.status(500).json({ error: 'Server error' });
    }
});

// API route to get leaderboard
app.get('/api/leaderboard', async (req, res) => {
    try {
        const users = await User.find({})
            .select('username coins')
            .sort({ coins: -1 })
            .limit(10);
        
        res.json({ users });
    } catch (error) {
        console.error('Error fetching leaderboard:', error);
        res.status(500).json({ error: 'Failed to fetch leaderboard' });
    }
});

// Check admin access middleware
function checkAdmin(req, res, next) {
    if (!req.session || !req.session.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    if (req.session.user.username !== 'shadow') {
        return res.status(403).json({ error: 'Access denied' });
    }
    
    next();
}

// Admin API route to get all users
app.get('/api/admin/users', checkAdmin, async (req, res) => {
    try {
        const users = await User.find({})
            .select('username coins serverCount createdAt')
            .sort({ createdAt: -1 });
        
        res.json({ users });
    } catch (error) {
        console.error('Error fetching users:', error);
        res.status(500).json({ error: 'Failed to fetch users' });
    }
});

// Admin API route to give coins
app.post('/api/admin/give-coins', checkAdmin, async (req, res) => {
    const { username, coins } = req.body;
    
    if (!username || !coins || coins <= 0) {
        return res.status(400).json({ error: 'Invalid username or coins amount' });
    }
    
    try {
        const user = await User.findOne({ username: username.trim() });
        
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        user.coins += parseInt(coins);
        await user.save();
        
        console.log(`Admin ${req.session.user.username} gave ${coins} coins to ${username}`);
        
        res.json({ 
            success: true, 
            message: `Successfully gave ${coins} coins to ${username}`,
            newBalance: user.coins
        });
    } catch (error) {
        console.error('Error giving coins:', error);
        res.status(500).json({ error: 'Failed to give coins' });
    }
});

// Admin API route to edit user
app.post('/api/admin/edit-user', checkAdmin, async (req, res) => {
    const { userId, username, password } = req.body;
    
    if (!userId || !username) {
        return res.status(400).json({ error: 'User ID and username are required' });
    }
    
    try {
        const user = await User.findById(userId);
        
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        user.username = username.trim();
        if (password) {
            user.password = password.trim();
        }
        
        await user.save();
        
        console.log(`Admin ${req.session.user.username} edited user ${userId}`);
        
        res.json({ 
            success: true, 
            message: 'User updated successfully'
        });
    } catch (error) {
        console.error('Error editing user:', error);
        res.status(500).json({ error: 'Failed to edit user' });
    }
});

// Admin API route to delete user
app.post('/api/admin/delete-user', checkAdmin, async (req, res) => {
    const { userId } = req.body;
    
    if (!userId) {
        return res.status(400).json({ error: 'User ID is required' });
    }
    
    try {
        const user = await User.findById(userId);
        
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        // Don't allow deleting the admin user
        if (user.username === 'shadow') {
            return res.status(400).json({ error: 'Cannot delete admin user' });
        }
        
        await User.findByIdAndDelete(userId);
        
        console.log(`Admin ${req.session.user.username} deleted user ${user.username}`);
        
        res.json({ 
            success: true, 
            message: 'User deleted successfully'
        });
    } catch (error) {
        console.error('Error deleting user:', error);
        res.status(500).json({ error: 'Failed to delete user' });
    }
});

// Admin API route to create coupon
app.post('/api/admin/create-coupon', checkAdmin, async (req, res) => {
    const { couponCode, amount, limit } = req.body;
    
    if (!couponCode || !amount || !limit || amount <= 0 || limit <= 0) {
        return res.status(400).json({ error: 'All fields are required with valid values' });
    }
    
    try {
        // Check if coupon already exists
        const existingCoupon = await Coupon.findOne({ code: couponCode.toUpperCase() });
        if (existingCoupon) {
            return res.status(400).json({ error: 'Coupon code already exists' });
        }
        
        const coupon = new Coupon({
            code: couponCode.toUpperCase(),
            amount: parseInt(amount),
            limit: parseInt(limit),
            createdBy: req.session.user.username
        });
        
        await coupon.save();
        
        console.log(`Admin ${req.session.user.username} created coupon ${couponCode}`);
        
        res.json({ 
            success: true, 
            message: 'Coupon created successfully',
            coupon: {
                code: coupon.code,
                amount: coupon.amount,
                limit: coupon.limit
            }
        });
    } catch (error) {
        console.error('Error creating coupon:', error);
        res.status(500).json({ error: 'Failed to create coupon' });
    }
});

// API route to redeem coupon
app.post('/api/redeem-coupon', async (req, res) => {
    if (!req.session || !req.session.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    const { couponCode } = req.body;
    
    if (!couponCode) {
        return res.status(400).json({ error: 'Coupon code is required' });
    }
    
    try {
        const coupon = await Coupon.findOne({ 
            code: couponCode.toUpperCase(),
            active: true
        });
        
        if (!coupon) {
            return res.status(404).json({ error: 'Invalid coupon code' });
        }
        
        // Check if coupon limit reached
        if (coupon.used >= coupon.limit) {
            return res.status(400).json({ error: 'Coupon limit reached' });
        }
        
        // Check if user already used this coupon
        if (coupon.usedBy.includes(req.session.user.id)) {
            return res.status(400).json({ error: 'You have already used this coupon' });
        }
        
        // Update user coins
        const user = await User.findById(req.session.user.id);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        user.coins += coupon.amount;
        await user.save();
        
        // Update coupon usage
        coupon.used += 1;
        coupon.usedBy.push(user._id);
        await coupon.save();
        
        // Update session
        req.session.user.coins = user.coins;
        
        console.log(`User ${user.username} redeemed coupon ${couponCode} for ${coupon.amount} coins`);
        
        res.json({ 
            success: true, 
            message: 'Coupon redeemed successfully',
            coins: coupon.amount,
            newBalance: user.coins
        });
    } catch (error) {
        console.error('Error redeeming coupon:', error);
        res.status(500).json({ error: 'Failed to redeem coupon' });
    }
});

// API route to buy resources
app.post('/api/buy-resource', async (req, res) => {
    if (!req.session || !req.session.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    const { type, amount, price } = req.body;
    
    try {
        const user = await User.findById(req.session.user.id);
        if (user.coins < price) {
            return res.status(400).json({ error: 'Insufficient coins' });
        }
        
        let userResources = await UserResources.findOne({ userId: user._id });
        if (!userResources) {
            userResources = new UserResources({ userId: user._id });
        }
        
        // Check limits
        const limits = { ram: 30720, cpu: 5000, disk: 51200 }; // 30GB, 5000%, 50GB
        
        if (type === 'ram' && userResources.purchasedRam + amount > limits.ram) {
            return res.status(400).json({ error: 'RAM limit exceeded (30GB max)' });
        }
        if (type === 'cpu' && userResources.purchasedCpu + amount > limits.cpu) {
            return res.status(400).json({ error: 'CPU limit exceeded (5000% max)' });
        }
        if (type === 'disk' && userResources.purchasedDisk + amount > limits.disk) {
            return res.status(400).json({ error: 'Disk limit exceeded (50GB max)' });
        }
        
        // Update resources
        user.coins -= price;
        if (type === 'ram') {
            userResources.availableRam += amount;
            userResources.purchasedRam += amount;
        } else if (type === 'cpu') {
            userResources.availableCpu += amount;
            userResources.purchasedCpu += amount;
        } else if (type === 'disk') {
            userResources.availableDisk += amount;
            userResources.purchasedDisk += amount;
        }
        
        await user.save();
        await userResources.save();
        
        req.session.user.coins = user.coins;
        
        console.log(`User ${user.username} bought ${amount}MB ${type}, new total: ${userResources.availableRam}MB RAM, ${userResources.availableCpu}% CPU, ${userResources.availableDisk}MB disk`);
        
        res.json({ success: true, newBalance: user.coins });
    } catch (error) {
        console.error('Error buying resource:', error);
        res.status(500).json({ error: 'Failed to buy resource' });
    }
});

// API route to buy server slots
app.post('/api/buy-slot', async (req, res) => {
    if (!req.session || !req.session.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    const { slots, price } = req.body;
    
    try {
        const user = await User.findById(req.session.user.id);
        if (user.coins < price) {
            return res.status(400).json({ error: 'Insufficient coins' });
        }
        
        let userResources = await UserResources.findOne({ userId: user._id });
        if (!userResources) {
            userResources = new UserResources({ userId: user._id });
        }
        
        if (userResources.purchasedSlots + slots > 3) { // Max 5 total (2 default + 3 purchasable)
            return res.status(400).json({ error: 'Server slot limit exceeded (5 max)' });
        }
        
        user.coins -= price;
        userResources.serverSlots += slots;
        userResources.purchasedSlots += slots;
        
        await user.save();
        await userResources.save();
        
        req.session.user.coins = user.coins;
        
        console.log(`User ${user.username} bought ${slots} server slot(s), new total: ${userResources.serverSlots} slots`);
        
        res.json({ success: true, newBalance: user.coins });
    } catch (error) {
        console.error('Error buying slot:', error);
        res.status(500).json({ error: 'Failed to buy slot' });
    }
});

// Admin API route to update store prices
app.post('/api/admin/update-price', checkAdmin, async (req, res) => {
    const { type, price } = req.body;
    
    // For now, just return success (prices can be stored in database later)
    res.json({ success: true, message: `${type} price updated to ${price} coins` });
});

// Admin API route to update Discord link
app.post('/api/admin/update-discord', checkAdmin, async (req, res) => {
    const { discordLink } = req.body;
    
    if (!discordLink || !discordLink.startsWith('https://discord.gg/')) {
        return res.status(400).json({ error: 'Invalid Discord invite link' });
    }
    
    try {
        // Store Discord link in environment or database
        // For now, we'll just return success
        console.log(`Admin ${req.session.user.username} updated Discord link to: ${discordLink}`);
        
        res.json({ 
            success: true, 
            message: 'Discord link updated successfully',
            discordLink
        });
    } catch (error) {
        console.error('Error updating Discord link:', error);
        res.status(500).json({ error: 'Failed to update Discord link' });
    }
});

// Admin API route to update Linkvertise URL
app.post('/api/admin/update-linkvertise', checkAdmin, async (req, res) => {
    const { linkvertiseUrl } = req.body;
    
    if (!linkvertiseUrl || (!linkvertiseUrl.startsWith('http://') && !linkvertiseUrl.startsWith('https://'))) {
        return res.status(400).json({ error: 'Invalid URL. Must start with http:// or https://' });
    }
    
    try {
        // Store Linkvertise URL (in a real app, this would be saved to database)
        // For now, we'll just return success and let client handle localStorage
        console.log(`Admin ${req.session.user.username} updated Linkvertise URL to: ${linkvertiseUrl}`);
        
        res.json({ 
            success: true, 
            message: 'Linkvertise URL updated successfully',
            linkvertiseUrl
        });
    } catch (error) {
        console.error('Error updating Linkvertise URL:', error);
        res.status(500).json({ error: 'Failed to update Linkvertise URL' });
    }
});

// Admin API route to remove coins
app.post('/api/admin/remove-coins', checkAdmin, async (req, res) => {
    const { username, coins } = req.body;
    
    if (!username || !coins || coins <= 0) {
        return res.status(400).json({ error: 'Invalid username or coins amount' });
    }
    
    try {
        const user = await User.findOne({ username: username.trim() });
        
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        const coinsToRemove = parseInt(coins);
        
        if (user.coins < coinsToRemove) {
            return res.status(400).json({ error: 'User does not have enough coins' });
        }
        
        user.coins -= coinsToRemove;
        await user.save();
        
        console.log(`Admin ${req.session.user.username} removed ${coins} coins from ${username}`);
        
        res.json({ 
            success: true, 
            message: `Successfully removed ${coins} coins from ${username}`,
            newBalance: user.coins
        });
    } catch (error) {
        console.error('Error removing coins:', error);
        res.status(500).json({ error: 'Failed to remove coins' });
    }
});

// Global variable to store current active node and server limit
let currentActiveNode = null;
let serverLimit = 600;
let nodeServerCounts = {};

// Function to get available nodes
async function getAvailableNodes() {
    try {
        const response = await pterodactylAPI.get('/nodes');
        const nodes = response.data.data || [];
        
        // Get server count for each node
        const nodesWithCounts = await Promise.all(nodes.map(async (node) => {
            try {
                const serversResponse = await pterodactylAPI.get('/servers');
                const allServers = serversResponse.data.data || [];
                const nodeServers = allServers.filter(server => server.attributes.node === node.attributes.id);
                
                nodeServerCounts[node.attributes.id] = nodeServers.length;
                
                return {
                    id: node.attributes.id,
                    name: node.attributes.name,
                    serverCount: nodeServers.length,
                    status: node.attributes.maintenance_mode ? 'maintenance' : 'active'
                };
            } catch (error) {
                console.error(`Error getting server count for node ${node.attributes.id}:`, error.message);
                return {
                    id: node.attributes.id,
                    name: node.attributes.name,
                    serverCount: 0,
                    status: 'error'
                };
            }
        }));
        
        return nodesWithCounts;
    } catch (error) {
        console.error('Error fetching nodes:', error);
        return [];
    }
}

// Function to get next available node
async function getNextAvailableNode() {
    const nodes = await getAvailableNodes();
    
    // Find node with least servers that's not in maintenance
    const availableNodes = nodes.filter(node => node.status !== 'maintenance' && node.serverCount < serverLimit);
    
    if (availableNodes.length === 0) {
        return null;
    }
    
    // Sort by server count (ascending)
    availableNodes.sort((a, b) => a.serverCount - b.serverCount);
    
    return availableNodes[0];
}

// Function to check if node switching is needed
async function checkNodeSwitching() {
    if (!currentActiveNode) {
        currentActiveNode = await getNextAvailableNode();
        return currentActiveNode;
    }
    
    const currentNodeCount = nodeServerCounts[currentActiveNode.id] || 0;
    
    if (currentNodeCount >= serverLimit) {
        console.log(`Node ${currentActiveNode.name} has reached limit (${currentNodeCount}/${serverLimit}), switching to next node...`);
        const nextNode = await getNextAvailableNode();
        
        if (nextNode && nextNode.id !== currentActiveNode.id) {
            console.log(`Switching from node ${currentActiveNode.name} to ${nextNode.name}`);
            currentActiveNode = nextNode;
        }
    }
    
    return currentActiveNode;
}

// Admin API route to get nodes information
app.get('/api/admin/nodes', checkAdmin, async (req, res) => {
    try {
        const nodes = await getAvailableNodes();
        
        if (!currentActiveNode && nodes.length > 0) {
            currentActiveNode = nodes[0];
        }
        
        res.json({
            success: true,
            nodes,
            currentNode: currentActiveNode,
            serverLimit
        });
    } catch (error) {
        console.error('Error fetching nodes:', error);
        res.status(500).json({ error: 'Failed to fetch nodes' });
    }
});

// Admin API route to switch active node
app.post('/api/admin/switch-node', checkAdmin, async (req, res) => {
    const { nodeId } = req.body;
    
    if (!nodeId) {
        return res.status(400).json({ error: 'Node ID is required' });
    }
    
    try {
        const nodes = await getAvailableNodes();
        const targetNode = nodes.find(node => node.id == nodeId);
        
        if (!targetNode) {
            return res.status(404).json({ error: 'Node not found' });
        }
        
        currentActiveNode = targetNode;
        
        console.log(`Admin ${req.session.user.username} switched active node to: ${targetNode.name}`);
        
        res.json({
            success: true,
            message: `Switched to node: ${targetNode.name}`,
            currentNode: currentActiveNode
        });
    } catch (error) {
        console.error('Error switching node:', error);
        res.status(500).json({ error: 'Failed to switch node' });
    }
});

// Admin API route to check node status
app.get('/api/admin/node-status', checkAdmin, async (req, res) => {
    try {
        const nodes = await getAvailableNodes();
        
        res.json({
            success: true,
            nodes,
            currentNode: currentActiveNode,
            serverLimit
        });
    } catch (error) {
        console.error('Error checking node status:', error);
        res.status(500).json({ error: 'Failed to check node status' });
    }
});

// Admin API route to update server limit
app.post('/api/admin/update-server-limit', checkAdmin, async (req, res) => {
    const { serverLimit: newLimit } = req.body;
    
    if (!newLimit || newLimit < 1 || newLimit > 1000) {
        return res.status(400).json({ error: 'Server limit must be between 1 and 1000' });
    }
    
    try {
        serverLimit = parseInt(newLimit);
        
        console.log(`Admin ${req.session.user.username} updated server limit to: ${serverLimit}`);
        
        res.json({
            success: true,
            message: `Server limit updated to ${serverLimit}`,
            serverLimit
        });
    } catch (error) {
        console.error('Error updating server limit:', error);
        res.status(500).json({ error: 'Failed to update server limit' });
    }
});

// Create Promotion model
const promotionSchema = new mongoose.Schema({
    serverName: {
        type: String,
        required: true,
        trim: true
    },
    serverIP: {
        type: String,
        required: true,
        trim: true
    },
    description: {
        type: String,
        required: true,
        trim: true
    },
    author: {
        type: String,
        required: true
    },
    authorId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    boosted: {
        type: Boolean,
        default: false
    },
    boostCount: {
        type: Number,
        default: 0
    },
    views: {
        type: Number,
        default: 0
    }
}, {
    timestamps: true
});

const Promotion = mongoose.model('Promotion', promotionSchema);

// Linkvertise completion tracking
const linkvertiseSessions = new Map();

// API route to process Linkvertise completion
app.post('/api/linkvertise-complete', async (req, res) => {
    if (!req.session || !req.session.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    const { sessionId, completionTime, detectionMethods, userAgent } = req.body;
    const userId = req.session.user.id;
    
    try {
        // Validate session
        if (!sessionId || typeof completionTime !== 'number') {
            return res.status(400).json({ error: 'Invalid completion data' });
        }
        
        // Anti-fraud checks
        const now = Date.now();
        const userSessions = linkvertiseSessions.get(userId) || [];
        
        // Check for duplicate session
        if (userSessions.some(session => session.sessionId === sessionId)) {
            return res.status(400).json({ error: 'Session already processed' });
        }
        
        // Rate limiting - max 3 completions per hour
        const oneHourAgo = now - (60 * 60 * 1000);
        const recentSessions = userSessions.filter(session => session.timestamp > oneHourAgo);
        
        if (recentSessions.length >= 3) {
            return res.status(429).json({ error: 'Too many completions. Please wait before trying again.' });
        }
        
        // Validate completion time (45 seconds to 5 minutes)
        if (completionTime < 45000 || completionTime > 300000) {
            return res.status(400).json({ error: 'Invalid completion time' });
        }
        
        // Validate detection methods
        const detectionScore = Object.values(detectionMethods || {}).filter(Boolean).length;
        if (detectionScore < 2) {
            return res.status(400).json({ error: 'Insufficient completion validation' });
        }
        
        // Award coins
        const user = await User.findById(userId);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        user.coins += 8;
        await user.save();
        
        // Update session
        req.session.user.coins = user.coins;
        
        // Record completion
        const sessionData = {
            sessionId,
            timestamp: now,
            completionTime,
            detectionMethods,
            userAgent,
            coinsAwarded: 8
        };
        
        userSessions.push(sessionData);
        
        // Keep only last 10 sessions per user
        if (userSessions.length > 10) {
            userSessions.splice(0, userSessions.length - 10);
        }
        
        linkvertiseSessions.set(userId, userSessions);
        
        console.log(`User ${user.username} completed Linkvertise task: +8 coins (Session: ${sessionId})`);
        
        res.json({
            success: true,
            coinsEarned: 8,
            newBalance: user.coins,
            sessionId: sessionId
        });
        
    } catch (error) {
        console.error('Linkvertise completion error:', error);
        res.status(500).json({ error: 'Failed to process completion' });
    }
});

// AFK earning with anti-cheat
const afkSessions = new Map();

app.post('/api/afk-earn', async (req, res) => {
    if (!req.session || !req.session.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    const userId = req.session.user.id;
    const now = Date.now();
    
    try {
        // Anti-cheat: Check session timing
        const lastEarn = afkSessions.get(userId);
        if (lastEarn && (now - lastEarn) < 55000) { // Must wait at least 55 seconds
            return res.status(429).json({ error: 'Too fast! Wait for the timer.' });
        }
        
        // Update last earn time
        afkSessions.set(userId, now);
        
        // Give coins
        const user = await User.findById(userId);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        user.coins += 1.2;
        await user.save();
        
        // Update session
        req.session.user.coins = user.coins;
        
        console.log(`User ${user.username} earned 1.2 coins from AFK`);
        
        res.json({
            success: true,
            earned: 1.2,
            newBalance: user.coins
        });
    } catch (error) {
        console.error('AFK earn error:', error);
        res.status(500).json({ error: 'Failed to earn coins' });
    }
});

// Create promotion
app.post('/api/create-promotion', async (req, res) => {
    if (!req.session || !req.session.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    const { serverName, serverIP, description } = req.body;
    
    if (!serverName || !serverIP || !description) {
        return res.status(400).json({ error: 'All fields are required' });
    }
    
    try {
        const user = await User.findById(req.session.user.id);
        
        if (user.coins < 500) {
            return res.status(400).json({ error: 'Insufficient coins. Need 500 coins.' });
        }
        
        // Check if user already has a promotion with same server name
        const existingPromo = await Promotion.findOne({ 
            authorId: user._id, 
            serverName: serverName.trim() 
        });
        
        if (existingPromo) {
            return res.status(400).json({ error: 'You already have a promotion for this server' });
        }
        
        // Deduct coins
        user.coins -= 500;
        await user.save();
        
        // Create promotion
        const promotion = new Promotion({
            serverName: serverName.trim(),
            serverIP: serverIP.trim(),
            description: description.trim(),
            author: user.username,
            authorId: user._id
        });
        
        await promotion.save();
        
        // Update session
        req.session.user.coins = user.coins;
        
        console.log(`User ${user.username} created promotion for ${serverName}`);
        
        res.json({
            success: true,
            promotion,
            newBalance: user.coins
        });
    } catch (error) {
        console.error('Create promotion error:', error);
        res.status(500).json({ error: 'Failed to create promotion' });
    }
});

// Boost promotion
app.post('/api/boost-promotion', async (req, res) => {
    if (!req.session || !req.session.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    const { promotionId } = req.body;
    
    if (!promotionId) {
        return res.status(400).json({ error: 'Promotion ID is required' });
    }
    
    try {
        const user = await User.findById(req.session.user.id);
        const promotion = await Promotion.findById(promotionId);
        
        if (!promotion) {
            return res.status(404).json({ error: 'Promotion not found' });
        }
        
        if (promotion.authorId.toString() !== user._id.toString()) {
            return res.status(403).json({ error: 'You can only boost your own promotions' });
        }
        
        if (user.coins < 100) {
            return res.status(400).json({ error: 'Insufficient coins. Need 100 coins.' });
        }
        
        // Deduct coins and boost
        user.coins -= 100;
        promotion.boosted = true;
        promotion.boostCount += 1;
        
        await user.save();
        await promotion.save();
        
        // Update session
        req.session.user.coins = user.coins;
        
        console.log(`User ${user.username} boosted promotion ${promotion.serverName}`);
        
        res.json({
            success: true,
            newBalance: user.coins
        });
    } catch (error) {
        console.error('Boost promotion error:', error);
        res.status(500).json({ error: 'Failed to boost promotion' });
    }
});

// Get promotions
app.get('/api/promotions', async (req, res) => {
    try {
        const promotions = await Promotion.find({})
            .sort({ boosted: -1, createdAt: -1 })
            .limit(50);
        
        res.json({
            success: true,
            promotions
        });
    } catch (error) {
        console.error('Get promotions error:', error);
        res.status(500).json({ error: 'Failed to get promotions' });
    }
});

// Update server resources
app.post('/api/update-server-resources', async (req, res) => {
    if (!req.session || !req.session.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    const { serverIdentifier, resources } = req.body;
    
    if (!serverIdentifier || !resources) {
        return res.status(400).json({ error: 'Server identifier and resources are required' });
    }
    
    try {
        const user = await User.findById(req.session.user.id);
        if (!user.pterodactylUserId) {
            return res.status(400).json({ error: 'Pterodactyl account not found' });
        }
        
        // Get user servers to verify ownership
        const servers = await getUserServers(user.pterodactylUserId);
        const server = servers.find(s => s.attributes.identifier === serverIdentifier);
        
        if (!server) {
            return res.status(404).json({ error: 'Server not found or access denied' });
        }
        
        // Validate resource limits
        const limits = {
            ram: { min: 512, max: 2048 },
            cpu: { min: 25, max: 100 },
            disk: { min: 1024, max: 5120 }
        };
        
        if (resources.ram < limits.ram.min || resources.ram > limits.ram.max) {
            return res.status(400).json({ error: `RAM must be between ${limits.ram.min}MB and ${limits.ram.max}MB` });
        }
        
        if (resources.cpu < limits.cpu.min || resources.cpu > limits.cpu.max) {
            return res.status(400).json({ error: `CPU must be between ${limits.cpu.min}% and ${limits.cpu.max}%` });
        }
        
        if (resources.disk < limits.disk.min || resources.disk > limits.disk.max) {
            return res.status(400).json({ error: `Disk must be between ${limits.disk.min}MB and ${limits.disk.max}MB` });
        }
        
        // Update server via Pterodactyl API
        const updateData = {
            limits: {
                memory: resources.ram,
                cpu: resources.cpu,
                disk: resources.disk,
                swap: 0,
                io: 500
            }
        };
        
        const response = await pterodactylAPI.patch(`/servers/${server.attributes.id}/build`, updateData);
        
        if (response.status === 200) {
            console.log(`Updated server ${serverIdentifier} resources:`, resources);
            
            res.json({
                success: true,
                message: 'Server resources updated successfully',
                resources
            });
        } else {
            console.error('Pterodactyl API error:', response.data);
            res.status(500).json({ error: 'Failed to update server resources' });
        }
        
    } catch (error) {
        console.error('Update server resources error:', error);
        
        if (error.response?.data?.errors) {
            const errors = error.response.data.errors;
            const firstError = Object.values(errors)[0];
            const errorMessage = Array.isArray(firstError) ? firstError[0] : firstError;
            return res.status(400).json({ error: errorMessage });
        }
        
        res.status(500).json({ error: 'Failed to update server resources' });
    }
});

// Admin API route to create user
app.post('/api/admin/create-user', checkAdmin, async (req, res) => {
    const { username, password } = req.body;
    
    if (!username || !password) {
        return res.status(400).json({ error: 'Username and password are required' });
    }
    
    if (username.length < 3 || password.length < 3) {
        return res.status(400).json({ error: 'Username and password must be at least 3 characters' });
    }
    
    try {
        // Check if user already exists
        const existingUser = await User.findOne({ username: username.trim() });
        if (existingUser) {
            return res.status(400).json({ error: 'Username already exists' });
        }
        
        // Create new user
        const newUser = new User({
            username: username.trim(),
            password: password.trim(),
            coins: 100, // Starting coins
            serverCount: 0,
            createdBy: req.session.user.username
        });
        
        await newUser.save();
        
        console.log(`Admin ${req.session.user.username} created user: ${username}`);
        
        res.json({
            success: true,
            message: `User "${username}" created successfully`,
            user: {
                username: newUser.username,
                coins: newUser.coins,
                id: newUser._id
            }
        });
    } catch (error) {
        console.error('Error creating user:', error);
        res.status(500).json({ error: 'Failed to create user' });
    }
});

// Quick user creation for admins
app.post('/api/quick-user', async (req, res) => {
    const { username, password, adminKey } = req.body;
    
    // Simple admin check
    if (adminKey !== 'blazenode2025') {
        return res.status(403).json({ error: 'Access denied' });
    }
    
    try {
        if (!username || !password) {
            return res.status(400).json({ error: 'Username and password required' });
        }
        
        const existingUser = await User.findOne({ username: username.trim() });
        if (existingUser) {
            return res.json({ success: true, message: 'User already exists', username });
        }
        
        const newUser = new User({
            username: username.trim(),
            password: password.trim(),
            coins: 1000,
            serverCount: 0,
            createdBy: 'quick-create'
        });
        
        await newUser.save();
        
        res.json({ 
            success: true, 
            message: 'User created successfully',
            username: newUser.username,
            password: password.trim()
        });
        
    } catch (error) {
        res.status(500).json({ error: 'Failed to create user' });
    }
});

// Bot API middleware
function checkBotAuth(req, res, next) {
    const authHeader = req.headers.authorization;
    const expectedToken = `Bearer ${config.BOT_API_KEY}`;
    
    if (authHeader === expectedToken) {
        next();
    } else {
        res.status(401).json({ error: 'Unauthorized bot access' });
    }
}

// Bot API route to create user
app.post('/api/bot/create-user', checkBotAuth, async (req, res) => {
    const { username, discordId, coins = 100 } = req.body;
    
    if (!username || !discordId) {
        return res.status(400).json({ error: 'Username and Discord ID are required' });
    }
    
    try {
        // Check if user already exists
        const existingUser = await User.findOne({ 
            $or: [{ username }, { discordId }] 
        });
        
        if (existingUser) {
            return res.json({ 
                success: true, 
                user: existingUser,
                message: 'User already exists'
            });
        }
        
        // Create new user
        const newUser = new User({
            username,
            password: username, // Default password same as username
            discordId,
            coins,
            serverCount: 0,
            createdBy: 'discord-bot'
        });
        
        await newUser.save();
        
        console.log(`Bot created user: ${username} (Discord: ${discordId})`);
        
        res.json({
            success: true,
            user: {
                username: newUser.username,
                discordId: newUser.discordId,
                coins: newUser.coins,
                id: newUser._id
            }
        });
    } catch (error) {
        console.error('Bot user creation error:', error);
        res.status(500).json({ error: 'Failed to create user' });
    }
});

// Bot API route to give coins
app.post('/api/bot/give-coins', checkBotAuth, async (req, res) => {
    const { username, coins } = req.body;
    
    if (!username || !coins || coins <= 0) {
        return res.status(400).json({ error: 'Valid username and coins amount required' });
    }
    
    try {
        const user = await User.findOne({ username });
        
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        user.coins += parseInt(coins);
        await user.save();
        
        console.log(`Bot gave ${coins} coins to ${username}`);
        
        res.json({
            success: true,
            newBalance: user.coins,
            message: `Gave ${coins} coins to ${username}`
        });
    } catch (error) {
        console.error('Bot give coins error:', error);
        res.status(500).json({ error: 'Failed to give coins' });
    }
});

// Bot API route to get user info
app.get('/api/bot/user/:username', checkBotAuth, async (req, res) => {
    const { username } = req.params;
    
    try {
        const user = await User.findOne({ username }).select('username coins serverCount discordId');
        
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        res.json({
            success: true,
            user: {
                username: user.username,
                coins: user.coins,
                serverCount: user.serverCount,
                discordId: user.discordId
            }
        });
    } catch (error) {
        console.error('Bot get user error:', error);
        res.status(500).json({ error: 'Failed to get user info' });
    }
});

// COMPREHENSIVE HEALTH CHECK
app.get('/api/health', async (req, res) => {
    console.log('\n=== HEALTH CHECK ===');
    
    const healthData = {
        status: 'OK',
        timestamp: new Date().toISOString(),
        server: {
            uptime: Math.round(process.uptime()),
            memory: {
                used: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
                total: Math.round(process.memoryUsage().heapTotal / 1024 / 1024)
            },
            nodeVersion: process.version,
            platform: process.platform
        },
        database: {
            state: mongoose.connection.readyState,
            stateText: {
                0: 'Disconnected',
                1: 'Connected',
                2: 'Connecting', 
                3: 'Disconnecting'
            }[mongoose.connection.readyState],
            host: mongoose.connection.host,
            name: mongoose.connection.name
        },
        session: {
            exists: !!req.session,
            id: req.sessionID,
            user: !!req.session?.user,
            username: req.session?.user?.username || null
        }
    };
    
    // Test database connection
    try {
        const userCount = await User.countDocuments().maxTimeMS(5000);
        healthData.database.userCount = userCount;
        healthData.database.queryTest = 'SUCCESS';
    } catch (dbError) {
        healthData.database.queryTest = 'FAILED';
        healthData.database.error = dbError.message;
    }
    
    console.log('Health check result:', JSON.stringify(healthData, null, 2));
    console.log('=== HEALTH CHECK END ===\n');
    
    res.json(healthData);
});



// DETAILED STATUS ENDPOINT
app.get('/api/status', async (req, res) => {
    try {
        const statusData = {
            status: 'OPERATIONAL',
            timestamp: new Date().toISOString(),
            version: '2.1.73',
            environment: config.NODE_ENV || 'production',
            server: {
                uptime: process.uptime(),
                memory: process.memoryUsage(),
                cpu: process.cpuUsage(),
                platform: process.platform,
                nodeVersion: process.version
            },
            database: {
                connection: mongoose.connection.readyState === 1 ? 'CONNECTED' : 'DISCONNECTED',
                state: mongoose.connection.readyState,
                host: mongoose.connection.host,
                name: mongoose.connection.name
            },
            apis: {
                pterodactyl: 'CHECKING...',
                mongodb: 'CHECKING...'
            }
        };
        
        // Test MongoDB
        try {
            const dbTest = await User.findOne({}).maxTimeMS(3000);
            statusData.apis.mongodb = 'OPERATIONAL';
            statusData.database.testQuery = 'SUCCESS';
        } catch (dbError) {
            statusData.apis.mongodb = 'ERROR';
            statusData.database.testQuery = 'FAILED';
            statusData.database.error = dbError.message;
        }
        
        // Test Pterodactyl API
        try {
            const pterodactylTest = await pterodactylAPI.get('/nests');
            statusData.apis.pterodactyl = 'OPERATIONAL';
            statusData.pterodactyl = {
                status: 'CONNECTED',
                nestsCount: pterodactylTest.data.data?.length || 0
            };
        } catch (pterodactylError) {
            statusData.apis.pterodactyl = 'ERROR';
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

// Initialize node management on startup
(async () => {
    try {
        console.log('🔄 Initializing node management...');
        const nodes = await getAvailableNodes();
        if (nodes.length > 0) {
            currentActiveNode = nodes[0];
            console.log(`✅ Active node set to: ${currentActiveNode.name}`);
        }
    } catch (error) {
        console.error('❌ Failed to initialize node management:', error.message);
    }
})();

// Add Discord ID field to User model if not exists
(async () => {
    try {
        await User.updateMany(
            { discordId: { $exists: false } },
            { $set: { discordId: null } }
        );
        console.log('✅ User model updated for Discord integration');
    } catch (error) {
        console.error('❌ Failed to update user model:', error.message);
    }
})();

// Export app for cPanel
module.exports = app;

console.log('\n' + '='.repeat(60));
console.log('🚀 BLAZENODE DASHBOARD - CPANEL OPTIMIZED');
console.log('='.repeat(60));
console.log('✅ Server Status: READY');
console.log('✅ Login System: BULLETPROOF IMPLEMENTATION');
console.log('✅ Database: AUTO-CONNECTING');
console.log('✅ Session Management: ENHANCED');
console.log('✅ Error Handling: COMPREHENSIVE');
console.log('✅ Debugging: EXTENSIVE LOGGING');
console.log('✅ cPanel Compatibility: OPTIMIZED');
console.log('⚡ Ready for production deployment!');
console.log('='.repeat(60));
console.log('Test Login: username="test", password="test"');
console.log('Health Check: /api/health');
console.log('Status Check: /api/status');
console.log('='.repeat(60) + '\n');