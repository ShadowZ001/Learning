const { Client, GatewayIntentBits, Collection, PermissionsBitField, SlashCommandBuilder, REST, Routes } = require('discord.js');
const mongoose = require('mongoose');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

// AI Configuration
const AIConfig = require('./models/AIConfig');

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
const PREFIX = '>'; // Main bot prefix

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
                        console.log(`📝 Loaded command: ${command.name} (${folder}) - Admin: ${command.adminOnly}`);
                        if (command.aliases) {
                            console.log(`   🔗 Aliases: ${command.aliases.join(', ')}`);
                        }
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
        let userCount = 0;
        try {
            const User = require('./models/User');
            userCount = await User.countDocuments();
        } catch (error) {
            console.log('⚠️ User model not available:', error.message);
        }
        
        console.log('✅ Bot Online:', bot.user.tag);
        console.log('🔧 Guilds:', bot.guilds.cache.size);
        console.log('👥 Users in DB:', userCount);
        console.log('📝 Commands loaded:', bot.commands.size);
        console.log(`🎯 Ready! Use ${PREFIX}help to see commands`);
        
        // Register slash commands
        const commands = [
            new SlashCommandBuilder()
                .setName('ai')
                .setDescription('AI setup and configuration')
                .setDefaultMemberPermissions(PermissionsBitField.Flags.Administrator),
            new SlashCommandBuilder()
                .setName('levelup')
                .setDescription('Level system configuration')
                .addStringOption(option =>
                    option.setName('mode')
                        .setDescription('Setup mode')
                        .addChoices(
                            { name: 'Normal Setup', value: 'normal' },
                            { name: 'Canvacard Setup', value: 'canva' }
                        ))
                .setDefaultMemberPermissions(PermissionsBitField.Flags.Administrator)
        ];
        
        const rest = new REST().setToken(process.env.DISCORD_BOT_TOKEN);
        
        try {
            console.log('🔄 Registering slash commands...');
            await rest.put(
                Routes.applicationCommands(bot.user.id),
                { body: commands }
            );
            console.log('✅ Slash commands registered successfully');
        } catch (error) {
            console.error('❌ Failed to register slash commands:', error);
        }
        
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
        // Skip bots
        if (message.author.bot) return;
        
        console.log(`📨 Message received: "${message.content}" from ${message.author.username}`);
        console.log(`🔍 Starts with prefix (${PREFIX}): ${message.content.startsWith(PREFIX)}`);
        console.log(`👑 User permissions: ${message.member?.permissions.has(PermissionsBitField.Flags.Administrator) ? 'Admin' : 'Not Admin'}`);
        console.log(`🏠 Guild: ${message.guild?.name || 'DM'}`);
        console.log('---');
        
        const isAdmin = message.author.id === ADMIN_ID || botAdmins.includes(message.author.id) || message.member?.permissions.has(PermissionsBitField.Flags.Administrator);
        
        // Check if user is premium
        let isPremium = false;
        // Skip premium check for now
        
        let commandName, args, hasPrefix = false;
        
        // Check for prefix command
        if (message.content.startsWith(PREFIX)) {
            hasPrefix = true;
            args = message.content.slice(PREFIX.length).trim().split(/ +/);
            commandName = args.shift().toLowerCase();
            console.log(`🔍 Prefix command detected: ${commandName}`);
        }
        // Check for premium no-prefix command (single letter A-Z, a-z)
        else if (isPremium && /^[A-Za-z]( |$)/.test(message.content)) {
            args = message.content.trim().split(/ +/);
            commandName = args.shift().toLowerCase();
        }
        // Not a command - check for AI response
        else {
            await handleAIResponse(message);
            return;
        }

        console.log(`📨 Command: ${hasPrefix ? PREFIX : ''}${commandName} | User: ${message.author.username} (${message.author.id}) | Admin: ${isAdmin} | Premium: ${isPremium}`);
        console.log(`📋 Args: [${args.join(', ')}]`);

        // Get command (check aliases too)
        const command = bot.commands.get(commandName) || bot.commands.find(cmd => cmd.aliases && cmd.aliases.includes(commandName));
        if (!command) {
            console.log(`❌ Command not found: ${commandName}`);
            return message.reply(`❌ **Unknown command:** \`${hasPrefix ? PREFIX : ''}${commandName}\`\\nUse \`${PREFIX}help\` to see all available commands.`);
        }

        console.log(`✅ Command found: ${command.name}, Admin only: ${command.adminOnly}, Premium only: ${command.premiumOnly}`);

        // Check admin permissions
        if (command.adminOnly && !isAdmin) {
            console.log(`❌ Access denied for user ${message.author.id}`);
            return message.reply(`❌ **Access Denied!**\\nOnly <@${ADMIN_ID}> and authorized admins can use this command.`);
        }
        
        // Check premium permissions
        if (command.premiumOnly && !isPremium && !isAdmin) {
            console.log(`❌ Premium access denied for user ${message.author.id}`);
            return message.reply(`❌ **Premium Required!**\\nThis command is only available for premium users. Contact <@${ADMIN_ID}> for premium access.`);
        }

        console.log(`🚀 Executing command: ${command.name}`);

        // Execute command with proper parameters
        await command.execute(message, args, isAdmin, bot, botAdmins, isPremium);
        
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



