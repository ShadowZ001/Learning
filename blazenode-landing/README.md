# BlazeNode Dashboard with Discord OAuth2

A modern dashboard with Discord OAuth2 authentication system.

## Features

- **Discord OAuth2 Login** - Secure authentication using Discord
- **Session Management** - Persistent user sessions
- **Auto Server Join** - Users automatically join your Discord server
- **Modern Dashboard** - Clean, responsive interface
- **User Profile Display** - Shows Discord avatar and username

## Setup Instructions

### 1. Install Dependencies
```bash
npm install
```

### 2. Environment Configuration
The `.env` file is already configured with your Discord app credentials:
- Client ID: `1412406526894669874`
- Client Secret: `a8n7Xeaw_6AgxXexR7E8RYc0CD2KAxCJ`
- Redirect URI: `https://localhost:3000/callback`
- Server ID: `1369352923221590047`

### 3. Discord App Configuration
Make sure your Discord application has the redirect URI set to:
```
https://localhost:3000/callback
```

### 4. Start the Server
```bash
npm start
# or
./start.sh
```

The server will run on `http://localhost:3000`

## File Structure

```
blazenode-landing/
├── server.js          # Express server with OAuth2 routes
├── package.json       # Dependencies and scripts
├── .env              # Environment variables
├── index.html        # Landing page with login button
├── dashboard.html    # Main dashboard (requires auth)
├── dashboard.js      # Dashboard functionality
├── dashboard.css     # Dashboard styling
├── script.js         # Landing page scripts
├── styles.css        # Landing page styling
└── README.md         # This file
```

## API Endpoints

- `GET /` - Landing page (redirects to dashboard if logged in)
- `GET /login` - Initiates Discord OAuth2 flow
- `GET /callback` - OAuth2 callback handler
- `GET /dashboard.html` - Dashboard page (requires auth)
- `GET /api/user` - Get current user info
- `POST /api/logout` - Logout and destroy session

## How It Works

1. **Login Flow**:
   - User clicks "Login with Discord" button
   - Redirects to Discord OAuth2 authorization
   - User authorizes the application
   - Discord redirects back to `/callback` with auth code
   - Server exchanges code for access token
   - Server fetches user profile from Discord API
   - User session is created and stored
   - User is redirected to dashboard

2. **Dashboard**:
   - Shows personalized welcome message with Discord username
   - Displays user's Discord avatar
   - Provides logout functionality
   - Protected route (requires authentication)

3. **Session Management**:
   - Sessions stored in memory (for development)
   - 24-hour session expiry
   - Automatic redirect to login if not authenticated

## Development Notes

- The server runs on port 3000 by default
- Sessions are stored in memory (use Redis/database for production)
- HTTPS is required for Discord OAuth2 in production
- The current setup is configured for localhost development

## Production Deployment

For production deployment:
1. Update the redirect URI in Discord app settings
2. Update `DISCORD_REDIRECT_URI` in `.env`
3. Use HTTPS
4. Implement persistent session storage
5. Add proper error handling and logging