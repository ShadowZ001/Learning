const express = require('express');
const session = require('express-session');
const cors = require('cors');
const mongoose = require('mongoose');
const path = require('path');
const passport = require('passport');
const DiscordStrategy = require('passport-discord').Strategy;
const config = require('./config');

const User = require('./models/User');

const app = express();

console.log('🚀 Starting BlazeNode Dashboard Server...');

// Force production environment
process.env.NODE_ENV = 'production';

// MongoDB connection with retry
async function connectMongoDB() {
    try {
        await mongoose.connect(config.MONGODB_URI, {
            serverSelectionTimeoutMS: 30000,
            socketTimeoutMS: 45000,
            maxPoolSize: 10,
            retryWrites: true
        });
        console.log('✅ MongoDB connected');
        return true;
    } catch (error) {
        console.error('❌ MongoDB failed:', error.message);
        return false;
    }
}

connectMongoDB();

// Create admin user - PRODUCTION READY
async function createAdminUser() {
    try {
        await new Promise(resolve => setTimeout(resolve, 3000)); // Wait for DB
        
        const adminExists = await User.findOne({ username: 'dev_shadowz' });
        if (!adminExists) {
            const admin = new User({
                username: 'dev_shadowz',
                password: 'shadowz',
                email: 'admin@blazenode.site',
                loginType: 'local',
                isAdmin: true,
                coins: 10000,
                serverCount: 0,
                createdAt: new Date()
            });
            await admin.save();
            console.log('✅ Admin user created: dev_shadowz / shadowz');
        } else {
            console.log('✅ Admin user exists');
        }
    } catch (error) {
        console.error('❌ Admin creation error:', error.message);
        // Retry admin creation
        setTimeout(createAdminUser, 5000);
    }
}

// Middleware
app.use(cors({
    origin: ['https://dash.blazenode.site', 'http://localhost:3000'],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
}));

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(express.static('.'));

app.use(session({
    secret: config.SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    name: 'blazenode.sid',
    cookie: { 
        secure: false, // Set to true in production with HTTPS
        httpOnly: true,
        maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
        sameSite: 'lax'
    }
}));

app.use(passport.initialize());
app.use(passport.session());

// Authentication check
app.use((req, res, next) => {
    req.isAuthenticated = () => {
        return req.session?.authenticated && req.session?.user?.id;
    };
    next();
});

