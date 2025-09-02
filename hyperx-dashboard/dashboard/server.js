require('dotenv').config();
const express = require('express');
const session = require('express-session');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 4000;

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

app.get('/api/user', (req, res) => {
  if (req.session.user) {
    const { access_token, ...userInfo } = req.session.user;
    res.json(userInfo);
  } else {
    res.status(401).json({ error: 'Not authenticated' });
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