const { Client, GatewayIntentBits, Collection } = require('discord.js');
const mongoose = require('mongoose');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

// Dashboard API connection
const dashboardAPI = axios.create({
    baseURL: process.env.DASHBOARD_URL || 'http://localhost:5503',
    headers: {
        'Authorization': `Bearer ${process.env.DASHBOARD_API_KEY}`,
        'Content-Type': 'application/json'
    },
    timeout: 10000
});

// Test dashboard connection
dashboardAPI.get('/api/debug/dbtest')
    .then(response => {
        console.log('✅ Dashboard API connection successful');
        console.log('📊 Dashboard status:', response.data.status);
    })
    .catch(error => {
        console.error('❌ Dashboard API connection failed:', error.message);
        console.log('🔄 Bot will continue without dashboard integration');
    });

// HARDCODED ADMIN ID - ONLY THIS USER CAN USE ADMIN COMMANDS
const ADMIN_ID = '1037768611126841405';
let botAdmins = [ADMIN_ID];
const PREFIX = '!'; // Changed from / to ! to avoid Discord slash command conflicts

console.log('🚀 Starting BlazeNode Discord Bot...');
console.log('👑 Admin User ID:', ADMIN_ID);
console.log('🔧 Command Prefix:', PREFIX);

// MongoDB connection with better error handling
mongoose.connect(process.env.MONGODB_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
    serverSelectionTimeoutMS: 5000,
    socketTimeoutMS: 45000,
})
.then(() => {
    console.log('✅ MongoDB Connected Successfully');
    console.log('📊 Database Name:', mongoose.connection.db.databaseName);
    console.log('🔗 Connection State:', mongoose.connection.readyState);
})
.catch(err => {
    console.error('❌ MongoDB Connection Failed:', err.message);
    console.error('❌ MongoDB URI:', process.env.MONGODB_URI ? 'Present' : 'Missing');
    process.exit(1);
});

// MongoDB connection events
mongoose.connection.on('connected', () => {
    console.log('🔗 Mongoose connected to MongoDB');
});

mongoose.connection.on('error', (err) => {
    console.error('❌ Mongoose connection error:', err);
});

mongoose.connection.on('disconnected', () => {
    console.log('🔌 Mongoose disconnected from MongoDB');
});

// Discord bot setup
const bot = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.DirectMessages
    ]
});

// Commands collection
bot.commands = new Collection();

// Load commands from folders
function loadCommands() {
    try {
        const commandFolders = ['user', 'admin'];
        
        for (const folder of commandFolders) {
            const commandsPath = path.join(__dirname, 'commands', folder);
            
            if (!fs.existsSync(commandsPath)) {
                console.log(`⚠️ Commands folder not found: ${commandsPath}`);
                continue;
            }
            
            const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));
            
            for (const file of commandFiles) {
                try {
                    const filePath = path.join(commandsPath, file);
                    delete require.cache[require.resolve(filePath)]; // Clear cache
                    const command = require(filePath);
                    
                    if ('name' in command && 'execute' in command) {
                        bot.commands.set(command.name, command);
                        console.log(`📝 Loaded command: ${command.name} (${folder})`);
                    } else {
                        console.log(`⚠️ Command ${file} is missing required properties.`);
                    }
                } catch (error) {
                    console.error(`❌ Error loading command ${file}:`, error.message);
                }
            }
        }
        console.log(`✅ Total commands loaded: ${bot.commands.size}`);
    } catch (error) {
        console.error('❌ Error loading commands:', error);
    }
}

// Load all commands
loadCommands();

bot.once('ready', async () => {
    try {
        const User = require('./models/User');
        const userCount = await User.countDocuments();
        
        console.log('✅ Bot Online:', bot.user.tag);
        console.log('🔧 Guilds:', bot.guilds.cache.size);
        console.log('👥 Users in DB:', userCount);
        console.log('📝 Commands loaded:', bot.commands.size);
        console.log(`🎯 Ready! Use ${PREFIX}help to see commands`);
        
        // Set bot status
        bot.user.setActivity(`${PREFIX}help | BlazeNode Dashboard`, { type: 'WATCHING' });
        
        // Sync with dashboard
        try {
            await syncWithDashboard();
        } catch (error) {
            console.error('❌ Dashboard sync failed:', error.message);
        }
    } catch (error) {
        console.error('❌ Error in ready event:', error);
    }
});

