# BlazeNode Discord Bot

Discord bot for managing BlazeNode dashboard users and coins.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure `.env` file with:
- `MONGODB_URI` - Same database as dashboard
- `DISCORD_BOT_TOKEN` - Your Discord bot token
- `ADMIN_USER_ID` - Discord user ID who can use commands

3. Start the bot:
```bash
npm start
```

## Commands (Admin Only)

- `/create <username> <password>` - Create new user
- `/coin give <username> <amount>` - Add coins to user
- `/coin remove <username> <amount>` - Remove coins from user
- `/balance <username>` - Check user's coin balance
- `/users` - List all users (max 10)
- `/delete <username>` - Delete user account
- `/help` - Show help message

## Deployment

This bot can be hosted separately from the dashboard on any Node.js hosting service.
Both bot and dashboard connect to the same MongoDB database.