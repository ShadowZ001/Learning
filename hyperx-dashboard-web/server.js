require('dotenv').config();
const express = require('express');
const session = require('express-session');
const axios = require('axios');
const path = require('path');
const mongoose = require('mongoose');
const cors = require('cors');
const User = require('./models/User');

const app = express();
const PORT = process.env.PORT || 4000;

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI)
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('MongoDB connection error:', err));

// Middleware
app.use(cors());
app.use(express.json());

// Session middleware
app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: { secure: false, maxAge: 24 * 60 * 60 * 1000 } // 24 hours
}));

// Serve static files
app.use(express.static(path.join(__dirname)));

// Routes
app.get('/', (req, res) => {
  if (req.session.user) {
    res.sendFile(path.join(__dirname, 'dashboard.html'));
  } else {
    res.sendFile(path.join(__dirname, 'index.html'));
  }
});

app.get('/login', (req, res) => {
  const authURL = `https://discord.com/api/oauth2/authorize?client_id=${process.env.DISCORD_CLIENT_ID}&redirect_uri=${encodeURIComponent(process.env.DISCORD_REDIRECT_URI)}&response_type=code&scope=identify%20guilds.join`;
  res.redirect(authURL);
});

app.get('/auth/discord/callback', async (req, res) => {
  const { code } = req.query;
  
  if (!code) {
    return res.redirect('/?error=no_code');
  }

  try {
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

    const { access_token } = tokenResponse.data;

    // Get user info
    const userResponse = await axios.get('https://discord.com/api/users/@me', {
      headers: {
        Authorization: `Bearer ${access_token}`
      }
    });

    const user = userResponse.data;

    // Auto-join user to Discord server
    if (process.env.DISCORD_BOT_TOKEN && process.env.DISCORD_SERVER_ID) {
      try {
        await axios.put(
          `https://discord.com/api/guilds/${process.env.DISCORD_SERVER_ID}/members/${user.id}`,
          { access_token: access_token },
          {
            headers: {
              Authorization: `Bot ${process.env.DISCORD_BOT_TOKEN}`,
              'Content-Type': 'application/json'
            }
          }
        );
      } catch (joinError) {
        console.log('User may already be in server or bot lacks permissions');
      }
    }

    // Find or create user in MongoDB
    let dbUser = await User.findOne({ discordId: user.id });
    
    if (!dbUser) {
      // New user - create with signup bonus
      dbUser = new User({
        discordId: user.id,
        username: user.username,
        discriminator: user.discriminator,
        avatar: user.avatar,
        coins: 150,
        signupBonusReceived: true,
        transactions: [{
          type: 'received',
          label: 'Welcome bonus',
          amount: 150,
          time: 'now'
        }]
      });
    } else {
      // Existing user - update info and last login
      dbUser.username = user.username;
      dbUser.discriminator = user.discriminator;
      dbUser.avatar = user.avatar;
      dbUser.lastLogin = new Date();
    }
    
    await dbUser.save();

    // Store user in session
    req.session.user = {
      id: user.id,
      username: user.username,
      discriminator: user.discriminator,
      avatar: user.avatar,
      access_token: access_token
    };

    res.redirect('/');
  } catch (error) {
    console.error('OAuth error:', error.response?.data || error.message);
    console.error('Full error:', error);
    res.redirect('/?error=auth_failed');
  }
});

app.get('/api/user', async (req, res) => {
  if (req.session.user) {
    try {
      const dbUser = await User.findOne({ discordId: req.session.user.id });
      if (dbUser) {
        res.json({
          id: dbUser.discordId,
          username: dbUser.username,
          discriminator: dbUser.discriminator,
          avatar: dbUser.avatar,
          coins: dbUser.coins,
          transactions: dbUser.transactions
        });
      } else {
        res.status(404).json({ error: 'User not found' });
      }
    } catch (error) {
      res.status(500).json({ error: 'Database error' });
    }
  } else {
    res.status(401).json({ error: 'Not authenticated' });
  }
});

// Add transaction endpoint
app.post('/api/transaction', async (req, res) => {
  if (!req.session.user) {
    return res.status(401).json({ error: 'Not authenticated' });
  }
  
  try {
    const { type, label, amount } = req.body;
    const dbUser = await User.findOne({ discordId: req.session.user.id });
    
    if (!dbUser) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    // Update coins
    if (type === 'received') {
      dbUser.coins += amount;
    } else if (type === 'sent') {
      if (dbUser.coins < amount) {
        return res.status(400).json({ error: 'Insufficient balance' });
      }
      dbUser.coins -= amount;
    }
    
    // Add transaction
    dbUser.transactions.unshift({
      type,
      label,
      amount,
      time: 'now'
    });
    
    await dbUser.save();
    
    res.json({ success: true, newBalance: dbUser.coins });
  } catch (error) {
    res.status(500).json({ error: 'Database error' });
  }
});

app.get('/logout', (req, res) => {
  req.session.destroy();
  res.redirect('/');
});

app.listen(PORT, () => {
  console.log(`HyperX Dashboard running on http://localhost:${PORT}`);
  console.log(`Discord OAuth redirect URI: ${process.env.DISCORD_REDIRECT_URI}`);
});