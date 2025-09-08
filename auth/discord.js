const axios = require('axios');
const config = require('../config');

// Enhanced Discord server join with retry logic
async function joinDiscordServerWithRetry(userId, accessToken, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            console.log(`🔄 Attempting to join Discord server (${attempt}/${maxRetries}):`, userId);
            
            const response = await axios.put(
                `https://discord.com/api/v10/guilds/${config.DISCORD_GUILD_ID}/members/${userId}`,
                {
                    access_token: accessToken
                },
                {
                    headers: {
                        'Authorization': `Bot ${config.BOT_API_KEY}`,
                        'Content-Type': 'application/json'
                    },
                    timeout: 10000
                }
            );
            
            console.log('✅ User successfully joined Discord server:', userId);
            return true;
            
        } catch (error) {
            const status = error.response?.status;
            const errorData = error.response?.data;
            
            console.log(`❌ Discord join attempt ${attempt} failed:`, {
                status,
                error: errorData?.message || error.message,
                userId
            });
            
            // Don't retry on certain errors
            if (status === 403 || status === 401 || status === 204) {
                console.log('🚫 Permanent error or already in server, not retrying');
                return status === 204; // 204 means already in server
            }
            
            // Wait before retry (exponential backoff)
            if (attempt < maxRetries) {
                const delay = Math.pow(2, attempt) * 1000;
                console.log(`⏳ Waiting ${delay}ms before retry...`);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }
    
    console.log('❌ Failed to join Discord server after all attempts:', userId);
    return false;
}

// Validate Discord bot token
async function validateDiscordBot() {
    try {
        const response = await axios.get('https://discord.com/api/v10/users/@me', {
            headers: {
                'Authorization': `Bot ${config.BOT_API_KEY}`
            },
            timeout: 5000
        });
        
        console.log('✅ Discord bot token valid:', response.data.username);
        return true;
    } catch (error) {
        console.error('❌ Discord bot token validation failed:', error.response?.status, error.response?.data || error.message);
        return false;
    }
}

module.exports = {
    joinDiscordServerWithRetry,
    validateDiscordBot
};