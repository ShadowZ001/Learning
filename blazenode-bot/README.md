# BlazeNode Discord Bot

Advanced Discord bot for BlazeNode hosting platform with dashboard integration and comprehensive user management.

## Features

- 👥 **User Management**: Create and manage user accounts
- 💰 **Coin System**: Give/remove coins, check balances
- 🔗 **Dashboard Integration**: Seamless API communication
- 📊 **Statistics**: User stats and leaderboards
- 🛡️ **Admin Commands**: Complete administrative control
- 🎮 **Server Integration**: Link Discord users to dashboard
- 📈 **Analytics**: Track user activity and engagement
- 🔒 **Security**: Role-based permissions and validation

## Commands

### Admin Commands
- `/give-coins <user> <amount>` - Give coins to a user
- `/remove-coins <user> <amount>` - Remove coins from a user
- `/user-info <user>` - Get detailed user information
- `/create-user <username>` - Create new dashboard account
- `/stats` - View bot and platform statistics

### User Commands
- `/balance` - Check your coin balance
- `/profile` - View your profile information
- `/leaderboard` - View top users by coins
- `/link-account` - Link Discord to dashboard account

## Installation

1. Clone the repository
2. Copy `.env.example` to `.env` and configure your settings
3. Install dependencies:
   ```bash
   npm install
   ```
4. Start the bot:
   ```bash
   npm start
   ```

## Environment Variables

See `.env.example` for all required environment variables.

## Dashboard Integration

The bot communicates with the BlazeNode dashboard through secure API endpoints:
- User creation and management
- Coin transactions
- Statistics synchronization
- Real-time updates

## Production Deployment

This bot is ready for deployment on:
- Railway
- Heroku
- VPS/Dedicated servers
- Any Node.js hosting platform

## Tech Stack

- **Framework**: Discord.js v14
- **Database**: MongoDB with Mongoose
- **API**: RESTful communication with dashboard
- **Authentication**: Token-based API authentication
- **Logging**: Comprehensive error handling and logging

## License

MIT License - see LICENSE file for details.