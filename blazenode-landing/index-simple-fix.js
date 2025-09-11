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

// Simple MongoDB connection
mongoose.connect(config.MONGODB_URI)
    .then(() => console.log('✅ MongoDB connected'))
    .catch(err => console.error('❌ MongoDB error:', err.message));

// Create admin user - SIMPLE
async function createAdminUser() {
    try {
        await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
        
        const adminExists = await User.findOne({ username: 'dev_shadowz' });
        if (!adminExists) {
            const admin = new User({
                username: 'dev_shadowz',
                password: 'shadowz',
                email: 'admin@blazenode.site',
                loginType: 'local',
                isAdmin: true,
                coins: 10000,
                serverCount: 0
            });
            await admin.save();
            console.log('✅ Admin user created: dev_shadowz / shadowz');
        } else {
            console.log('✅ Admin user exists');
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

// Discord Strategy
passport.use(new DiscordStrategy({
    clientID: config.DISCORD_CLIENT_ID,
    clientSecret: config.DISCORD_CLIENT_SECRET,
    callbackURL: config.DISCORD_REDIRECT_URI,
    scope: ['identify', 'email']
}, async (accessToken, refreshToken, profile, done) => {
    try {
        console.log('🔐 Discord OAuth for:', profile.username);
        
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
                lastLogin: new Date()
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
            return res.redirect('/?error=discord_failed&message=' + encodeURIComponent('Discord authentication failed'));
        }
        
        if (!user) {
            console.error('❌ No user from Discord');
            return res.redirect('/?error=no_user&message=' + encodeURIComponent('No user data received'));
        }
        
        req.logIn(user, (loginErr) => {
            if (loginErr) {
                console.error('❌ Login error:', loginErr);
                return res.redirect('/?error=login_failed&message=' + encodeURIComponent('Login process failed'));
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
            return res.redirect('/dashboard');
        });
    })(req, res, next);
});

// Username/Password login - SIMPLIFIED
app.post('/auth/login', async (req, res) => {
    const { username, password } = req.body;
    
    console.log('🔐 Local login attempt:', username);
    
    try {
        // Simple user lookup
        const user = await User.findOne({ username: username });
        
        console.log('User lookup result:', {
            found: !!user,
            username: user?.username,
            hasPassword: !!user?.password,
            isAdmin: user?.isAdmin
        });
        
        if (!user || user.password !== password) {
            console.log('❌ Invalid credentials for:', username);
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
        
        res.json({ 
            success: true, 
            message: 'Login successful',
            redirect: '/dashboard'
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
            serverCount: 0
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

module.exports = app;

if (require.main === module) {
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log(`🚀 Server running on port ${PORT}`);
        console.log(`🔗 Production URL: https://dash.blazenode.site`);
        console.log(`🔐 Discord OAuth: ${config.DISCORD_REDIRECT_URI}`);
        console.log(`👤 Admin: dev_shadowz / shadowz`);
        console.log(`🎮 Both login methods available`);
    });
}