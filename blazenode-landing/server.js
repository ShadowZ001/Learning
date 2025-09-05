const express = require('express');
const session = require('express-session');
const cors = require('cors');
const axios = require('axios');
const mongoose = require('mongoose');
const path = require('path');
require('dotenv').config();

const User = require('./models/User');

const app = express();
const PORT = process.env.PORT || 5501;

console.log('Starting server with Discord OAuth2 and MongoDB...');

// MongoDB connection
mongoose.connect(process.env.MONGODB_URI)
    .then(() => console.log('✅ Connected to MongoDB'))
    .catch(err => console.error('❌ MongoDB connection error:', err));

// Middleware
app.use(cors({
    origin: true,
    credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('.'));
app.use(session({
    secret: process.env.SESSION_SECRET || 'fallback-secret',
    resave: false,
    saveUninitialized: false,
    cookie: { 
        secure: false, 
        maxAge: 24 * 60 * 60 * 1000,
        httpOnly: true
    }
}));

// Discord OAuth2 login route
app.get('/login', (req, res) => {
    console.log('Login route accessed');
    
    const authUrl = `https://discord.com/oauth2/authorize?client_id=${process.env.DISCORD_CLIENT_ID}&response_type=code&redirect_uri=${encodeURIComponent(process.env.DISCORD_REDIRECT_URI)}&scope=identify%20email%20guilds.join`;
    console.log('Redirecting to:', authUrl);
    
    res.redirect(authUrl);
});

// OAuth2 callback endpoint
app.get('/callback', async (req, res) => {
    const { code, error } = req.query;
    
    console.log('Callback received');
    
    if (error) {
        console.log('OAuth error:', error);
        return res.redirect('/?error=oauth_error');
    }
    
    if (!code) {
        console.log('No authorization code received');
        return res.redirect('/?error=no_code');
    }

    try {
        console.log('Exchanging code for access token...');
        
        // Exchange code for access token
        const tokenResponse = await axios.post('https://discord.com/api/oauth2/token', 
            new URLSearchParams({
                client_id: process.env.DISCORD_CLIENT_ID,
                client_secret: process.env.DISCORD_CLIENT_SECRET,
                grant_type: 'authorization_code',
                code: code,
                redirect_uri: process.env.DISCORD_REDIRECT_URI
            }),
            {
                headers: { 
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            }
        );

        const { access_token, token_type } = tokenResponse.data;
        console.log('Access token received');

        // Get user info from Discord
        const userResponse = await axios.get('https://discord.com/api/users/@me', {
            headers: { 
                'Authorization': `${token_type} ${access_token}`
            }
        });

        const discordUser = userResponse.data;
        console.log('User data received:', discordUser.username);

        // Find or create user in database
        let user = await User.findOne({ discordId: discordUser.id });
        
        if (!user) {
            console.log('Creating new user in database');
            user = new User({
                discordId: discordUser.id,
                username: discordUser.username,
                discriminator: discordUser.discriminator || '0',
                email: discordUser.email,
                avatar: discordUser.avatar,
                coins: 100
            });
            await user.save();
            console.log('New user created with 100 coins');
        } else {
            console.log('Existing user found, updating login time');
            user.username = discordUser.username;
            user.email = discordUser.email;
            user.avatar = discordUser.avatar;
            user.lastLogin = new Date();
            await user.save();
        }

        // Store user in session
        req.session.user = {
            id: user._id,
            discordId: user.discordId,
            username: user.username,
            email: user.email,
            avatar: user.avatar,
            coins: user.coins
        };

        console.log('User session created, redirecting to dashboard');
        res.redirect('/dashboard.html');
        
    } catch (error) {
        console.error('Discord OAuth error:', error.response?.data || error.message);
        res.redirect('/?error=auth_failed');
    }
});

// API route to get current user
app.get('/api/user', (req, res) => {
    if (!req.session.user) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    res.json(req.session.user);
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
        
        // Check if 24 hours have passed
        if (lastReward && (now - lastReward) < 24 * 60 * 60 * 1000) {
            return res.status(400).json({ error: 'Daily reward already claimed' });
        }

        // Award coins and update streak
        user.coins += 25;
        user.dailyRewardStreak += 1;
        user.lastDailyReward = now;
        await user.save();

        // Update session
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

// Logout route
app.post('/api/logout', (req, res) => {
    console.log('Logout requested');
    req.session.destroy((err) => {
        if (err) {
            console.error('Session destroy error:', err);
        }
        res.json({ success: true });
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
    if (!req.session.user) {
        return res.redirect('/');
    }
    res.sendFile(path.join(__dirname, 'dashboard.html'));
});

app.get('/dashboard', (req, res) => {
    res.redirect('/dashboard.html');
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).send('Internal Server Error');
});

app.listen(PORT, () => {
    console.log(`✅ Server running on http://localhost:${PORT}`);
    console.log(`✅ Login URL: http://localhost:${PORT}/login`);
    console.log(`✅ Callback URL: ${process.env.DISCORD_REDIRECT_URI}`);
});