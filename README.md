# BlazeNode Platform

Complete hosting platform with advanced dashboard and Discord bot integration.

## Project Structure

```
├── blazenode-landing/     # Web Dashboard
│   ├── server.js         # Main server file
│   ├── dashboard.html    # Dashboard interface
│   ├── dashboard.js      # Frontend logic
│   ├── dashboard.css     # Styling
│   ├── models/          # Database models
│   └── .env.example     # Environment template
│
├── blazenode-bot/        # Discord Bot
│   ├── bot.js           # Main bot file
│   ├── commands/        # Bot commands
│   ├── models/          # Database models
│   └── .env.example     # Environment template
│
└── README.md            # This file
```

## Features Overview

### Dashboard (blazenode-landing/)
- 🎮 Server management with Pterodactyl integration
- 💰 Advanced coin earning system
- 🔗 Linkvertise integration with fraud detection
- ⏰ AFK earning system
- 🏆 Leaderboards and competitions
- 🛍️ Resource store
- 📢 Server promotion system
- 👑 Complete admin panel

### Discord Bot (blazenode-bot/)
- 👥 User account management
- 💰 Coin transactions
- 📊 Statistics and analytics
- 🔗 Dashboard integration
- 🛡️ Admin commands
- 📈 Real-time synchronization

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Learning
   ```

2. **Setup Dashboard**
   ```bash
   cd blazenode-landing
   cp .env.example .env
   # Edit .env with your configuration
   npm install
   npm start
   ```

3. **Setup Discord Bot**
   ```bash
   cd ../blazenode-bot
   cp .env.example .env
   # Edit .env with your configuration
   npm install
   npm start
   ```

## Production Deployment

Both applications are production-ready and can be deployed on:
- **Dashboard**: Vercel, Netlify, Railway, Heroku
- **Bot**: Railway, Heroku, VPS, Dedicated servers

## Environment Configuration

Each project has its own `.env.example` file with detailed configuration options.

## Tech Stack

- **Backend**: Node.js, Express.js
- **Database**: MongoDB
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Bot Framework**: Discord.js v14
- **API Integration**: Pterodactyl Panel
- **Security**: Advanced validation and fraud detection

## License

MIT License - Open source and free to use.

## Support

For support and questions, join our Discord community or create an issue in this repository.