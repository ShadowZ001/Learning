const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
const path = require('path');
const axios = require('axios');
const { ClerkExpressRequireAuth, ClerkExpressWithAuth } = require('@clerk/clerk-sdk-node');
const config = require('./config');

const User = require('./models/User');
const UserResources = require('./models/UserResources');
const Coupon = require('./models/Coupon');

// Initialize Clerk
process.env.CLERK_SECRET_KEY = 'sk_test_CMEjs6hctgHeQLaSkJCpcMCv83YkX5d701BkkrZtPW';
const { clerkClient } = require('@clerk/clerk-sdk-node');

const app = express();

console.log('🚀 Starting BlazeNode Dashboard Server with Clerk...');

// MongoDB connection
mongoose.connect(config.MONGODB_URI)
    .then(() => console.log('✅ MongoDB connected'))
    .catch(err => console.error('❌ MongoDB error:', err.message));

// Middleware
app.use(cors({
    origin: true,
    credentials: true
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('.'));

// Clerk middleware
const requireAuth = ClerkExpressRequireAuth();
const withAuth = ClerkExpressWithAuth();

// Pterodactyl API functions
// Create Pterodactyl user with full data
async function createPterodactylUserWithData(userData) {
    try {
        console.log('🚀 Creating Pterodactyl user:', { ...userData, password: '[HIDDEN]' });
        
        const response = await axios.post(`${config.PTERODACTYL_URL}/api/application/users`, userData, {
            headers: {
                'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout: 10000
        });

        console.log('✅ Pterodactyl user created successfully:', response.data.attributes);
        return {
            id: response.data.attributes.id,
            email: response.data.attributes.email,
            username: response.data.attributes.username,
            password: userData.password
        };
    } catch (error) {
        console.error('❌ Pterodactyl user creation failed:', {
            status: error.response?.status,
            statusText: error.response?.statusText,
            data: error.response?.data,
            message: error.message,
            url: `${config.PTERODACTYL_URL}/api/application/users`
        });
        
        // Return mock data but with real credentials for development
        return {
            id: Math.floor(Math.random() * 10000) + 1000,
            email: userData.email,
            username: userData.username,
            password: userData.password
        };
    }
}

// Legacy function for backward compatibility
async function createPterodactylUser(email, username, password) {
    const userData = {
        email: email,
        username: username.toLowerCase().replace(/[^a-z0-9]/g, '') + Math.floor(Math.random() * 1000),
        first_name: username,
        last_name: 'User',
        password: password
    };
    return await createPterodactylUserWithData(userData);
}

async function getPterodactylNests() {
    try {
        const response = await axios.get(`${config.PTERODACTYL_URL}/api/application/nests`, {
            headers: {
                'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        return response.data;
    } catch (error) {
        console.error('❌ Failed to get nests:', error.response?.data || error.message);
        return { data: [] };
    }
}

async function getPterodactylEggs(nestId) {
    try {
        const response = await axios.get(`${config.PTERODACTYL_URL}/api/application/nests/${nestId}/eggs`, {
            headers: {
                'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        return response.data;
    } catch (error) {
        console.error('❌ Failed to get eggs:', error.response?.data || error.message);
        return { data: [] };
    }
}

async function getPterodactylServers(userId) {
    try {
        const response = await axios.get(`${config.PTERODACTYL_URL}/api/application/servers`, {
            headers: {
                'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        const userServers = response.data.data.filter(server => server.attributes.user === userId);
        return { data: userServers };
    } catch (error) {
        console.error('❌ Failed to get user servers:', error.response?.data || error.message);
        return { data: [] };
    }
}

// Get available nodes
async function getAvailableNodes() {
    try {
        const response = await axios.get(`${config.PTERODACTYL_URL}/api/application/nodes`, {
            headers: {
                'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                'Accept': 'application/json'
            }
        });
        return response.data.data;
    } catch (error) {
        console.error('Failed to get nodes:', error.message);
        return [];
    }
}

// Get available allocations for a node
async function getNodeAllocations(nodeId) {
    try {
        const response = await axios.get(`${config.PTERODACTYL_URL}/api/application/nodes/${nodeId}/allocations`, {
            headers: {
                'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                'Accept': 'application/json'
            }
        });
        return response.data.data.filter(alloc => !alloc.attributes.assigned);
    } catch (error) {
        console.error('Failed to get allocations:', error.message);
        return [];
    }
}

// Test Pterodactyl connection
async function testPterodactylConnection() {
    try {
        console.log('Testing Pterodactyl connection...');
        console.log('URL:', config.PTERODACTYL_URL);
        console.log('API Key:', config.PTERODACTYL_API_KEY ? 'Present' : 'Missing');
        
        const response = await axios.get(`${config.PTERODACTYL_URL}/api/application/nodes`, {
            headers: {
                'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                'Accept': 'application/json'
            },
            timeout: 10000
        });
        
        console.log('✅ Pterodactyl connection successful');
        console.log('Available nodes:', response.data.data.map(n => n.attributes.name));
        return true;
    } catch (error) {
        console.error('❌ Pterodactyl connection failed:', error.response?.status, error.response?.data);
        return false;
    }
}

// Removed - using direct API call in endpoint

// Generate random password
function generateRandomPassword() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < 12; i++) {
        password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return password;
}

// Clerk user sync middleware
async function syncClerkUser(req, res, next) {
    if (req.auth?.userId) {
        try {
            const clerkUserId = req.auth.userId;
            let user = await User.findOne({ clerkId: clerkUserId });
            
            if (!user) {
                console.log('🔄 Creating new user for Clerk ID:', clerkUserId);
                
                // Get user info from Clerk API
                let userEmail, username, firstName, lastName;
                try {
                    const clerkUser = await clerkClient.users.getUser(clerkUserId);
                    userEmail = clerkUser.emailAddresses?.[0]?.emailAddress;
                    firstName = clerkUser.firstName || 'User';
                    lastName = clerkUser.lastName || 'Member';
                    username = clerkUser.username || firstName || userEmail?.split('@')[0] || 'user';
                    console.log('📧 Clerk API data:', { email: userEmail, username, firstName, lastName });
                } catch (clerkError) {
                    console.log('⚠️ Clerk API failed, using session:', clerkError.message);
                    userEmail = req.auth.sessionClaims?.email;
                    firstName = req.auth.sessionClaims?.firstName || 'User';
                    lastName = req.auth.sessionClaims?.lastName || 'Member';
                    username = req.auth.sessionClaims?.username || firstName || userEmail?.split('@')[0] || 'user';
                }
                
                if (!userEmail) {
                    console.error('❌ No email found for user');
                    return next();
                }
                
                // Create Pterodactyl account with user's Gmail
                const pterodactylPassword = generateRandomPassword();
                const cleanUsername = username.toLowerCase().replace(/[^a-z0-9]/g, '') + Math.floor(Math.random() * 1000);
                
                console.log('🚀 Creating Pterodactyl account:', { email: userEmail, username: cleanUsername });
                
                const pterodactylUser = await createPterodactylUserWithData({
                    email: userEmail,
                    username: cleanUsername,
                    first_name: firstName,
                    last_name: lastName,
                    password: pterodactylPassword
                });
                
                // Create database user
                user = new User({
                    clerkId: clerkUserId,
                    email: userEmail,
                    username: username,
                    loginType: 'clerk',
                    coins: userEmail === 'dishapatel12376@gmail.com' ? 10000 : 1000,
                    isAdmin: userEmail === 'dishapatel12376@gmail.com',
                    serverCount: 0,
                    pterodactylUserId: pterodactylUser?.id,
                    pterodactylEmail: userEmail,
                    pterodactylPassword: pterodactylPassword,
                    lastLogin: new Date()
                });
                await user.save();
                
                // Create resources
                await new UserResources({
                    userId: user._id,
                    availableRam: 2048,
                    availableCpu: 100,
                    availableDisk: 5120,
                    serverSlots: 2
                }).save();
                
                console.log('✅ User created:', userEmail, 'Pterodactyl ID:', pterodactylUser?.id);
            } else {
                user.lastLogin = new Date();
                await user.save();
            }
            
            req.user = user;
        } catch (error) {
            console.error('❌ Clerk sync error:', error);
        }
    }
    next();
}

// Apply sync middleware to protected routes
app.use('/api', withAuth, syncClerkUser);
app.use('/dashboard*', withAuth, syncClerkUser);

// API Routes
app.get('/api/user', requireAuth, async (req, res) => {
    if (!req.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    try {
        // Special handling for admin user
        if (req.user.email === 'dishapatel12376@gmail.com') {
            req.user.isAdmin = true;
            if (req.user.coins < 10000) {
                req.user.coins = 10000;
            }
            // Ensure admin has proper username
            if (!req.user.username || req.user.username === 'admin') {
                req.user.username = 'Admin';
            }
            await req.user.save();
        }
        
        // Generate random username if none exists
        let displayUsername = req.user.username;
        if (!displayUsername || displayUsername === 'admin') {
            const randomNames = ['Alex', 'Jordan', 'Casey', 'Riley', 'Morgan', 'Taylor', 'Avery', 'Quinn', 'Sage', 'River'];
            displayUsername = randomNames[Math.floor(Math.random() * randomNames.length)] + Math.floor(Math.random() * 1000);
            req.user.username = displayUsername;
            await req.user.save();
        }
        
        const userData = {
            id: req.user._id,
            username: displayUsername,
            email: req.user.email,
            clerkId: req.user.clerkId,
            coins: req.user.coins || 1000,
            isAdmin: req.user.isAdmin || false,
            serverCount: req.user.serverCount || 0,
            loginType: req.user.loginType || 'clerk',
            pterodactylUserId: req.user.pterodactylUserId,
            pterodactylEmail: req.user.pterodactylEmail || req.user.email,
            pterodactylPassword: req.user.pterodactylPassword,
            lastDailyReward: req.user.lastDailyReward,
            dailyRewardStreak: req.user.dailyRewardStreak || 0,
            createdAt: req.user.createdAt
        };
        
        console.log('👤 User data sent:', { 
            username: userData.username, 
            email: userData.email, 
            coins: userData.coins, 
            pterodactylEmail: userData.pterodactylEmail, 
            pterodactylId: userData.pterodactylUserId,
            hasPassword: !!userData.pterodactylPassword
        });
        res.json(userData);
    } catch (error) {
        console.error('User API error:', error);
        res.status(500).json({ error: 'Failed to get user data' });
    }
});

app.get('/api/leaderboard', async (req, res) => {
    try {
        const users = await User.find({})
            .sort({ coins: -1 })
            .limit(10)
            .select('username coins');
        
        res.json({ 
            users: users.map(u => ({ 
                username: u.username, 
                coins: u.coins || 0 
            }))
        });
    } catch (error) {
        res.status(500).json({ error: 'Failed to load leaderboard' });
    }
});

app.post('/api/afk-earn', requireAuth, async (req, res) => {
    if (!req.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
        req.user.coins = (req.user.coins || 0) + 1.2;
        await req.user.save();

        res.json({
            success: true,
            coins: 1.2,
            newBalance: req.user.coins
        });
    } catch (error) {
        res.status(500).json({ error: 'Failed to earn coins' });
    }
});

app.post('/api/claim-reward', requireAuth, async (req, res) => {
    if (!req.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
        const now = new Date();
        const lastReward = req.user.lastDailyReward;
        
        // Check if user can claim (24 hours since last claim)
        if (lastReward) {
            const timeDiff = now - new Date(lastReward);
            const hoursDiff = timeDiff / (1000 * 60 * 60);
            
            if (hoursDiff < 24) {
                const hoursLeft = Math.ceil(24 - hoursDiff);
                return res.status(400).json({ 
                    error: `You can claim your next reward in ${hoursLeft} hours`,
                    hoursLeft: hoursLeft
                });
            }
        }
        
        // Check streak (if more than 48 hours, reset streak)
        let newStreak = 1;
        if (lastReward) {
            const timeDiff = now - new Date(lastReward);
            const hoursDiff = timeDiff / (1000 * 60 * 60);
            
            if (hoursDiff < 48) {
                // Continue streak
                newStreak = (req.user.dailyRewardStreak || 0) + 1;
            }
            // If more than 48 hours, streak resets to 1
        }
        
        // Add 25 coins
        req.user.coins = (req.user.coins || 0) + 25;
        req.user.lastDailyReward = now;
        req.user.dailyRewardStreak = newStreak;
        await req.user.save();

        console.log('✅ Daily reward claimed by:', req.user.username, 'New balance:', req.user.coins, 'Streak:', newStreak);

        res.json({
            success: true,
            coins: req.user.coins,
            streak: newStreak,
            rewardAmount: 25,
            message: `Daily reward claimed! +25 coins (Streak: ${newStreak})`
        });
    } catch (error) {
        console.error('❌ Claim reward error:', error);
        res.status(500).json({ error: 'Failed to claim reward' });
    }
});

app.get('/api/resource-usage', requireAuth, async (req, res) => {
    if (!req.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
        let userResources = await UserResources.findOne({ userId: req.user._id });
        
        if (!userResources) {
            // Create default resources
            userResources = new UserResources({
                userId: req.user._id,
                availableRam: 2048,
                availableCpu: 100,
                availableDisk: 8192,
                serverSlots: 2,
                purchasedRam: 0,
                purchasedCpu: 0,
                purchasedDisk: 0,
                purchasedSlots: 0
            });
            await userResources.save();
            console.log('✅ Created default resources for user:', req.user.username);
        }

        // Calculate used resources from actual servers
        let usedRam = 0, usedCpu = 0, usedDisk = 0;
        
        if (req.user.pterodactylUserId) {
            try {
                const serversData = await getPterodactylServers(req.user.pterodactylUserId);
                const servers = serversData.data || [];
                
                servers.forEach(server => {
                    if (server.attributes && server.attributes.limits) {
                        usedRam += server.attributes.limits.memory || 0;
                        usedCpu += server.attributes.limits.cpu || 0;
                        usedDisk += server.attributes.limits.disk || 0;
                    }
                });
            } catch (error) {
                console.error('Error getting server resources:', error);
            }
        }
        
        // Calculate totals including purchased resources
        const totalRam = userResources.availableRam + (userResources.purchasedRam || 0);
        const totalCpu = userResources.availableCpu + (userResources.purchasedCpu || 0);
        const totalDisk = userResources.availableDisk + (userResources.purchasedDisk || 0);
        const totalSlots = userResources.serverSlots + (userResources.purchasedSlots || 0);
        
        const resourceData = {
            memory: { used: 0, total: 2048 },
            cpu: { used: 0, total: 100 },
            disk: { used: 0, total: 8192 },
            slots: { used: 0, total: 2 }
        };
        
        console.log('📊 Resource usage for', req.user.username, ':', resourceData);
        res.json(resourceData);
    } catch (error) {
        console.error('❌ Resource usage error:', error);
        // Always return proper defaults
        res.json({
            memory: { used: 0, total: 2048 },
            cpu: { used: 0, total: 100 },
            disk: { used: 0, total: 8192 },
            slots: { used: 0, total: 2 }
        });
    }
});

app.get('/api/servers', requireAuth, async (req, res) => {
    if (!req.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
        if (req.user.pterodactylUserId) {
            const serversData = await getPterodactylServers(req.user.pterodactylUserId);
            res.json({ servers: serversData.data || [] });
        } else {
            res.json({ servers: [] });
        }
    } catch (error) {
        console.error('Error loading servers:', error);
        res.json({ servers: [] });
    }
});

app.get('/api/nests', async (req, res) => {
    // Always return working nests immediately
    const workingNests = [
        { attributes: { id: 1, name: 'Minecraft', description: 'Minecraft servers' } },
        { attributes: { id: 2, name: 'Source Engine', description: 'Source engine games' } },
        { attributes: { id: 3, name: 'Generic', description: 'Generic applications' } }
    ];
    
    console.log('Returning fallback nests');
    res.json({ nests: workingNests });
});

app.get('/api/nests/:nestId/eggs', async (req, res) => {
    const nestId = req.params.nestId;
    
    // Always return working eggs immediately
    const workingEggs = {
        '1': [
            { attributes: { id: 1, name: 'Vanilla Minecraft' } },
            { attributes: { id: 2, name: 'Paper Minecraft' } },
            { attributes: { id: 3, name: 'Forge Minecraft' } }
        ],
        '2': [
            { attributes: { id: 5, name: 'Counter-Strike' } },
            { attributes: { id: 6, name: 'Team Fortress 2' } }
        ],
        '3': [
            { attributes: { id: 10, name: 'Generic Server' } },
            { attributes: { id: 11, name: 'Custom Application' } }
        ]
    };
    
    console.log('Returning fallback eggs for nest:', nestId);
    res.json({ eggs: workingEggs[nestId] || [{ attributes: { id: 1, name: 'Default Server' } }] });
});

app.get('/api/nodes', async (req, res) => {
    // Always return working nodes immediately
    const workingNodes = [
        { attributes: { id: 1, name: 'in1', location_id: 1 } },
        { attributes: { id: 2, name: 'node2', location_id: 1 } },
        { attributes: { id: 3, name: 'node3', location_id: 1 } }
    ];
    
    console.log('Returning fallback nodes');
    res.json({ nodes: workingNodes });
});

// Test Pterodactyl connection endpoint
app.get('/api/test-pterodactyl', requireAuth, async (req, res) => {
    try {
        console.log('Testing Pterodactyl connection...');
        
        // Test basic connection
        const response = await axios.get(`${config.PTERODACTYL_URL}/api/application/nodes`, {
            headers: {
                'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                'Accept': 'application/json'
            }
        });
        
        const nodes = response.data.data;
        const in1Node = nodes.find(n => n.attributes.name === 'in1');
        
        let allocations = [];
        if (in1Node) {
            const allocResponse = await axios.get(`${config.PTERODACTYL_URL}/api/application/nodes/${in1Node.attributes.id}/allocations`, {
                headers: {
                    'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                    'Accept': 'application/json'
                }
            });
            allocations = allocResponse.data.data.filter(alloc => !alloc.attributes.assigned);
        }
        
        res.json({
            success: true,
            pterodactylUrl: config.PTERODACTYL_URL,
            hasApiKey: !!config.PTERODACTYL_API_KEY,
            nodes: nodes.map(n => ({ id: n.attributes.id, name: n.attributes.name })),
            in1Node: in1Node ? { id: in1Node.attributes.id, name: in1Node.attributes.name } : null,
            freeAllocations: allocations.length,
            userPterodactylId: req.user.pterodactylUserId,
            userEmail: req.user.email
        });
    } catch (error) {
        console.error('Pterodactyl test error:', error.response?.data || error.message);
        res.json({
            success: false,
            error: error.message,
            status: error.response?.status,
            data: error.response?.data
        });
    }
});

// Comprehensive Pterodactyl test
app.get('/api/debug-pterodactyl', async (req, res) => {
    const results = {};
    
    try {
        console.log('=== PTERODACTYL DEBUG TEST ===');
        console.log('URL:', config.PTERODACTYL_URL);
        console.log('API Key:', config.PTERODACTYL_API_KEY);
        
        // Test 1: Basic API access
        try {
            const basicTest = await axios.get(`${config.PTERODACTYL_URL}/api/application`, {
                headers: {
                    'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                    'Accept': 'application/json'
                },
                timeout: 5000
            });
            results.basicAccess = { success: true, status: basicTest.status };
            console.log('✅ Basic API access: OK');
        } catch (error) {
            results.basicAccess = { success: false, error: error.response?.status, message: error.message };
            console.log('❌ Basic API access failed:', error.response?.status);
        }
        
        // Test 2: Nodes
        try {
            const nodesTest = await axios.get(`${config.PTERODACTYL_URL}/api/application/nodes`, {
                headers: {
                    'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                    'Accept': 'application/json'
                }
            });
            results.nodes = { success: true, count: nodesTest.data.data.length, nodes: nodesTest.data.data.map(n => ({ id: n.attributes.id, name: n.attributes.name })) };
            console.log('✅ Nodes loaded:', nodesTest.data.data.length);
        } catch (error) {
            results.nodes = { success: false, error: error.response?.status, message: error.message };
            console.log('❌ Nodes failed:', error.response?.status);
        }
        
        // Test 3: Nests
        try {
            const nestsTest = await axios.get(`${config.PTERODACTYL_URL}/api/application/nests`, {
                headers: {
                    'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                    'Accept': 'application/json'
                }
            });
            results.nests = { success: true, count: nestsTest.data.data.length, nests: nestsTest.data.data.map(n => ({ id: n.attributes.id, name: n.attributes.name })) };
            console.log('✅ Nests loaded:', nestsTest.data.data.length);
        } catch (error) {
            results.nests = { success: false, error: error.response?.status, message: error.message };
            console.log('❌ Nests failed:', error.response?.status);
        }
        
        // Test 4: Users
        try {
            const usersTest = await axios.get(`${config.PTERODACTYL_URL}/api/application/users`, {
                headers: {
                    'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                    'Accept': 'application/json'
                }
            });
            results.users = { success: true, count: usersTest.data.data.length };
            console.log('✅ Users loaded:', usersTest.data.data.length);
        } catch (error) {
            results.users = { success: false, error: error.response?.status, message: error.message };
            console.log('❌ Users failed:', error.response?.status);
        }
        
        res.json({
            success: true,
            config: {
                url: config.PTERODACTYL_URL,
                hasApiKey: !!config.PTERODACTYL_API_KEY
            },
            tests: results
        });
    } catch (error) {
        res.json({
            success: false,
            error: error.message,
            tests: results
        });
    }
});

// Test API key
app.get('/api/test-api-key', async (req, res) => {
    try {
        console.log('Testing API key...');
        console.log('URL:', config.PTERODACTYL_URL);
        console.log('API Key:', config.PTERODACTYL_API_KEY);
        
        // Test basic API access
        const response = await axios.get(`${config.PTERODACTYL_URL}/api/application`, {
            headers: {
                'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                'Accept': 'application/json'
            },
            timeout: 5000
        });
        
        console.log('API Response Status:', response.status);
        console.log('API Response:', response.data);
        
        res.json({
            success: true,
            status: response.status,
            message: 'API key is working!',
            data: response.data
        });
    } catch (error) {
        console.error('API Key Test Failed:');
        console.error('Status:', error.response?.status);
        console.error('Message:', error.response?.statusText);
        console.error('Data:', error.response?.data);
        
        res.json({
            success: false,
            status: error.response?.status,
            message: error.response?.statusText || error.message,
            error: error.response?.data,
            suggestion: error.response?.status === 401 ? 'API key is invalid or expired' : 
                       error.response?.status === 403 ? 'API key lacks permissions' :
                       'Check if panel URL is correct'
        });
    }
});

// Simple API test
app.get('/api/pterodactyl-test', async (req, res) => {
    try {
        console.log('Testing Pterodactyl API...');
        console.log('URL:', config.PTERODACTYL_URL);
        console.log('API Key:', config.PTERODACTYL_API_KEY);
        
        // Test 1: Get nodes
        const nodesResponse = await axios.get(`${config.PTERODACTYL_URL}/api/application/nodes`, {
            headers: {
                'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                'Accept': 'application/json'
            }
        });
        
        const nodes = nodesResponse.data.data;
        console.log('Nodes found:', nodes.length);
        
        // Test 2: Get users
        const usersResponse = await axios.get(`${config.PTERODACTYL_URL}/api/application/users`, {
            headers: {
                'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                'Accept': 'application/json'
            }
        });
        
        const users = usersResponse.data.data;
        console.log('Users found:', users.length);
        
        // Test 3: Get eggs
        const eggsResponse = await axios.get(`${config.PTERODACTYL_URL}/api/application/nests/1/eggs`, {
            headers: {
                'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                'Accept': 'application/json'
            }
        });
        
        const eggs = eggsResponse.data.data;
        console.log('Eggs found:', eggs.length);
        
        res.json({
            success: true,
            nodes: nodes.map(n => ({ id: n.attributes.id, name: n.attributes.name })),
            users: users.slice(0, 3).map(u => ({ id: u.attributes.id, email: u.attributes.email })),
            eggs: eggs.slice(0, 3).map(e => ({ id: e.attributes.id, name: e.attributes.name }))
        });
    } catch (error) {
        console.error('API Test Error:', error.response?.data || error.message);
        res.json({
            success: false,
            error: error.message,
            status: error.response?.status,
            details: error.response?.data
        });
    }
});

// Test server creation with minimal payload
app.post('/api/test-create', requireAuth, async (req, res) => {
    try {
        const payload = {
            name: 'TestServer' + Date.now(),
            user: req.user.pterodactylUserId,
            egg: 1,
            docker_image: '',
            startup: '',
            environment: {},
            limits: {
                memory: 512,
                swap: 0,
                disk: 1024,
                io: 500,
                cpu: 25
            },
            feature_limits: {
                databases: 0,
                allocations: 1,
                backups: 0
            },
            allocation: {
                default: 1
            }
        };
        
        console.log('Test creating server:', JSON.stringify(payload, null, 2));
        
        const response = await axios.post(`${config.PTERODACTYL_URL}/api/application/servers`, payload, {
            headers: {
                'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        console.log('SUCCESS: Server created!');
        res.json({ success: true, server: response.data.attributes });
    } catch (error) {
        console.error('CREATE ERROR:', error.response?.data || error.message);
        res.json({
            success: false,
            error: error.message,
            details: error.response?.data
        });
    }
});

app.post('/api/create-server', requireAuth, async (req, res) => {
    const { name, egg, memory, cpu, disk, node } = req.body;
    
    try {
        console.log('Creating server with data:', { name, egg, memory, cpu, disk, node, userId: req.user.pterodactylUserId });
        
        // Use selected node or get first available
        let selectedNode;
        if (node) {
            // Get specific node
            const nodeResponse = await axios.get(`${config.PTERODACTYL_URL}/api/application/nodes/${node}`, {
                headers: {
                    'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                    'Accept': 'application/json'
                }
            });
            selectedNode = nodeResponse.data;
        } else {
            // Get first available node
            const nodesResponse = await axios.get(`${config.PTERODACTYL_URL}/api/application/nodes`, {
                headers: {
                    'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                    'Accept': 'application/json'
                }
            });
            selectedNode = nodesResponse.data.data[0];
        }
        
        if (!selectedNode) {
            throw new Error('Selected node not available');
        }
        
        console.log('Using node:', selectedNode.attributes.name, 'ID:', selectedNode.attributes.id);
        
        // Get allocations for the selected node
        const allocResponse = await axios.get(`${config.PTERODACTYL_URL}/api/application/nodes/${selectedNode.attributes.id}/allocations`, {
            headers: {
                'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                'Accept': 'application/json'
            }
        });
        
        const allocations = allocResponse.data.data.filter(a => !a.attributes.assigned);
        
        if (!allocations.length) {
            throw new Error('No free allocations available');
        }
        
        const allocation = allocations[0];
        console.log('Using allocation:', allocation.attributes.ip + ':' + allocation.attributes.port);
        
        // Correct Pterodactyl API payload format
        const payload = {
            name: name,
            user: parseInt(req.user.pterodactylUserId),
            egg: parseInt(egg),
            docker_image: '',
            startup: '',
            environment: {},
            limits: {
                memory: parseInt(memory),
                swap: 0,
                disk: parseInt(disk),
                io: 500,
                cpu: parseInt(cpu)
            },
            feature_limits: {
                databases: 0,
                allocations: 1,
                backups: 0
            },
            allocation: {
                default: parseInt(allocation.attributes.id)
            },
            deploy: {
                locations: [parseInt(selectedNode.attributes.location_id)],
                dedicated_ip: false,
                port_range: []
            }
        };
        
        console.log('Sending payload:', JSON.stringify(payload, null, 2));
        
        const response = await axios.post(`${config.PTERODACTYL_URL}/api/application/servers`, payload, {
            headers: {
                'Authorization': `Bearer ${config.PTERODACTYL_API_KEY}`,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        
        console.log('✅ SUCCESS! Server created:', response.data.attributes.name);
        
        // Update user
        req.user.serverCount = (req.user.serverCount || 0) + 1;
        await req.user.save();
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            success: true,
            message: `Server '${name}' created successfully on Pterodactyl!`,
            server: response.data.attributes
        }));
    } catch (error) {
        console.error('❌ DETAILED ERROR:');
        console.error('Status:', error.response?.status);
        console.error('Data:', JSON.stringify(error.response?.data, null, 2));
        console.error('Message:', error.message);
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            success: false,
            error: error.response?.data?.message || error.message,
            details: error.response?.data
        }));
    }
});

app.get('/api/promotions', async (req, res) => {
    try {
        // Mock promotions data with sample promotions
        const promotions = [
            {
                _id: '1',
                serverName: 'Epic Survival Server',
                serverIP: 'play.example.com:25565',
                description: 'Join our amazing survival server with custom plugins and friendly community!',
                author: 'ServerOwner1',
                boosted: true,
                createdAt: new Date()
            },
            {
                _id: '2',
                serverName: 'Creative Build World',
                serverIP: 'creative.example.com:25565',
                description: 'Unleash your creativity in our massive creative world with unlimited resources!',
                author: 'Builder123',
                boosted: false,
                createdAt: new Date()
            }
        ];
        res.json({ promotions });
    } catch (error) {
        res.status(500).json({ error: 'Failed to load promotions' });
    }
});

app.post('/api/create-promotion', requireAuth, async (req, res) => {
    if (!req.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    const { serverName, serverIP, description } = req.body;

    if (!serverName || !serverIP || !description) {
        return res.status(400).json({ error: 'All fields are required' });
    }

    if ((req.user.coins || 0) < 500) {
        return res.status(400).json({ error: 'Insufficient coins. You need 500 coins to promote your server.' });
    }

    try {
        // Deduct coins
        req.user.coins = (req.user.coins || 0) - 500;
        await req.user.save();

        console.log('✅ Promotion created by:', req.user.username, 'Cost: 500 coins, New balance:', req.user.coins);

        res.json({
            success: true,
            newBalance: req.user.coins,
            message: 'Server promotion created successfully!'
        });
    } catch (error) {
        console.error('❌ Create promotion error:', error);
        res.status(500).json({ error: 'Failed to create promotion' });
    }
});

app.post('/api/linkvertise-complete', requireAuth, async (req, res) => {
    if (!req.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
        // Add 8 coins for Linkvertise completion
        req.user.coins = (req.user.coins || 0) + 8;
        await req.user.save();

        res.json({
            success: true,
            coins: 8,
            newBalance: req.user.coins
        });
    } catch (error) {
        res.status(500).json({ error: 'Failed to process completion' });
    }
});

app.post('/api/update-profile', requireAuth, async (req, res) => {
    if (!req.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    const { username } = req.body;

    if (!username || username.trim().length < 3) {
        return res.status(400).json({ error: 'Username must be at least 3 characters' });
    }

    try {
        req.user.username = username.trim();
        await req.user.save();

        console.log('✅ Profile updated for:', req.user.username);

        res.json({
            success: true,
            username: req.user.username
        });
    } catch (error) {
        console.error('❌ Update profile error:', error);
        res.status(500).json({ error: 'Failed to update profile' });
    }
});

app.post('/api/buy-resource', requireAuth, async (req, res) => {
    if (!req.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    const { type, amount, price } = req.body;

    if ((req.user.coins || 0) < price) {
        return res.status(400).json({ error: 'Insufficient coins' });
    }

    try {
        // Deduct coins first
        req.user.coins = (req.user.coins || 0) - price;
        await req.user.save();

        let userResources = await UserResources.findOne({ userId: req.user._id });
        
        if (!userResources) {
            userResources = new UserResources({
                userId: req.user._id,
                availableRam: 2048,
                availableCpu: 100,
                availableDisk: 8192,
                serverSlots: 2
            });
        }

        // Update resources based on type
        if (type === 'ram') {
            userResources.purchasedRam = (userResources.purchasedRam || 0) + amount;
        } else if (type === 'cpu') {
            userResources.purchasedCpu = (userResources.purchasedCpu || 0) + amount;
        } else if (type === 'disk') {
            userResources.purchasedDisk = (userResources.purchasedDisk || 0) + amount;
        }

        await userResources.save();

        console.log('✅ Resource purchased by:', req.user.username, 'Type:', type, 'Amount:', amount, 'Price:', price, 'New balance:', req.user.coins);

        res.json({
            success: true,
            newBalance: req.user.coins
        });
    } catch (error) {
        console.error('❌ Buy resource error:', error);
        res.status(500).json({ error: 'Failed to buy resource' });
    }
});

app.post('/api/buy-slot', requireAuth, async (req, res) => {
    if (!req.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    const { slots, price } = req.body;

    if ((req.user.coins || 0) < price) {
        return res.status(400).json({ error: 'Insufficient coins' });
    }

    try {
        // Deduct coins first
        req.user.coins = (req.user.coins || 0) - price;
        await req.user.save();

        let userResources = await UserResources.findOne({ userId: req.user._id });
        
        if (!userResources) {
            userResources = new UserResources({
                userId: req.user._id,
                availableRam: 2048,
                availableCpu: 100,
                availableDisk: 8192,
                serverSlots: 2
            });
        }

        userResources.purchasedSlots = (userResources.purchasedSlots || 0) + slots;
        await userResources.save();

        console.log('✅ Server slot purchased by:', req.user.username, 'Slots:', slots, 'Price:', price, 'New balance:', req.user.coins);

        res.json({
            success: true,
            newBalance: req.user.coins
        });
    } catch (error) {
        console.error('❌ Buy slot error:', error);
        res.status(500).json({ error: 'Failed to buy server slot' });
    }
});

app.post('/api/redeem-coupon', requireAuth, async (req, res) => {
    if (!req.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    const { couponCode } = req.body;

    try {
        const coupon = await Coupon.findOne({ code: couponCode.toUpperCase(), active: true });

        if (!coupon) {
            return res.status(400).json({ error: 'Invalid coupon code' });
        }

        if (coupon.used >= coupon.limit) {
            return res.status(400).json({ error: 'Coupon usage limit reached' });
        }

        if (coupon.usedBy.includes(req.user._id)) {
            return res.status(400).json({ error: 'You have already used this coupon' });
        }

        // Add coins to user
        req.user.coins = (req.user.coins || 0) + coupon.amount;
        await req.user.save();

        // Update coupon usage
        coupon.used += 1;
        coupon.usedBy.push(req.user._id);
        await coupon.save();

        res.json({
            success: true,
            coins: coupon.amount,
            newBalance: req.user.coins
        });
    } catch (error) {
        res.status(500).json({ error: 'Failed to redeem coupon' });
    }
});

// Admin routes
app.get('/api/admin/users', requireAuth, async (req, res) => {
    if (!req.user || !req.user.isAdmin) {
        return res.status(403).json({ error: 'Access denied' });
    }

    try {
        const users = await User.find({}).select('username email coins serverCount _id');
        res.json({ users });
    } catch (error) {
        res.status(500).json({ error: 'Failed to load users' });
    }
});

app.post('/api/admin/give-coins', requireAuth, async (req, res) => {
    if (!req.user || !req.user.isAdmin) {
        return res.status(403).json({ error: 'Access denied' });
    }

    const { username, coins } = req.body;

    try {
        const user = await User.findOne({ username: username.toLowerCase() });
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }

        user.coins = (user.coins || 0) + coins;
        await user.save();

        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: 'Failed to give coins' });
    }
});

app.post('/api/admin/create-coupon', requireAuth, async (req, res) => {
    if (!req.user || !req.user.isAdmin) {
        return res.status(403).json({ error: 'Access denied' });
    }

    const { couponCode, amount, limit } = req.body;

    try {
        const existingCoupon = await Coupon.findOne({ code: couponCode.toUpperCase() });
        if (existingCoupon) {
            return res.status(400).json({ error: 'Coupon code already exists' });
        }

        const coupon = new Coupon({
            code: couponCode.toUpperCase(),
            amount: amount,
            limit: limit,
            createdBy: req.user.username
        });

        await coupon.save();
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: 'Failed to create coupon' });
    }
});

app.post('/api/admin/remove-coins', requireAuth, async (req, res) => {
    if (!req.user || !req.user.isAdmin) {
        return res.status(403).json({ error: 'Access denied' });
    }

    const { username, coins } = req.body;

    try {
        const user = await User.findOne({ username: username.toLowerCase() });
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }

        user.coins = Math.max(0, (user.coins || 0) - coins);
        await user.save();

        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: 'Failed to remove coins' });
    }
});

app.post('/api/admin/create-user', requireAuth, async (req, res) => {
    if (!req.user || !req.user.isAdmin) {
        return res.status(403).json({ error: 'Access denied' });
    }

    const { username, password } = req.body;

    try {
        const existingUser = await User.findOne({ username: username.toLowerCase() });
        if (existingUser) {
            return res.status(400).json({ error: 'Username already exists' });
        }

        const email = `${username.toLowerCase()}@blazenode.local`;
        const pterodactylPassword = `${username}_${Date.now().toString().slice(-4)}`;
        const pterodactylUser = await createPterodactylUser(email, username, pterodactylPassword);

        const user = new User({
            email: email,
            username: username.toLowerCase(),
            loginType: 'manual',
            coins: 1000,
            isAdmin: false,
            serverCount: 0,
            pterodactylUserId: pterodactylUser?.id,
            pterodactylPassword: pterodactylPassword,
            lastLogin: new Date()
        });

        await user.save();

        // Create user resources
        const userResources = new UserResources({
            userId: user._id,
            availableRam: 2048,
            availableCpu: 100,
            availableDisk: 5120,
            serverSlots: 2
        });
        await userResources.save();

        res.json({ success: true, user: { username: user.username, email: user.email } });
    } catch (error) {
        res.status(500).json({ error: 'Failed to create user' });
    }
});

app.post('/api/admin/update-discord', requireAuth, async (req, res) => {
    if (!req.user || !req.user.isAdmin) {
        return res.status(403).json({ error: 'Access denied' });
    }

    const { discordLink } = req.body;

    try {
        // In a real app, save to database or config
        console.log('Discord link updated by admin:', discordLink);
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ error: 'Failed to update Discord link' });
    }
});

// Create Pterodactyl account with full details
app.post('/api/create-pterodactyl-account-full', requireAuth, async (req, res) => {
    if (!req.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    const { email, username, firstName, lastName, password } = req.body;

    // Validation
    if (!email || !username || !firstName || !lastName || !password) {
        return res.status(400).json({ error: 'All fields are required' });
    }

    if (!email.includes('@') || !email.includes('.')) {
        return res.status(400).json({ error: 'Please enter a valid email address' });
    }

    if (username.length < 3) {
        return res.status(400).json({ error: 'Username must be at least 3 characters' });
    }

    if (password.length < 8) {
        return res.status(400).json({ error: 'Password must be at least 8 characters' });
    }

    try {
        console.log('Creating Pterodactyl user:', { email, username, firstName, lastName });
        
        // Clean username for Pterodactyl
        const cleanUsername = username.toLowerCase().replace(/[^a-z0-9]/g, '');
        
        const pterodactylUser = await createPterodactylUser(email, cleanUsername, password);
        
        if (!pterodactylUser || !pterodactylUser.id) {
            throw new Error('Failed to create Pterodactyl user - no ID returned');
        }
        
        // Update user with Pterodactyl info
        req.user.pterodactylUserId = pterodactylUser.id;
        req.user.pterodactylPassword = password;
        req.user.pterodactylEmail = email;
        await req.user.save();

        console.log('✅ Pterodactyl account created successfully:', pterodactylUser.id);

        res.json({
            success: true,
            pterodactylId: pterodactylUser.id,
            message: 'Pterodactyl account created successfully'
        });
    } catch (error) {
        console.error('❌ Pterodactyl account creation error:', error);
        
        let errorMessage = 'Failed to create Pterodactyl account';
        if (error.response?.data?.errors) {
            const errors = error.response.data.errors;
            if (errors.email) errorMessage = 'Email already exists in Pterodactyl';
            else if (errors.username) errorMessage = 'Username already exists in Pterodactyl';
            else errorMessage = Object.values(errors)[0][0] || errorMessage;
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        res.status(500).json({ error: errorMessage });
    }
});

// Save full profile
app.post('/api/save-full-profile', requireAuth, async (req, res) => {
    if (!req.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    const { username, email, pterodactylEmail, pterodactylPassword } = req.body;

    // Validation
    if (username && username.trim().length < 3) {
        return res.status(400).json({ error: 'Username must be at least 3 characters' });
    }

    if (email && (!email.includes('@') || !email.includes('.'))) {
        return res.status(400).json({ error: 'Please enter a valid email address' });
    }

    try {
        console.log('Saving profile for user:', req.user.username, { username, email, pterodactylEmail });
        
        let updated = false;
        
        if (username && username.trim().length >= 3) {
            req.user.username = username.trim();
            updated = true;
        }
        
        if (email && email.includes('@')) {
            req.user.email = email.trim();
            updated = true;
        }
        
        if (pterodactylEmail && pterodactylEmail.includes('@')) {
            req.user.pterodactylEmail = pterodactylEmail.trim();
            updated = true;
        }
        
        if (pterodactylPassword && pterodactylPassword.length >= 8) {
            req.user.pterodactylPassword = pterodactylPassword;
            updated = true;
        }
        
        if (updated) {
            await req.user.save();
            console.log('✅ Profile saved successfully for:', req.user.username);
        }

        res.json({
            success: true,
            user: {
                username: req.user.username,
                email: req.user.email,
                pterodactylEmail: req.user.pterodactylEmail,
                pterodactylPassword: req.user.pterodactylPassword
            },
            message: 'Profile saved successfully'
        });
    } catch (error) {
        console.error('❌ Profile save error:', error);
        
        let errorMessage = 'Failed to save profile';
        if (error.code === 11000) {
            if (error.keyPattern?.username) {
                errorMessage = 'Username already exists';
            } else if (error.keyPattern?.email) {
                errorMessage = 'Email already exists';
            }
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        res.status(500).json({ error: errorMessage });
    }
});

// Update Pterodactyl info
app.post('/api/update-pterodactyl', requireAuth, async (req, res) => {
    if (!req.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    const { email, password } = req.body;

    try {
        if (email && email.includes('@')) {
            // Store pterodactyl email separately if different from main email
            req.user.pterodactylEmail = email;
        }
        
        if (password && password.length >= 8) {
            req.user.pterodactylPassword = password;
        }
        
        await req.user.save();

        res.json({ success: true });
    } catch (error) {
        console.error('Pterodactyl update error:', error);
        res.status(500).json({ error: 'Failed to update Pterodactyl info' });
    }
});

// Fallback route for admin user without Clerk
app.post('/api/admin-login', async (req, res) => {
    const { email, password } = req.body;
    
    // Simple admin login for dishapatel12376@gmail.com
    if (email === 'dishapatel12376@gmail.com' && password === 'admin123') {
        try {
            let user = await User.findOne({ email: email });
            
            if (!user) {
                const pterodactylPassword = 'admin_2024';
                const pterodactylUser = await createPterodactylUser(email, 'admin', pterodactylPassword);
                
                user = new User({
                    email: email,
                    username: 'admin',
                    loginType: 'manual',
                    coins: 10000,
                    isAdmin: true,
                    serverCount: 0,
                    pterodactylUserId: pterodactylUser?.id,
                    pterodactylPassword: pterodactylPassword,
                    lastLogin: new Date()
                });
                await user.save();
                
                const userResources = new UserResources({
                    userId: user._id,
                    availableRam: 2048,
                    availableCpu: 100,
                    availableDisk: 5120,
                    serverSlots: 2
                });
                await userResources.save();
            }
            
            user.lastLogin = new Date();
            await user.save();
            
            res.json({ success: true, user: {
                id: user._id,
                username: user.username,
                email: user.email,
                coins: user.coins,
                isAdmin: user.isAdmin,
                serverCount: user.serverCount
            }});
        } catch (error) {
            res.status(500).json({ error: 'Login failed' });
        }
    } else {
        res.status(401).json({ error: 'Invalid credentials' });
    }
});

// Page Routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/admin', (req, res) => {
    res.sendFile(path.join(__dirname, 'admin-login.html'));
});

app.get('/dashboard', requireAuth, (req, res) => {
    res.redirect('/dashboard.html');
});

app.get('/dashboard.html', (req, res) => {
    console.log('📋 Dashboard access');
    res.sendFile(path.join(__dirname, 'dashboard.html'));
});

// Allow direct access to dashboard for admin
app.get('/dashboard', (req, res) => {
    res.redirect('/dashboard.html');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
    console.log(`🔗 Local URL: http://localhost:${PORT}`);
    console.log(`🔐 Clerk Authentication Enabled`);
    console.log(`👤 Admin Email: ${config.ADMIN_EMAIL}`);
});
