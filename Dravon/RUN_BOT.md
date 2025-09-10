# 🚀 Dravon Bot - Quick Start Guide

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **Discord Bot Token** from Discord Developer Portal
3. **MongoDB Database** (optional, uses local JSON if not available)

## ⚡ Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Make sure your `.env` file has the Discord token:
```env
DISCORD_TOKEN=your_bot_token_here
```

### 3. Start the Bot
```bash
# Method 1: Enhanced startup script (Recommended)
python start_dravon.py

# Method 2: Direct startup
python main.py
```

### 4. Sync Slash Commands (Optional)
```bash
python sync_commands.py
```

## 🎯 Features Implemented

### ✅ Cooldown System
- **Normal Users**: 2-second cooldown on all commands
- **Premium Users**: No cooldowns
- **Premium Guilds**: No cooldowns for all members

### ✅ Guild Join Messages
- **Thank You Message**: Sent when bot joins a server
- **Support & Partnership Buttons**: Direct links to official servers
- **Greeting Message**: Additional welcome with help button

### ✅ No-Prefix System (Premium)
- **Premium Users**: Can use commands without prefix
- **Premium Guilds**: All members can use commands without prefix
- **Smart Detection**: Recognizes all bot commands automatically

### ✅ Hybrid Commands
- **Slash Commands**: All major commands work with `/`
- **Regular Commands**: Traditional prefix commands still work
- **Dual Support**: Users can choose their preferred method

## 🎮 Command Examples

### Regular Commands (with prefix)
```
>help              # Show help menu
>serverinfo        # Server information
>botinfo           # Bot statistics
>premium           # Premium features
>antinuke setup    # Security setup
>play music        # Play music
```

### Slash Commands
```
/help              # Show help menu
/serverinfo        # Server information
/botinfo           # Bot statistics
/premium           # Premium features
/antinuke setup    # Security setup
/play music        # Play music
```

### Premium No-Prefix (Premium Users Only)
```
help               # Show help menu
serverinfo         # Server information
botinfo            # Bot statistics
premium            # Premium features
antinuke setup     # Security setup
play music         # Play music
```

## 🔧 Bot Configuration

### Premium System
- **User Premium**: Individual premium access
- **Guild Premium**: Server-wide premium (activated by premium users)
- **Features**: No cooldowns, Spotify music, premium badges

### Security Features
- **AntiNuke v6.0**: Advanced server protection
- **AutoMod**: Automatic content moderation
- **Whitelist System**: Trusted user management

### Music System
- **Multi-node Lavalink**: Reliable music streaming
- **Spotify Integration**: Premium feature
- **Interactive Controls**: Button-based player

## 📊 Bot Status

When the bot starts successfully, you'll see:
```
==================================================
🤖 Dravon#1234 has connected to Discord!
📊 Bot is in 5 guilds
👥 Serving 1,250 users
📅 Ready at: 2025-01-09 15:30:45
==================================================
✅ Synced 25 slash commands globally
```

## 🛠️ Troubleshooting

### Common Issues

1. **Bot not responding to commands**
   - Check if bot has proper permissions
   - Verify the prefix is correct (`>`)
   - Try slash commands instead

2. **Slash commands not working**
   - Run `python sync_commands.py`
   - Wait up to 1 hour for global sync
   - Check bot permissions

3. **Music not working**
   - Verify Lavalink nodes in `.env`
   - Check voice channel permissions
   - Try different music sources

4. **Premium features not working**
   - Check database connection
   - Verify premium status with `/premium show`
   - Contact support if issues persist

## 📞 Support

- **Support Server**: https://discord.gg/UKR78VcEtg
- **Partnership**: https://discord.gg/NCDpChD6US
- **Bot Invite**: [Add Dravon](https://discord.com/oauth2/authorize?client_id=1412942933405208668&permissions=8&integration_type=0&scope=bot)

## 🎉 Success!

Your Dravon bot is now running with:
- ✅ 2-second cooldowns for normal users
- ✅ No cooldowns for premium users/guilds
- ✅ Guild join messages with buttons
- ✅ Enhanced no-prefix system
- ✅ Working slash commands
- ✅ All premium features active

Enjoy your fully-featured Discord bot! 🚀