// Slash command handler
bot.on('interactionCreate', async (interaction) => {
    if (!interaction.isChatInputCommand()) return;
    
    const isAdmin = interaction.member?.permissions.has(PermissionsBitField.Flags.Administrator);
    
    if (!isAdmin) {
        return interaction.reply({ content: '❌ **Access Denied!** Only administrators can use this command.', ephemeral: true });
    }
    
    // Create fake message object for compatibility
    const fakeMessage = {
        author: interaction.user,
        guild: interaction.guild,
        channel: interaction.channel,
        member: interaction.member,
        reply: async (options) => {
            if (interaction.replied || interaction.deferred) {
                return interaction.followUp(options);
            } else {
                return interaction.reply(options);
            }
        }
    };
    
    try {
        if (interaction.commandName === 'ai') {
            const aiCommand = require('./commands/admin/ai.js');
            await aiCommand.execute(fakeMessage, []);
        } else if (interaction.commandName === 'levelup') {
            const levelupCommand = require('./commands/admin/levelup.js');
            const mode = interaction.options.getString('mode') || 'normal';
            const args = mode === 'canva' ? ['canva'] : [];
            await levelupCommand.execute(fakeMessage, args);
        }
    } catch (error) {
        console.error('❌ Slash command error:', error);
        const errorMsg = { content: '❌ An error occurred while executing the command.', ephemeral: true };
        if (interaction.replied || interaction.deferred) {
            await interaction.followUp(errorMsg);
        } else {
            await interaction.reply(errorMsg);
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

// AI Response Handler
async function handleAIResponse(message) {
    try {
        if (!message.guild) return;
        
        const config = await AIConfig.findOne({ guildId: message.guild.id });
        if (!config || !config.enabled || !config.channelId) return;
        
        if (message.channel.id !== config.channelId) return;
        
        // Skip if message starts with prefix (it's a command)
        if (message.content.startsWith('>')) return;
        
        // Show typing indicator
        await message.channel.sendTyping();
        
        const response = await axios.post('https://api.aichatos.cloud/api/generateContent', {
            model: 'gemini-2.5-pro',
            prompt: `You are a helpful AI assistant in a Discord server. Keep responses concise and friendly.\n\nUser: ${message.content}`,
            max_tokens: 500
        }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const aiResponse = response.data.response || response.data.text || response.data.content;
        
        // Split long messages
        if (aiResponse.length > 2000) {
            const chunks = aiResponse.match(/[\s\S]{1,2000}/g);
            for (const chunk of chunks) {
                await message.reply(chunk);
            }
        } else {
            await message.reply(aiResponse);
        }
        
    } catch (error) {
        console.error('❌ AI Response Error:', error.message);
        if (error.response?.status === 401) {
            await message.reply('❌ AI service authentication failed. Please check API key.');
        } else if (error.response?.status === 429) {
            await message.reply('❌ AI service rate limit reached. Please try again later.');
        } else {
            await message.reply('❌ AI service temporarily unavailable.');
        }
    }
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