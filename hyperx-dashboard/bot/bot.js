require('dotenv').config();
const { Client, GatewayIntentBits, EmbedBuilder, PermissionsBitField } = require('discord.js');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers
    ]
});

client.once('ready', () => {
    console.log(`✅ Bot is online as ${client.user.tag}`);
    console.log(`🔗 Invite link: https://discord.com/api/oauth2/authorize?client_id=${client.user.id}&permissions=8&scope=bot`);
    
    // Set bot status
    client.user.setActivity('HyperX Dashboard', { type: 'WATCHING' });
});

// Welcome new members
client.on('guildMemberAdd', member => {
    const welcomeEmbed = new EmbedBuilder()
        .setColor('#ff6b35')
        .setTitle('🎮 Welcome to HyperX!')
        .setDescription(`Welcome ${member.user}, to **${member.guild.name}**!`)
        .addFields(
            { name: '🚀 Get Started', value: 'Visit our dashboard to create your free game server!' },
            { name: '🔗 Dashboard', value: 'http://localhost:4000' },
            { name: '📋 Rules', value: 'Please read our server rules and have fun!' }
        )
        .setThumbnail(member.user.displayAvatarURL())
        .setTimestamp()
        .setFooter({ text: 'HyperX Game Hosting', iconURL: client.user.displayAvatarURL() });

    // Try to send welcome message to system channel or first available channel
    const channel = member.guild.systemChannel || member.guild.channels.cache.find(ch => ch.type === 0);
    if (channel) {
        channel.send({ embeds: [welcomeEmbed] });
    }
});

// Basic commands
client.on('messageCreate', message => {
    if (message.author.bot) return;

    const prefix = '!';
    if (!message.content.startsWith(prefix)) return;

    const args = message.content.slice(prefix.length).trim().split(/ +/);
    const command = args.shift().toLowerCase();

    switch (command) {
        case 'ping':
            message.reply(`🏓 Pong! Latency: ${Date.now() - message.createdTimestamp}ms`);
            break;

        case 'dashboard':
            const dashboardEmbed = new EmbedBuilder()
                .setColor('#ff6b35')
                .setTitle('🎮 HyperX Dashboard')
                .setDescription('Access your game server management dashboard!')
                .addFields(
                    { name: '🔗 Dashboard URL', value: 'http://localhost:4000' },
                    { name: '🎯 Features', value: '• Create game servers\n• File management\n• Server console\n• Analytics\n• DDoS protection' }
                )
                .setTimestamp();
            message.reply({ embeds: [dashboardEmbed] });
            break;

        case 'help':
            const helpEmbed = new EmbedBuilder()
                .setColor('#ff6b35')
                .setTitle('🤖 HyperX Bot Commands')
                .setDescription('Here are the available commands:')
                .addFields(
                    { name: '!ping', value: 'Check bot latency' },
                    { name: '!dashboard', value: 'Get dashboard link and info' },
                    { name: '!help', value: 'Show this help message' },
                    { name: '!serverinfo', value: 'Show server information' }
                )
                .setTimestamp();
            message.reply({ embeds: [helpEmbed] });
            break;

        case 'serverinfo':
            const serverEmbed = new EmbedBuilder()
                .setColor('#ff6b35')
                .setTitle(`📊 ${message.guild.name} Server Info`)
                .setThumbnail(message.guild.iconURL())
                .addFields(
                    { name: '👑 Owner', value: `<@${message.guild.ownerId}>`, inline: true },
                    { name: '👥 Members', value: `${message.guild.memberCount}`, inline: true },
                    { name: '📅 Created', value: `<t:${Math.floor(message.guild.createdTimestamp / 1000)}:F>`, inline: true },
                    { name: '🔒 Verification Level', value: `${message.guild.verificationLevel}`, inline: true },
                    { name: '📝 Channels', value: `${message.guild.channels.cache.size}`, inline: true },
                    { name: '😀 Emojis', value: `${message.guild.emojis.cache.size}`, inline: true }
                )
                .setTimestamp();
            message.reply({ embeds: [serverEmbed] });
            break;
    }
});

// Error handling
client.on('error', error => {
    console.error('Discord client error:', error);
});

process.on('unhandledRejection', error => {
    console.error('Unhandled promise rejection:', error);
});

// Login to Discord
client.login(process.env.DISCORD_BOT_TOKEN);