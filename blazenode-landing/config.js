// Configuration file for BlazeNode Dashboard
// Production configuration with all values filled

module.exports = {
    // Database Configuration
    MONGODB_URI: 'mongodb+srv://subhasish824988_db_user:blazenode@cluster0.ngqj9vt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0',
    
    // Session Configuration
    SESSION_SECRET: 'blazenode_secret_key_2025_production_ready',
    
    // Pterodactyl Panel Configuration
    PTERODACTYL_API_KEY: 'ptla_Q1aRhsnRiJ8PQEErS3IiknCuuAG1zdueM1OVck39LMN',
    PTERODACTYL_URL: 'https://panel.blazenode.site',
    
    // Bot API Configuration  
    BOT_API_KEY: process.env.DISCORD_BOT_TOKEN || 'your_bot_token_here',
    
    // Discord OAuth2 Configuration - PRODUCTION FIXED
    DISCORD_CLIENT_ID: '1414622141705617583',
    DISCORD_CLIENT_SECRET: 'lwXQLgJdLy844a1ejcTwjhzUwH4MqDh_',
    DISCORD_REDIRECT_URI: 'https://dash.blazenode.site/auth/callback',
    DISCORD_GUILD_ID: '1413789539350118020',
    DISCORD_INVITE_LINK: 'https://discord.gg/PyfEzq5gQ',
    
    // Admin Configuration
    ADMIN_EMAIL: 'dereckrich8@gmail.com',
    
    // Environment
    NODE_ENV: process.env.NODE_ENV || 'development'
};