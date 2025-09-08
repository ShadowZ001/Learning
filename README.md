# BlazeNode Dashboard

Advanced web dashboard for BlazeNode hosting platform with Discord OAuth2 authentication, Linkvertise integration, server management, and comprehensive user features.

## 🚀 Features

### 🔐 **Dual Authentication System**
- **Username/Password Login** - Traditional authentication
- **Discord OAuth2** - Seamless Discord integration with auto-server joining
- **Admin System** - Role-based access control
- **Session Management** - Secure session handling

### 🎮 **Server Management**
- **Pterodactyl Integration** - Full server lifecycle management
- **Resource Allocation** - RAM, CPU, Disk management
- **Real-time Monitoring** - Server status and usage tracking
- **One-click Deployment** - Instant server creation

### 💰 **Economy System**
- **BlazeCoins** - Virtual currency system
- **Multiple Earning Methods** - AFK, Linkvertise, Daily rewards
- **Store System** - Purchase resources and upgrades
- **Coupon System** - Redeem codes for rewards

### 🎯 **Advanced Features**
- **AFK Earning** - Automated coin generation
- **Pong Mini-Game** - Entertainment while earning
- **Linkvertise Integration** - Advanced completion detection
- **Server Promotion** - Community server sharing
- **Leaderboards** - User rankings and competitions

### 👑 **Admin Panel**
- **User Management** - Create, edit, delete users
- **Coin Management** - Give/remove coins
- **Store Management** - Update prices and items
- **System Monitoring** - Health checks and diagnostics
- **Discord Management** - Server integration settings

## 🛠️ **Tech Stack**

- **Backend**: Node.js, Express.js
- **Database**: MongoDB with Mongoose ODM
- **Authentication**: Passport.js with Discord OAuth2
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **API Integration**: Pterodactyl Panel API, Discord API
- **Session Management**: Express Sessions

## 📦 **Installation**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd blazenode-landing
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start the server**
   ```bash
   npm start
   ```

## ⚙️ **Configuration**

### Required Environment Variables

```env
# Database
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database

# Session
SESSION_SECRET=your_session_secret_key

# Pterodactyl Panel
PTERODACTYL_API_KEY=your_pterodactyl_api_key
PTERODACTYL_URL=https://panel.yourdomain.com

# Discord OAuth2
DISCORD_CLIENT_ID=your_discord_client_id
DISCORD_CLIENT_SECRET=your_discord_client_secret
DISCORD_REDIRECT_URI=https://yourdomain.com/auth/callback
DISCORD_GUILD_ID=your_discord_server_id
DISCORD_INVITE_LINK=https://discord.gg/yourinvite

# Bot Configuration
BOT_API_KEY=your_discord_bot_token

# Admin
ADMIN_EMAIL=admin@yourdomain.com
```

## 🔧 **Discord OAuth2 Setup**

1. **Create Discord Application**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create new application
   - Note the Client ID and Client Secret

2. **Configure OAuth2**
   - Add redirect URI: `https://yourdomain.com/auth/callback`
   - Select scopes: `identify`, `email`, `guilds.join`

3. **Bot Setup**
   - Create bot in the application
   - Copy bot token
   - Invite bot to your server with appropriate permissions

## 🚀 **Deployment**

### Production Deployment Options:
- **Vercel** - Serverless deployment
- **Railway** - Container deployment
- **Heroku** - Platform as a Service
- **cPanel** - Traditional hosting
- **VPS/Dedicated** - Full control

### cPanel Deployment:
1. Upload files to public_html
2. Install dependencies: `npm install`
3. Configure environment in `config.js`
4. Start with: `node app.js`

## 🔒 **Security Features**

- **CSRF Protection** - State parameter validation
- **Session Security** - Secure cookie configuration
- **Input Validation** - Comprehensive data sanitization
- **Rate Limiting** - API endpoint protection
- **Error Handling** - Graceful error management

## 📱 **Mobile Responsive**

- **Adaptive Design** - Works on all devices
- **Touch Optimized** - Mobile-friendly interactions
- **Progressive Enhancement** - Core functionality always available

## 🎮 **Gaming Features**

- **AFK System** - Earn coins while active
- **Mini Games** - Pong game integration
- **Achievements** - Daily streaks and rewards
- **Competitions** - Leaderboard rankings

## 🔧 **API Endpoints**

### Authentication
- `POST /api/login` - Username/password login
- `GET /auth/discord` - Discord OAuth2 initiation
- `GET /auth/callback` - Discord OAuth2 callback
- `POST /api/logout` - User logout

### User Management
- `GET /api/user` - Get current user data
- `GET /api/resource-usage` - Get resource allocation
- `POST /api/admin/create-user` - Create new user (admin)

### Server Management
- `GET /api/servers` - Get user servers
- `POST /api/create-server` - Create new server
- `POST /api/delete-server` - Delete server
- `GET /api/nests` - Get available server types

## 📊 **Monitoring**

- `GET /api/health` - Health check endpoint
- `GET /api/status` - System status
- `GET /api/debug` - Debug information

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- **Discord Server**: [Join our community](https://discord.gg/PyfEzq5gQ)
- **Documentation**: Check the wiki for detailed guides
- **Issues**: Report bugs via GitHub issues

## 🔄 **Version History**

- **v2.1.0** - Discord OAuth2 integration
- **v2.0.0** - Complete dashboard rewrite
- **v1.0.0** - Initial release

---

**Built with ❤️ by the BlazeNode Team**