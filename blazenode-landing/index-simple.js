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

// MongoDB connection
async function connectMongoDB() {
    try {
        await mongoose.connect(config.MONGODB_URI);
        console.log('✅ MongoDB connected');
        return true;
    } catch (error) {
        console.error('❌ MongoDB failed:', error.message);
        return false;
    }
}

connectMongoDB();

// Create admin user
async function createAdminUser() {
    try {
        const adminExists = await User.findOne({ username: 'dev_shadowz' });
        if (!adminExists) {
            const admin = new User({
                username: 'dev_shadowz',
                password: 'shadowz', // Plain text for simplicity
                email: 'admin@blazenode.site',
                loginType: 'local',
                isAdmin: true,
                coins: 10000,
                serverCount: 0
            });
            await admin.save();
            console.log('✅ Admin user created: dev_shadowz / shadowz');
        }
    } catch (error) {
        console.error('❌ Admin creation failed:', error.message);
    }
}

// Middleware
app.use(cors({
    origin: true,
    credentials: true
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('.'));

app.use(session({
    secret: config.SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    cookie: { 
        secure: false,
        httpOnly: true,
        maxAge: 24 * 60 * 60 * 1000
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

// Discord Strategy - FIXED WITH DETAILED LOGGING
passport.use(new DiscordStrategy({
    clientID: config.DISCORD_CLIENT_ID,
    clientSecret: config.DISCORD_CLIENT_SECRET,
    callbackURL: config.DISCORD_REDIRECT_URI,
    scope: ['identify', 'email']
}, async (accessToken, refreshToken, profile, done) => {
    try {
        console.log('🔐 Discord OAuth callback received');
        console.log('👤 Profile ID:', profile.id);
        console.log('👤 Profile Username:', profile.username);
        console.log('📧 Profile Email:', profile.email);
        console.log('🔗 Using callback URL:', config.DISCORD_REDIRECT_URI);
        
        // Check database connection
        if (mongoose.connection.readyState !== 1) {
            console.log('⚠️ Database not connected, attempting reconnection...');
            await connectMongoDB();
        }
        
        if (mongoose.connection.readyState !== 1) {
            console.error('❌ Database connection failed during OAuth');
            return done(new Error('Database connection failed'), null);
        }
        
        console.log('✅ Database connected, proceeding with user lookup');
        
        let user = await User.findOne({ discordId: profile.id });
        
        if (user) {
            console.log('📝 Found existing user:', user.discordUsername);
            user.discordUsername = profile.username;
            user.discordAvatar = profile.avatar;
            user.email = profile.email || user.email;
            user.lastLogin = new Date();
        } else {
            console.log('🆕 Creating new user for:', profile.username);
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
        
        const savedUser = await user.save();
        console.log('✅ User saved successfully:', savedUser.discordUsername, savedUser._id);
        console.log('🎯 Returning user to callback');
        return done(null, savedUser);
        
    } catch (error) {
        console.error('❌ Discord OAuth Strategy Error:');
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
        return done(error, null);
    }
}));

passport.serializeUser((user, done) => {
    console.log('🔄 Serializing user:', user._id);
    done(null, user._id);
});

passport.deserializeUser(async (id, done) => {
    try {
        console.log('🔄 Deserializing user:', id);
        const user = await User.findById(id);
        done(null, user);
    } catch (error) {
        console.error('❌ Deserialize error:', error);
        done(error, null);
    }
});

// Initialize admin user after delay
setTimeout(createAdminUser, 3000);

// Auth Routes
app.get('/auth/discord', (req, res, next) => {
    console.log('🔐 Discord OAuth initiated');
    console.log('🔗 Client ID:', config.DISCORD_CLIENT_ID);
    console.log('🔗 Redirect URI:', config.DISCORD_REDIRECT_URI);
    passport.authenticate('discord')(req, res, next);
});

app.get('/auth/callback', (req, res, next) => {
    console.log('🔄 Discord callback route hit');
    console.log('📝 Query params:', req.query);
    
    passport.authenticate('discord', (err, user, info) => {
        console.log('🔄 Passport authenticate callback');
        console.log('❓ Error:', err);
        console.log('👤 User:', user ? user._id : 'null');
        console.log('ℹ️ Info:', info);
        
        if (err) {
            console.error('❌ Discord authentication error:', err.message);
            return res.redirect('/?error=discord_auth_failed&message=' + encodeURIComponent(err.message));
        }
        
        if (!user) {
            console.error('❌ No user returned from Discord');
            return res.redirect('/?error=discord_no_user&message=' + encodeURIComponent('Discord authentication failed - no user data'));
        }
        
        console.log('✅ User received, attempting login');
        
        req.logIn(user, (loginErr) => {
            if (loginErr) {
                console.error('❌ req.logIn error:', loginErr);
                return res.redirect('/?error=login_failed&message=' + encodeURIComponent('Login process failed'));
            }
            
            console.log('✅ req.logIn successful');
            
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
            
            console.log('✅ Session created for:', req.session.user.username);
            console.log('🔄 Redirecting to dashboard...');
            
            return res.redirect('/dashboard');
        });
    })(req, res, next);
});

// Simple local login
app.post('/auth/login', async (req, res) => {
    const { username, password } = req.body;
    
    console.log('🔐 Local login attempt:', username);
    
    try {
        const user = await User.findOne({ 
            username: username.toLowerCase(),
            loginType: 'local'
        });
        
        if (!user || user.password !== password) {
            console.log('❌ Invalid credentials for:', username);
            return res.status(401).json({ error: 'Invalid credentials' });
        }
        
        console.log('✅ Local login success:', username);
        
        // Create session
        req.session.authenticated = true;
        req.session.user = {
            id: user._id.toString(),
            username: user.username,
            email: user.email,
            coins: user.coins || 0,
            isAdmin: user.isAdmin || false,
            serverCount: user.serverCount || 0,
            loginType: 'local'
        };
        
        res.json({ 
            success: true, 
            user: req.session.user,
            redirect: '/dashboard'
        });
        
    } catch (error) {
        console.error('❌ Local login error:', error);
        res.status(500).json({ error: 'Login failed' });
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
        console.log('🔄 Already logged in, redirecting to dashboard');
        return res.redirect('/dashboard');
    }
    console.log('🏠 Serving login page');
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/dashboard', (req, res) => {
    if (!req.isAuthenticated()) {
        console.log('❌ Not authenticated, redirecting to login');
        return res.redirect('/?error=not_logged_in');
    }
    console.log('🔄 Redirecting to dashboard.html');
    res.redirect('/dashboard.html');
});

app.get('/dashboard.html', (req, res) => {
    if (!req.isAuthenticated()) {
        console.log('❌ Not authenticated for dashboard.html');
        return res.redirect('/?error=not_logged_in');
    }
    console.log('📋 Serving dashboard for:', req.session.user.username);
    res.sendFile(path.join(__dirname, 'dashboard.html'));
});

// Debug route
app.get('/debug', (req, res) => {
    res.json({
        session: req.session,
        authenticated: req.isAuthenticated(),
        mongoState: mongoose.connection.readyState,
        config: {
            clientId: config.DISCORD_CLIENT_ID,
            redirectUri: config.DISCORD_REDIRECT_URI
        }
    });
});

module.exports = app;

if (require.main === module) {
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log(`🚀 Server running on port ${PORT}`);
        console.log(`🔗 URL: https://dash.blazenode.site`);
        console.log(`🔐 Discord OAuth: ${config.DISCORD_REDIRECT_URI}`);
        console.log(`👤 Admin Login: dev_shadowz / shadowz`);
        console.log(`🎮 Discord Login: Available`);
    });
}