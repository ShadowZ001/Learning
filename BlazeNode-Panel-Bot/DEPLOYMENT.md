# BlazeNode Panel Bot - Deployment Guide

## Repository Setup Instructions

Since automatic GitHub repository creation failed, please follow these steps to create the repository manually:

### Step 1: Create GitHub Repository
1. Go to https://github.com/ShadowZ001
2. Click "New repository"
3. Repository name: `BlazeNode-Panel-Bot`
4. Description: `Complete Discord bot for Pterodactyl panel management with advanced features`
5. Set as Public
6. Don't initialize with README (we already have files)
7. Click "Create repository"

### Step 2: Push Code to Repository
After creating the repository, run these commands in the bot folder:

```bash
git remote set-url origin https://github.com/ShadowZ001/BlazeNode-Panel-Bot.git
git push -u origin main
```

## Bot Features Completed

✅ **Core Features:**
- Server creation with step-by-step setup
- Resource shop and management system
- Advanced coin system with role rewards
- Chat coins system (1 coin per 2 messages)
- Gambling system with coinflip
- Admin management tools

✅ **Role System:**
- Collector roles based on coin thresholds
- Automatic role assignment/removal
- Congratulations and breakdown messages

✅ **Admin Commands:**
- `/admin` - Manage administrators
- `/coins` - Add/remove user coins
- `/blacklist` - Blacklist management
- `/createcode` - Create redeem codes
- `/server` - Server management
- `/chat` - Chat coins system control

✅ **User Commands:**
- `/create` - Server creation
- `/balance` - Enhanced balance card
- `/shop` - Resource shopping
- `/resources` - Resource inventory
- `/coinflip` - Gambling with 40% win chance
- `/leaderboard` - Top users with pagination
- `/redeem` - Redeem codes

✅ **Special Features:**
- Server slot limit (max 2 extra slots)
- Reduced specs for additional servers
- Server creation notifications
- Blacklist protection for all commands
- Error handling and crash prevention

## Environment Variables Required

```env
BOT_TOKEN=your_discord_bot_token
PTERODACTYL_API_KEY=your_pterodactyl_api_key
PTERODACTYL_URL=your_pterodactyl_panel_url
MONGODB_URI=your_mongodb_connection_string
GUILD_ID=your_discord_server_id
```

## Installation

1. Clone the repository
2. Run `npm install`
3. Copy `.env.example` to `.env` and fill in your values
4. Run `npm start`

The bot is ready for production deployment!