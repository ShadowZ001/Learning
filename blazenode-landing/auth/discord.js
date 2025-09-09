const axios = require('axios');
const config = require('../config');

// Enhanced Discord server join with retry logic and role assignment
async function joinDiscordServerWithRetry(userId, accessToken, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            console.log(`🔄 Attempting to join Discord server (${attempt}/${maxRetries}):`, userId);
            
            const response = await axios.put(
                `https://discord.com/api/v10/guilds/${config.DISCORD_GUILD_ID}/members/${userId}`,
                {
                    access_token: accessToken,
                    roles: [] // Add default roles if needed
                },
                {
                    headers: {
                        'Authorization': `Bot ${config.BOT_API_KEY}`,
                        'Content-Type': 'application/json'
                    },
                    timeout: 15000
                }
            );
            
            console.log('✅ User successfully joined Discord server:', userId);
            
            // Send welcome message
            await sendWelcomeMessage(userId);
            
            return true;
            
        } catch (error) {
            const status = error.response?.status;
            const errorData = error.response?.data;
            
            console.log(`❌ Discord join attempt ${attempt} failed:`, {
                status,
                error: errorData?.message || error.message,
                code: errorData?.code,
                userId
            });
            
            // Handle specific Discord API errors
            if (status === 204 || (status === 409 && errorData?.code === 40007)) {
                console.log('✅ User already in server');
                return true;
            }
            
            if (status === 403 || status === 401) {
                console.log('🚫 Permanent error, not retrying');
                return false;
            }
            
            // Wait before retry (exponential backoff)
            if (attempt < maxRetries) {
                const delay = Math.min(Math.pow(2, attempt) * 1000, 10000);
                console.log(`⏳ Waiting ${delay}ms before retry...`);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }
    
    console.log('❌ Failed to join Discord server after all attempts:', userId);
    return false;
}

// Send welcome message to new member
async function sendWelcomeMessage(userId) {
    try {
        const dmChannel = await axios.post(
            'https://discord.com/api/v10/users/@me/channels',
            {
                recipient_id: userId
            },
            {
                headers: {
                    'Authorization': `Bot ${config.BOT_API_KEY}`,
                    'Content-Type': 'application/json'
                },
                timeout: 5000
            }
        );
        
        await axios.post(
            `https://discord.com/api/v10/channels/${dmChannel.data.id}/messages`,
            {
                embeds: [{
                    title: '🎉 Welcome to BlazeNode!',
                    description: 'Thanks for joining our Discord server! You can now access your dashboard and manage your servers.',
                    color: 0x5865f2,
                    fields: [
                        {
                            name: '🌐 Dashboard',
                            value: 'https://dash.blazenode.site',
                            inline: true
                        },
                        {
                            name: '📋 Panel',
                            value: 'https://panel.blazenode.site',
                            inline: true
                        }
                    ],
                    footer: {
                        text: 'BlazeNode - Asia\'s No. 1 Game Hosting'
                    }
                }]
            },
            {
                headers: {
                    'Authorization': `Bot ${config.BOT_API_KEY}`,
                    'Content-Type': 'application/json'
                },
                timeout: 5000
            }
        );
        
        console.log('✅ Welcome message sent to:', userId);
    } catch (error) {
        console.log('⚠️ Could not send welcome message:', error.response?.data?.message || error.message);
    }
}

// Validate Discord bot token and permissions
async function validateDiscordBot() {
    try {
        // Check bot user info
        const botResponse = await axios.get('https://discord.com/api/v10/users/@me', {
            headers: {
                'Authorization': `Bot ${config.BOT_API_KEY}`
            },
            timeout: 5000
        });
        
        console.log('✅ Discord bot token valid:', botResponse.data.username);
        
        // Check guild permissions
        const guildResponse = await axios.get(
            `https://discord.com/api/v10/guilds/${config.DISCORD_GUILD_ID}`,
            {
                headers: {
                    'Authorization': `Bot ${config.BOT_API_KEY}`
                },
                timeout: 5000
            }
        );
        
        console.log('✅ Bot has access to guild:', guildResponse.data.name);
        
        return true;
    } catch (error) {
        console.error('❌ Discord bot validation failed:', {
            status: error.response?.status,
            error: error.response?.data?.message || error.message
        });
        return false;
    }
}

// Check if user is already in guild
async function checkUserInGuild(userId) {
    try {
        const response = await axios.get(
            `https://discord.com/api/v10/guilds/${config.DISCORD_GUILD_ID}/members/${userId}`,
            {
                headers: {
                    'Authorization': `Bot ${config.BOT_API_KEY}`
                },
                timeout: 5000
            }
        );
        
        return !!response.data;
    } catch (error) {
        return false;
    }
}

// Refresh Discord access token
async function refreshDiscordToken(refreshToken) {
    try {
        const response = await axios.post(
            'https://discord.com/api/v10/oauth2/token',
            new URLSearchParams({
                client_id: config.DISCORD_CLIENT_ID,
                client_secret: config.DISCORD_CLIENT_SECRET,
                grant_type: 'refresh_token',
                refresh_token: refreshToken
            }),
            {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                timeout: 5000
            }
        );
        
        return response.data;
    } catch (error) {
        console.error('❌ Failed to refresh Discord token:', error.response?.data || error.message);
        return null;
    }
}

module.exports = {
    joinDiscordServerWithRetry,
    validateDiscordBot,
    sendWelcomeMessage,
    checkUserInGuild,
    refreshDiscordToken
};