// Discord Strategy - PRODUCTION FIXED
passport.use(new DiscordStrategy({
    clientID: config.DISCORD_CLIENT_ID,
    clientSecret: config.DISCORD_CLIENT_SECRET,
    callbackURL: config.DISCORD_REDIRECT_URI,
    scope: ['identify', 'email']
}, async (accessToken, refreshToken, profile, done) => {
    try {
        console.log('🔐 Discord OAuth for:', profile.username, profile.id);
        
        // Ensure DB connection
        let retries = 3;
        while (mongoose.connection.readyState !== 1 && retries > 0) {
            console.log('⚠️ Reconnecting to MongoDB...');
            await connectMongoDB();
            retries--;
            if (retries > 0) await new Promise(r => setTimeout(r, 1000));
        }
        
        if (mongoose.connection.readyState !== 1) {
            console.error('❌ Database unavailable');
            return done(new Error('Database connection failed'), null);
        }
        
        let user = await User.findOne({ discordId: profile.id });
        
        if (user) {
            user.discordUsername = profile.username;
            user.discordAvatar = profile.avatar;
            user.email = profile.email || user.email;
            user.lastLogin = new Date();
        } else {
            user = new User({
                discordId: profile.id,
                discordUsername: profile.username,
                discordAvatar: profile.avatar,
                email: profile.email || `${profile.username}@discord.user`,
                username: profile.username,
                loginType: 'discord',
                coins: 1000,
                isAdmin: profile.email === config.ADMIN_EMAIL,
                serverCount: 0,
                lastLogin: new Date(),
                createdAt: new Date()
            });
        }
        
        await user.save();
        console.log('✅ Discord user saved:', user.discordUsername);
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

// Initialize admin user
createAdminUser();

// Auth Routes
app.get('/auth/discord', (req, res, next) => {
    console.log('🔐 Discord OAuth initiated');
    passport.authenticate('discord')(req, res, next);
});

app.get('/auth/callback', (req, res, next) => {
    console.log('🔄 Discord callback received');
    
    passport.authenticate('discord', (err, user, info) => {
        if (err) {
            console.error('❌ Discord auth error:', err.message);
            return res.redirect('/?error=discord_failed&message=' + encodeURIComponent('Discord authentication failed. Please try again.'));
        }
        
        if (!user) {
            console.error('❌ No user from Discord');
            return res.redirect('/?error=no_user&message=' + encodeURIComponent('No user data received from Discord.'));
        }
        
        req.logIn(user, (loginErr) => {
            if (loginErr) {
                console.error('❌ Login error:', loginErr);
                return res.redirect('/?error=login_failed&message=' + encodeURIComponent('Login process failed.'));
            }
            
            // Create session
            req.session.authenticated = true;
            req.session.user = {
                id: user._id.toString(),
                username: user.discordUsername || user.username,
                email: user.email,
                discordId: user.discordId,
                coins: user.coins || 1000,
                isAdmin: user.isAdmin || false,
                serverCount: user.serverCount || 0,
                loginType: 'discord'
            };
            
            console.log('✅ Discord login successful for:', req.session.user.username);
            
            // Save session before redirect
            req.session.save((saveErr) => {
                if (saveErr) {
                    console.error('❌ Session save error:', saveErr);
                    return res.redirect('/?error=session_failed');
                }
                return res.redirect('/dashboard');
            });
        });
    })(req, res, next);
});

// Username/Password login - PRODUCTION FIXED
app.post('/auth/login', async (req, res) => {
    const { username, password } = req.body;
    
    console.log('🔐 Local login attempt:', username);
    
    try {
        // Ensure DB connection
        if (mongoose.connection.readyState !== 1) {
            console.log('⚠️ Database not connected, attempting reconnection...');
            await connectMongoDB();
        }
        
        if (mongoose.connection.readyState !== 1) {
            console.error('❌ Database connection failed');
            return res.status(500).json({ error: 'Database connection failed' });
        }
        
        // Find user with multiple methods
        let user = await User.findOne({ username: username });
        if (!user) {
            user = await User.findOne({ username: username.toLowerCase() });
        }
        if (!user) {
            user = await User.findOne({ username: { $regex: new RegExp(`^${username}$`, 'i') } });
        }
        
        console.log('User lookup result:', {
            found: !!user,
            username: user?.username,
            hasPassword: !!user?.password,
            loginType: user?.loginType,
            isAdmin: user?.isAdmin
        });
        
        if (!user) {
            console.log('❌ User not found:', username);
            return res.status(401).json({ error: 'Invalid username or password' });
        }
        
        if (!user.password || user.password !== password) {
            console.log('❌ Invalid password for:', username);
            return res.status(401).json({ error: 'Invalid username or password' });
        }
        
        console.log('✅ Local login success:', username);
        
        // Update last login
        user.lastLogin = new Date();
        await user.save();
        
        // Create session
        req.session.authenticated = true;
        req.session.user = {
            id: user._id.toString(),
            username: user.username,
            email: user.email,
            coins: user.coins || 1000,
            isAdmin: user.isAdmin || false,
            serverCount: user.serverCount || 0,
            loginType: 'local'
        };
        
        console.log('✅ Session created for local user:', username);
        
        // Save session before responding
        req.session.save((saveErr) => {
            if (saveErr) {
                console.error('❌ Session save error:', saveErr);
                return res.status(500).json({ error: 'Session save failed' });
            }
            
            res.json({ 
                success: true, 
                message: 'Login successful',
                redirect: '/dashboard'
            });
        });
        
    } catch (error) {
        console.error('❌ Local login error:', error);
        res.status(500).json({ error: 'Login failed: ' + error.message });
    }
});

// Admin user creation
app.post('/api/admin/create-user', async (req, res) => {
    if (!req.session?.user?.username || req.session.user.username !== 'dev_shadowz') {
        return res.status(403).json({ error: 'Access denied - Admin only' });
    }
    
    const { username, password } = req.body;
    
    if (!username || !password) {
        return res.status(400).json({ error: 'Username and password required' });
    }
    
    try {
        const existingUser = await User.findOne({ username: username.toLowerCase() });
        if (existingUser) {
            return res.status(400).json({ error: 'Username already exists' });
        }
        
        const newUser = new User({
            username: username.toLowerCase(),
            password: password,
            email: `${username.toLowerCase()}@blazenode.local`,
            loginType: 'local',
            coins: 1000,
            isAdmin: false,
            serverCount: 0,
            createdAt: new Date()
        });
        
        await newUser.save();
        console.log('✅ New user created by admin:', username);
        
        res.json({ 
            success: true, 
            message: `User '${username}' created successfully`,
            username: username
        });
        
    } catch (error) {
        console.error('❌ User creation error:', error);
        res.status(500).json({ error: 'Failed to create user' });
    }
});

// API Routes
app.get('/api/user', async (req, res) => {
    if (!req.session?.user?.id) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    try {
        const user = await User.findById(req.session.user.id);
        if (!user) {
            req.session.destroy(() => {});
            return res.status(401).json({ error: 'User not found' });
        }
        
        res.json({
            id: user._id,
            username: user.discordUsername || user.username,
            email: user.email,
            discordId: user.discordId,
            coins: user.coins,
            isAdmin: user.isAdmin || false,
            serverCount: user.serverCount || 0,
            loginType: user.loginType || 'discord'
        });
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
            .select('discordUsername username coins');
        
        res.json({ 
            users: users.map(u => ({ 
                username: u.discordUsername || u.username, 
                coins: u.coins || 0 
            }))
        });
    } catch (error) {
        res.status(500).json({ error: 'Failed to load leaderboard' });
    }
});

app.post('/api/afk-earn', async (req, res) => {
    if (!req.isAuthenticated()) {
        return res.status(401).json({ error: 'Not authenticated' });
    }

    try {
        const user = await User.findById(req.session.user.id);
        if (!user) {
            return res.status(404).json({ error: 'User not found' });
        }

        user.coins = (user.coins || 0) + 1.2;
        await user.save();
        req.session.user.coins = user.coins;

        res.json({
            success: true,
            coins: 1.2,
            newBalance: user.coins
        });
    } catch (error) {
        res.status(500).json({ error: 'Failed to earn coins' });
    }
});

app.post('/api/logout', (req, res) => {
    const username = req.session?.user?.username || 'unknown';
    req.session.destroy((err) => {
        if (err) {
            return res.status(500).json({ error: 'Logout failed' });
        }
        console.log('🚪 Logout:', username);
        res.json({ success: true });
    });
});

// Page Routes
app.get('/', (req, res) => {
    if (req.session?.user?.id) {
        return res.redirect('/dashboard');
    }
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/dashboard', (req, res) => {
    if (!req.isAuthenticated()) {
        return res.redirect('/?error=not_logged_in');
    }
    res.redirect('/dashboard.html');
});

app.get('/dashboard.html', (req, res) => {
    if (!req.isAuthenticated()) {
        return res.redirect('/?error=not_logged_in');
    }
    console.log('📋 Dashboard for:', req.session.user.username);
    res.sendFile(path.join(__dirname, 'dashboard.html'));
});

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'OK',
        timestamp: new Date().toISOString(),
        mongodb: mongoose.connection.readyState === 1 ? 'Connected' : 'Disconnected',
        environment: process.env.NODE_ENV
    });
});

module.exports = app;

if (require.main === module) {
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log(`🚀 Server running on port ${PORT}`);
        console.log(`🔗 Production URL: https://dash.blazenode.site`);
        console.log(`🔐 Discord OAuth: ${config.DISCORD_REDIRECT_URI}`);
        console.log(`👤 Admin: dev_shadowz / shadowz`);
        console.log(`🎮 Both login methods available`);
        console.log(`🌍 Environment: ${process.env.NODE_ENV}`);
    });
}