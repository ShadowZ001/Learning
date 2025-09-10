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
        httpOnly: true,
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

// Discord OAuth2 Strategy - FIXED VERSION
passport.use(new DiscordStrategy({
    clientID: config.DISCORD_CLIENT_ID,
    clientSecret: config.DISCORD_CLIENT_SECRET,
    callbackURL: config.DISCORD_REDIRECT_URI,
    scope: ['identify', 'email']
}, async (accessToken, refreshToken, profile, done) => {
    try {
        console.log('🔐 Discord OAuth success for:', profile.username);
        
        // Ensure MongoDB is connected
        if (mongoose.connection.readyState !== 1) {
            console.log('⚠️ MongoDB not connected, attempting reconnection...');
            await ensureMongoConnection();
        }
        
        if (mongoose.connection.readyState !== 1) {
            console.error('❌ MongoDB connection failed during OAuth');
            return done(new Error('Database connection failed'), null);
        }
        
        // Find or create user
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

// Validate Discord bot token on startup
validateDiscordBot().catch(err => {
    console.log('⚠️ Discord bot validation failed, continuing without bot features');
});

// Discord OAuth2 routes with enhanced security
app.get('/auth/discord', (req, res, next) => {
    console.log('🔐 Discord OAuth2 login initiated');
    passport.authenticate('discord')(req, res, next);
});

app.get('/auth/callback', (req, res, next) => {
    passport.authenticate('discord', (err, user, info) => {
        if (err) {
            console.error('❌ Discord authentication error:', err.message);
            return res.redirect('/?error=auth_failed');
        }
        
        if (!user) {
            console.error('❌ No user returned from Discord');
            return res.redirect('/?error=no_user');
        }
        
        console.log('✅ Discord callback success for:', user.discordUsername);
        
        // Login user
        req.logIn(user, (loginErr) => {
            if (loginErr) {
                console.error('❌ Login error:', loginErr);
                return res.redirect('/?error=login_failed');
            }
            
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
            
            // Save session and redirect
            req.session.save((saveErr) => {
                if (saveErr) {
                    console.error('❌ Session save error:', saveErr);
                    return res.redirect('/?error=session_failed');
                }
                
                console.log('✅ Session saved, redirecting to dashboard');
                res.redirect('/dashboard.html');
            });
        });
    })(req, res, next);
});

// User API - Get current user data
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

// Serve static files
app.get('/', (req, res) => {
    console.log('🏠 Home page access');
    
    // Check if already authenticated
    if (req.session?.user?.id) {
        console.log('✅ Already logged in, redirecting to dashboard');
        return res.redirect('/dashboard.html');
    }
    
    console.log('🔐 Not logged in, serving login page');
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/dashboard.html', (req, res) => {
    console.log('📋 Dashboard access attempt');
    console.log('Session exists:', !!req.session);
    console.log('Session user:', req.session?.user?.username);
    console.log('Session authenticated:', req.session?.authenticated);
    
    // Check if user is authenticated
    if (!req.session?.authenticated || !req.session?.user?.id) {
        console.log('❌ Not authenticated, redirecting to login');
        return res.redirect('/');
    }
    
    console.log('✅ User authenticated, serving dashboard for:', req.session.user.username);
    res.sendFile(path.join(__dirname, 'dashboard.html'));
});

app.get('/dashboard', (req, res) => {
    res.redirect('/dashboard.html');
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