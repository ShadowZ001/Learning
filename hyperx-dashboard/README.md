# HyperX Game Hosting Platform

A complete game hosting platform with Discord integration, featuring a web dashboard and Discord bot.

## 🏗️ Project Structure

```
hyperx-dashboard/
├── bot/                    # Discord Bot
│   ├── bot.js             # Main bot file
│   ├── package.json       # Bot dependencies
│   └── .env              # Bot environment variables
├── dashboard/             # Web Dashboard
│   ├── server.js         # Express server
│   ├── index.html        # Login page
│   ├── dashboard.html    # Main dashboard
│   ├── package.json      # Dashboard dependencies
│   └── .env             # Dashboard environment variables
├── package.json          # Main project file
└── README.md            # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm run install:all
```

### 2. Configure Environment Variables
Update the `.env` files in both `bot/` and `dashboard/` folders with your Discord application credentials:

```env
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_SERVER_ID=your_server_id
DISCORD_REDIRECT_URI=http://localhost:4000/auth/discord/callback
SESSION_SECRET=your_generated_session_secret
PORT=4000
```

### 3. Start Both Services
```bash
# Start both bot and dashboard
npm start

# Or start them separately
npm run start:dashboard
npm run start:bot

# For development with auto-restart
npm run dev
```

## 🎮 Features

### Discord Bot
- Welcome new members with embedded messages
- Basic commands (!ping, !help, !dashboard, !serverinfo)
- Server information display
- Integration with dashboard

### Web Dashboard
- Discord OAuth2 authentication
- User session management
- Modern responsive UI
- Server management interface
- File manager
- Analytics dashboard

## 🔧 Bot Commands

- `!ping` - Check bot latency
- `!dashboard` - Get dashboard link and information
- `!help` - Show available commands
- `!serverinfo` - Display server statistics

## 🌐 Dashboard Features

- **Authentication**: Secure Discord OAuth2 login
- **Server Management**: Create and manage game servers
- **File Manager**: Web-based file management
- **Console**: Real-time server console
- **Analytics**: Performance monitoring
- **Security**: DDoS protection settings

## 📋 Setup Requirements

1. Discord Application with Bot permissions
2. Node.js 16+ installed
3. Valid Discord server for testing

## 🔗 URLs

- Dashboard: http://localhost:4000
- Discord OAuth: Configured in Discord Developer Portal

## 🛠️ Development

Each component can be developed independently:

```bash
# Dashboard only
cd dashboard && npm run dev

# Bot only  
cd bot && npm run dev
```

## 📝 Notes

- Make sure your Discord application redirect URI matches the one in `.env`
- The bot needs appropriate permissions in your Discord server
- Session secrets should be unique and secure for production