const express = require('express');
const session = require('express-session');
const cors = require('cors');
const mongoose = require('mongoose');
const path = require('path');
const passport = require('passport');
const DiscordStrategy = require('passport-discord').Strategy;
const LocalStrategy = require('passport-local').Strategy;
const bcrypt = require('bcrypt');
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

// Create admin user on startup
async function createAdminUser() {
    try {
        const adminExists = await User.findOne({ username: 'dev_shadowz' });
        if (!adminExists) {
            const hashedPassword = await bcrypt.hash('shadowz', 10);
            const admin = new User({
                username: 'dev_shadowz',
                password: hashedPassword,
                email: 'admin@blazenode.site',
                loginType: 'local',
                isAdmin: true,
                coins: 10000,
                serverCount: 0
            });
            await admin.save();
            console.log('✅ Admin user created: dev_shadowz');
        }
    } catch (error) {
        console.error('❌ Admin creation failed:', error.message);
    }
}

// Local Strategy for admin login
passport.use(new LocalStrategy(
    async (username, password, done) => {
        try {
            console.log('🔐 Local login attempt:', username);
            
            const user = await User.findOne({ username: username.toLowerCase() });
            if (!user) {
                console.log('❌ User not found:', username);
                return done(null, false, { message: 'Invalid credentials' });
            }
            
            const isValid = await bcrypt.compare(password, user.password);
            if (!isValid) {
                console.log('❌ Invalid password for:', username);
                return done(null, false, { message: 'Invalid credentials' });
            }
            
            console.log('✅ Local login success:', username);
            return done(null, user);
        } catch (error) {
            console.error('❌ Local auth error:', error);
            return done(error);
        }
    }
));

// Discord Strategy - FIXED
passport.use(new DiscordStrategy({
    clientID: config.DISCORD_CLIENT_ID,
    clientSecret: config.DISCORD_CLIENT_SECRET,
    callbackURL: config.DISCORD_REDIRECT_URI,
    scope: ['identify', 'email']
}, async (accessToken, refreshToken, profile, done) => {
    try {
        console.log('🔐 Discord OAuth for:', profile.username, profile.id);
        console.log('📧 Discord email:', profile.email);
        console.log('🔗 Callback URL used:', config.DISCORD_REDIRECT_URI);
        
        // Ensure database connection
        if (mongoose.connection.readyState !== 1) {
            console.log('⚠️ Reconnecting to database...');
            await connectMongoDB();
        }
        
        if (mongoose.connection.readyState !== 1) {
            console.error('❌ Database connection failed');
            return done(new Error('Database unavailable'), null);
        }
        
        let user = await User.findOne({ discordId: profile.id });
        
        if (user) {
            // Update existing user
            user.discordUsername = profile.username;
            user.discordAvatar = profile.avatar;
            user.email = profile.email || user.email;
            user.lastLogin = new Date();
            console.log('📝 Updating user:', profile.username);
        } else {
            // Create new user
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
            console.log('🆕 Creating user:', profile.username);
        }
        
        const savedUser = await user.save();
        console.log('✅ User saved:', savedUser.discordUsername, savedUser._id);
        return done(null, savedUser);
        
    } catch (error) {
        console.error('❌ Discord OAuth error:', error.message);
        console.error('Stack:', error.stack);
        return done(new Error('Discord authentication failed'), null);
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
setTimeout(createAdminUser, 2000);

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
            return res.redirect('/?error=discord_auth_failed&message=' + encodeURIComponent(err.message));
        }
        
        if (!user) {
            console.error('❌ No user from Discord:', info);
            return res.redirect('/?error=discord_no_user&message=' + encodeURIComponent('Discord authentication failed'));
        }
        
        req.logIn(user, (loginErr) => {
            if (loginErr) {
                console.error('❌ Login error:', loginErr);
                return res.redirect('/?error=login_failed&message=' + encodeURIComponent('Login process failed'));
            }
            
            console.log('✅ Discord user logged in:', user._id);
            
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
            
            console.log('🔄 Redirecting to dashboard...');
            return res.redirect('/dashboard');
        });
    })(req, res, next);
});

// Local login route
app.post('/auth/login', (req, res, next) => {
    console.log('🔐 Local login attempt for:', req.body.username);
    
    passport.authenticate('local', (err, user, info) => {
        if (err) {
            console.error('❌ Local auth error:', err);
            return res.status(500).json({ error: 'Authentication error' });
        }
        
        if (!user) {
            console.log('❌ Local login failed:', info?.message);
            return res.status(401).json({ error: info?.message || 'Invalid credentials' });
        }
        
        req.logIn(user, (loginErr) => {
            if (loginErr) {
                console.error('❌ Local login error:', loginErr);
                return res.status(500).json({ error: 'Login failed' });
            }
            
            console.log('✅ Local user logged in:', user.username);
            
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

// Debug route
app.get('/debug', (req, res) => {
    res.json({
        session: req.session,
        user: req.user,
        authenticated: req.isAuthenticated(),
        config: {
            clientId: config.DISCORD_CLIENT_ID,
            redirectUri: config.DISCORD_REDIRECT_URI,
            mongoConnected: mongoose.connection.readyState === 1
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
        console.log(`👤 Admin: dev_shadowz / shadowz`);
    });
}