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

// CORS configuration
app.use(cors({
    origin: function(origin, callback) {
        return callback(null, true);
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept']
}));

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
        httpOnly: true,
        maxAge: 7 * 24 * 60 * 60 * 1000,
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

// Discord OAuth2 Strategy
passport.use(new DiscordStrategy({
    clientID: config.DISCORD_CLIENT_ID,
    clientSecret: config.DISCORD_CLIENT_SECRET,
    callbackURL: config.DISCORD_REDIRECT_URI,
    scope: ['identify', 'email']
}, async (accessToken, refreshToken, profile, done) => {
    try {
        console.log('🔐 Discord OAuth success for:', profile.username);
        
        if (mongoose.connection.readyState !== 1) {
            await ensureMongoConnection();
        }
        
        if (mongoose.connection.readyState !== 1) {
            return done(new Error('Database connection failed'), null);
        }
        
        let user = await User.findOne({ discordId: profile.id });
        
        if (user) {
            user.discordUsername = profile.username;
            user.discordAvatar = profile.avatar;
            user.email = profile.email;
            user.lastLogin = new Date();
        } else {
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
        console.log('✅ User saved:', user.discordUsername);
        return done(null, user);
        
    } catch (error) {
        console.error('❌ OAuth error:', error.message);
        return done(new Error('Authentication failed'), null);
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

// Discord OAuth2 routes
app.get('/auth/discord', (req, res, next) => {
    console.log('🔐 Discord OAuth2 login initiated');
    passport.authenticate('discord')(req, res, next);
});

// Discord OAuth callback - FIXED VERSION
app.get('/auth/callback', (req, res, next) => {
    passport.authenticate('discord', (err, user, info) => {
        if (err) {
            console.error("Auth error:", err);
            return res.redirect('/?error=auth_failed');
        }
        if (!user) {
            console.error("No user returned:", info);
            return res.redirect('/?error=no_user');
        }
        req.logIn(user, (loginErr) => {
            if (loginErr) {
                console.error("Login error:", loginErr);
                return next(loginErr);
            }
            console.log("✅ User logged in:", user.id);
            
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
            
            // Redirect to dashboard
            return res.redirect('/dashboard');
        });
    })(req, res, next);
});

// User API
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
        
        console.log('✅ User API response for:', userData.username);
        res.json(userData);
        
    } catch (error) {
        console.error('❌ User API error:', error);
        res.status(500).json({ error: 'Failed to get user data' });
    }
});

// Routes
app.get('/', (req, res) => {
    if (req.session?.user?.id) {
        return res.redirect('/dashboard');
    }
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/dashboard.html', (req, res) => {
    if (!req.isAuthenticated || !req.isAuthenticated()) {
        return res.redirect('/?error=not_logged_in');
    }
    res.sendFile(path.join(__dirname, 'dashboard.html'));
});

app.get('/dashboard', (req, res) => {
    res.redirect('/dashboard.html');
});

// API endpoints
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
        console.error('AFK earn error:', error);
        res.status(500).json({ error: 'Failed to earn coins' });
    }
});

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
        
        if (lastReward && (now - lastReward) < 24 * 60 * 60 * 1000) {
            return res.status(400).json({ error: 'Daily reward already claimed today' });
        }

        user.coins = (user.coins || 0) + 25;
        user.lastDailyReward = now;
        
        if (lastReward && (now - lastReward) < 48 * 60 * 60 * 1000) {
            user.dailyRewardStreak = (user.dailyRewardStreak || 0) + 1;
        } else {
            user.dailyRewardStreak = 1;
        }

        await user.save();

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

module.exports = app;

if (require.main === module) {
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log(`🚀 BlazeNode Dashboard Server Ready on port ${PORT}`);
    });
}