bot.on('messageCreate', async (message) => {
    try {
        // Skip bots and non-commands
        if (message.author.bot) return;
        if (!message.content.startsWith(PREFIX)) return;

        // Parse command and arguments
        const args = message.content.slice(PREFIX.length).trim().split(/ +/);
        const commandName = args.shift().toLowerCase();
        const isAdmin = message.author.id === ADMIN_ID || botAdmins.includes(message.author.id);

        console.log(`📨 Command: ${PREFIX}${commandName} | User: ${message.author.username} (${message.author.id}) | Admin: ${isAdmin}`);
        console.log(`📋 Args: [${args.join(', ')}]`);

        // Get command
        const command = bot.commands.get(commandName);
        if (!command) {
            console.log(`❌ Command not found: ${commandName}`);
            return message.reply(`❌ **Unknown command:** \`${PREFIX}${commandName}\`\\nUse \`${PREFIX}help\` to see all available commands.`);
        }

        console.log(`✅ Command found: ${command.name}, Admin only: ${command.adminOnly}`);

        // Check admin permissions
        if (command.adminOnly && !isAdmin) {
            console.log(`❌ Access denied for user ${message.author.id}`);
            return message.reply(`❌ **Access Denied!**\\nOnly <@${ADMIN_ID}> and authorized admins can use this command.`);
        }

        console.log(`🚀 Executing command: ${command.name}`);

        // Execute command with proper parameters
        await command.execute(message, args, isAdmin, bot, botAdmins);
        
        console.log(`✅ Command executed successfully: ${command.name}`);
        
    } catch (error) {
        console.error('❌ Message handler error:', error);
        console.error('❌ Stack trace:', error.stack);
        
        try {
            await message.reply(`❌ **Error:** ${error.message}\\n*Check console for details.*`);
        } catch (replyError) {
            console.error('❌ Could not send error message:', replyError);
        }
    }
});

// Enhanced error handling
bot.on('error', (error) => {
    console.error('❌ Discord.js error:', error);
});

bot.on('warn', (warning) => {
    console.warn('⚠️ Discord.js warning:', warning);
});

bot.on('shardError', (error) => {
    console.error('❌ Shard error:', error);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
});

process.on('uncaughtException', (error) => {
    console.error('❌ Uncaught Exception:', error);
    process.exit(1);
});

// Dashboard sync function
async function syncWithDashboard() {
    try {
        const response = await dashboardAPI.get('/api/debug/users');
        const dashboardUsers = response.data.users || [];
        
        console.log(`🔄 Synced with dashboard: ${dashboardUsers.length} users`);
        return dashboardUsers;
    } catch (error) {
        console.error('❌ Dashboard sync error:', error.message);
        return [];
    }
}

// Function to create dashboard user from Discord
async function createDashboardUser(discordUser, initialCoins = 100) {
    try {
        const response = await dashboardAPI.post('/api/bot/create-user', {
            username: discordUser.username,
            discordId: discordUser.id,
            coins: initialCoins
        });
        
        if (response.data.success) {
            console.log(`✅ Created dashboard user: ${discordUser.username}`);
            return response.data.user;
        }
    } catch (error) {
        console.error('❌ Failed to create dashboard user:', error.message);
    }
    return null;
}

// Function to give coins via dashboard
async function giveDashboardCoins(username, coins) {
    try {
        const response = await dashboardAPI.post('/api/bot/give-coins', {
            username,
            coins
        });
        
        if (response.data.success) {
            console.log(`✅ Gave ${coins} coins to ${username}`);
            return response.data;
        }
    } catch (error) {
        console.error('❌ Failed to give coins:', error.message);
    }
    return null;
}

// Export functions for use in commands
bot.dashboardAPI = dashboardAPI;
bot.syncWithDashboard = syncWithDashboard;
bot.createDashboardUser = createDashboardUser;
bot.giveDashboardCoins = giveDashboardCoins;

// Login with better error handling
console.log('🔑 Attempting to login...');
bot.login(process.env.DISCORD_BOT_TOKEN)
    .then(() => {
        console.log('🔑 Bot login successful');
        console.log('🤖 BlazeNode Discord Bot is now online!');
    })
    .catch(err => {
        console.error('❌ Bot login failed:', err);
        console.error('❌ Token:', process.env.DISCORD_BOT_TOKEN ? 'Present' : 'Missing');
        process.exit(1);
    });