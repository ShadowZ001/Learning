// Configuration file for BlazeNode Dashboard
// REPLACE THESE VALUES FOR YOUR CPANEL DEPLOYMENT

module.exports = {
    // Database Configuration - REPLACE WITH YOUR MONGODB
    MONGODB_URI: 'YOUR_MONGODB_CONNECTION_STRING',
    
    // Session Configuration - REPLACE WITH RANDOM SECRET
    SESSION_SECRET: 'YOUR_RANDOM_SESSION_SECRET_KEY',
    
    // Pterodactyl Panel Configuration - REPLACE WITH YOUR PANEL
    PTERODACTYL_API_KEY: 'YOUR_PTERODACTYL_API_KEY',
    PTERODACTYL_URL: 'https://YOUR_PANEL_DOMAIN.com',
    
    // Bot API Configuration - REPLACE WITH YOUR BOT TOKEN
    BOT_API_KEY: 'YOUR_DISCORD_BOT_TOKEN',
    
    // Discord OAuth2 Configuration - UPDATE REDIRECT_URI TO YOUR DOMAIN
    DISCORD_CLIENT_ID: '1414622141705617583',
    DISCORD_CLIENT_SECRET: 'lwXQLgJdLy844a1ejcTwjhzUwH4MqDh',
    DISCORD_REDIRECT_URI: 'https://YOUR_DOMAIN.com/auth/callback',
    DISCORD_GUILD_ID: '1413789539350118020',
    DISCORD_INVITE_LINK: 'https://discord.gg/PyfEzq5gQ',
    
    // Admin Configuration - KEEP THIS EMAIL
    ADMIN_EMAIL: 'mailtocedrickh8@gmail.com',
    
    // Environment
    NODE_ENV: 'production'
};