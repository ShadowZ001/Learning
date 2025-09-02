# HyperX Deployment Guide

## 📁 Project Structure

- **`/hyperx-dashboard-web/`** - Web dashboard with MongoDB integration
- **`/hyperx-bot/`** - Discord bot (separate project)

## 🚀 Dashboard Deployment (Railway/Heroku)

### 1. Deploy Dashboard
```bash
cd hyperx-dashboard-web
npm install
```

### 2. Environment Variables
```
DISCORD_CLIENT_ID=1412406526894669874
DISCORD_CLIENT_SECRET=bBBqobQww0M_FdqVz2J_Y3ob1RUCQkTj
DISCORD_REDIRECT_URI=https://your-dashboard-url.com/auth/discord/callback
SESSION_SECRET=your_session_secret
MONGODB_URI=mongodb+srv://subhasish824988_db_user:blazenode@cluster0.ngqj9vt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

### 3. Start Dashboard
```bash
npm start
```

## 🤖 Bot Deployment (Railway/Heroku)

### 1. Deploy Bot
```bash
cd hyperx-bot
npm install
```

### 2. Environment Variables
```
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_SERVER_ID=your_server_id
```

### 3. Start Bot
```bash
npm start
```

## 🔧 Discord App Setup

1. **OAuth2 Redirect URI**: `https://your-dashboard-url.com/auth/discord/callback`
2. **Bot Permissions**: Administrator or required permissions
3. **Bot Invite**: Add bot to your Discord server

## 📊 Features

### Dashboard
- ✅ Discord OAuth authentication
- ✅ MongoDB user storage
- ✅ Coin system with transactions
- ✅ Wallet management
- ✅ Resource store
- ✅ Mobile responsive

### Bot
- ✅ Discord commands
- ✅ Server management
- ✅ User verification

## 🌐 URLs

- **GitHub**: https://github.com/ShadowZ001/Learning
- **Dashboard**: Deploy to Railway/Heroku
- **Bot**: Deploy to Railway/Heroku (separate instance)