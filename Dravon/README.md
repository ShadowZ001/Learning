# 🤖 Dravon Bot - Advanced Discord Server Management

[![Discord](https://img.shields.io/discord/1413789539350118020?color=7289da&logo=discord&logoColor=white)](https://discord.gg/UKR78VcEtg)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Dravon** is a comprehensive Discord bot designed for advanced server management with premium features, security systems, and entertainment modules.

## ✨ Features

### 🛡️ **Security & Moderation**
- **AntiNuke v6.0** - Advanced server protection system
- **AutoMod** - Automatic content filtering and moderation
- **Comprehensive Moderation** - Ban, kick, mute, warn with DM notifications
- **Whitelist System** - Trusted user management

### 🎵 **Music System**
- **Multi-Platform Support** - YouTube, Spotify (Premium), SoundCloud
- **24/7 Mode** - Keep bot in voice channel (Premium feature)
- **Interactive Player** - Button controls and queue management
- **Voice Channel Status** - Shows currently playing song in VC
- **Smart Node Management** - Automatic failover to backup Lavalink servers

### 🎫 **Server Management**
- **Ticket System** - Professional support ticket management
- **Welcome/Leave Messages** - Customizable member greetings
- **AutoRole** - Automatic role assignment for new members
- **Invite Tracking** - Track who invites new members
- **Giveaway System** - Falcon-style giveaway management

### 💎 **Premium Features**
- **No-Prefix Commands** - Natural command usage for premium users
- **Spotify Integration** - High-quality music streaming
- **24/7 Music Mode** - Never-ending voice presence
- **Priority Support** - Faster response times
- **Advanced Analytics** - Detailed server insights

### 🎮 **Entertainment**
- **Fun Commands** - Kiss, slap, hug with anime GIFs
- **Interactive Games** - Various entertainment modules
- **Custom Embeds** - Beautiful embed creation system

### 📊 **Information & Utilities**
- **Server Analytics** - Detailed server information
- **User Profiles** - Comprehensive user information with banners
- **Bot Statistics** - Real-time bot performance metrics
- **Ping Command** - Bot, API, and Lavalink latency

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- MongoDB database
- Discord Bot Token
- Lavalink server (optional, for music features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/dravon-bot.git
   cd dravon-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   ```bash
   cp config_template.py config.py
   # Edit config.py with your settings
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your tokens and database URI
   ```

5. **Run the bot**
   ```bash
   python start_dravon.py
   ```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with the following variables:

```env
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret

# Database Configuration
MONGODB_URI=your_mongodb_connection_string

# Lavalink Configuration (Optional)
LAVALINK_HOST=localhost
LAVALINK_PORT=2333
LAVALINK_PASSWORD=youshallnotpass

# Admin Configuration
BOT_ADMIN_ID=your_user_id
```

### Bot Permissions
The bot requires the following permissions:
- Administrator (recommended) or specific permissions:
  - Manage Server
  - Manage Roles
  - Manage Channels
  - Manage Messages
  - Connect & Speak (for music)
  - Use Voice Activity
  - Send Messages
  - Embed Links
  - Attach Files

## 📋 Commands

### Basic Commands
- `/help` - Show all available commands
- `/serverinfo` - Display server information
- `/userinfo` - Show user information
- `/ping` - Check bot latency

### Moderation
- `/kick <user> [reason]` - Kick a member
- `/ban <user> [reason]` - Ban a member
- `/mute <user> <time> [reason]` - Mute a member
- `/purge <amount>` - Delete messages

### Music
- `/play <song>` - Play music
- `/skip` - Skip current track
- `/stop` - Stop music and clear queue
- `/247 enable/disable` - Toggle 24/7 mode (Premium)

### Setup Commands
- `/antinuke setup` - Configure security system
- `/automod setup` - Setup automatic moderation
- `/welcome setup` - Configure welcome messages
- `/ticket setup` - Setup ticket system

## 🏗️ Deployment

### Pterodactyl Panel
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions on Pterodactyl panels.

### Docker
```bash
docker build -t dravon-bot .
docker run -d --name dravon-bot -e DISCORD_TOKEN="your_token" dravon-bot
```

### VPS/Dedicated Server
```bash
# Clone and setup
git clone https://github.com/yourusername/dravon-bot.git
cd dravon-bot
chmod +x start.sh
./start.sh
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Discord Server**: [Join our support server](https://discord.gg/UKR78VcEtg)
- **Documentation**: Check the `/docs` command in Discord
- **Issues**: Report bugs on GitHub Issues

## 🙏 Acknowledgments

- Discord.py community for the excellent library
- Lavalink developers for the music functionality
- All contributors and users who help improve Dravon

## 📊 Statistics

- **Servers**: 1000+ Discord servers
- **Users**: 100,000+ users served
- **Commands**: 100+ available commands
- **Uptime**: 99.9% average uptime

---

**Made with ❤️ by the Dravon Team**

[Invite Dravon](https://discord.com/oauth2/authorize?client_id=1412942933405208668&permissions=8&integration_type=0&scope=bot) | [Support Server](https://discord.gg/UKR78VcEtg) | [Partnership](https://discord.gg/GwXUfVjnTm)