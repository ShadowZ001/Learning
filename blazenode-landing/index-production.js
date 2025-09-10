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

// MongoDB connection with retry logic
async function connectMongoDB() {
    try {
        await mongoose.connect(config.MONGODB_URI, {
            serverSelectionTimeoutMS: 30000,
            socketTimeoutMS: 45000,
            maxPoolSize: 10
        });
        console.log('✅ MongoDB connected');
        return true;
    } catch (error) {
        console.error('❌ MongoDB connection failed:', error.message);
        return false;
    }
}

connectMongoDB();

// CORS and middleware
app.use(cors({
    origin: true,
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept']
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

// Authentication middleware
app.use((req, res, next) => {
    req.isAuthenticated = () => {
        return req.session?.authenticated && req.session?.user?.id;
    };
    next();
});

// Passport setup
app.use(passport.initialize());
app.use(passport.session());

// Discord Strategy - FIXED
passport.use(new DiscordStrategy({
    clientID: config.DISCORD_CLIENT_ID,
    clientSecret: config.DISCORD_CLIENT_SECRET,
    callbackURL: config.DISCORD_REDIRECT_URI,
    scope: ['identify', 'email']
}, async (accessToken, refreshToken, profile, done) => {
    try {
        console.log('🔐 Discord auth for:', profile.username);
        
        // Ensure DB connection
        if (mongoose.connection.readyState !== 1) {
            await connectMongoDB();
        }
        
        if (mongoose.connection.readyState !== 1) {
            console.error('❌ Database not available');
            return done(null, false);
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
                lastLogin: new Date()
            });
        }
        
        await user.save();
        console.log('✅ User saved:', user.discordUsername);
        return done(null, user);
        
    } catch (error) {
        console.error('❌ OAuth error:', error.message);
        return done(null, false);
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

// Routes
app.get('/auth/discord', passport.authenticate('discord'));

app.get('/auth/callback', (req, res, next) => {
    passport.authenticate('discord', (err, user, info) => {
        if (err) {
            console.error('Auth error:', err);
            return res.redirect('/?error=auth_failed');
        }
        if (!user) {
            console.error('No user returned:', info);
            return res.redirect('/?error=no_user');
        }
        
        req.logIn(user, (loginErr) => {
            if (loginErr) {
                console.error('Login error:', loginErr);
                return res.redirect('/?error=login_failed');
            }
            
            console.log('✅ User logged in:', user._id);
            
            // Create session
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
            
            console.log('🔄 Redirecting to dashboard...');
            return res.redirect('/dashboard');
        });
    })(req, res, next);
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
            username: user.discordUsername,
            email: user.email,
            discordId: user.discordId,
            coins: user.coins,
            isAdmin: user.isAdmin || false,
            serverCount: user.serverCount || 0,
            loginType: 'discord'
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
            .select('discordUsername coins');
        
        res.json({ 
            users: users.map(u => ({ 
                username: u.discordUsername, 
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
    req.session.destroy((err) => {
        if (err) {
            return res.status(500).json({ error: 'Logout failed' });
        }
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
    console.log('📋 Serving dashboard for:', req.session.user.username);
    res.sendFile(path.join(__dirname, 'dashboard.html'));
});

// Error handling
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).json({ error: 'Internal server error' });
});

module.exports = app;

if (require.main === module) {
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log(`🚀 Server running on port ${PORT}`);
        console.log(`🔗 Production URL: https://dash.blazenode.site`);
        console.log(`🔐 Discord OAuth: ${config.DISCORD_REDIRECT_URI}`);
    });
}