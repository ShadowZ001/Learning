const { EmbedBuilder } = require('discord.js');
const User = require('../../models/User');

module.exports = {
    name: 'logs',
    description: 'View bot statistics and logs',
    usage: '/logs',
    adminOnly: true,
    async execute(message, args, isAdmin, bot) {
        try {
            const totalUsers = await User.countDocuments();
            const recentUsers = await User.countDocuments({ 
                createdAt: { $gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) } 
            });
            const activeUsers = await User.countDocuments({ 
                lastLogin: { $gte: new Date(Date.now() - 24 * 60 * 60 * 1000) } 
            });

            const embed = new EmbedBuilder()
                .setColor(0x6B7280)
                .setTitle('📊 Bot Statistics & Logs')
                .setDescription('**System Status & Analytics**')
                .addFields(
                    { name: '🟢 Bot Status', value: 'Online & Ready', inline: true },
                    { name: '⏱️ Uptime', value: `${Math.floor(bot.uptime / 1000 / 60)} minutes`, inline: true },
                    { name: '🏓 Ping', value: `${bot.ws.ping}ms`, inline: true },
                    { name: '👥 Total Users', value: totalUsers.toString(), inline: true },
                    { name: '🆕 New (7 days)', value: recentUsers.toString(), inline: true },
                    { name: '🔥 Active (24h)', value: activeUsers.toString(), inline: true },
                    { name: '🏰 Guilds', value: bot.guilds.cache.size.toString(), inline: true },
                    { name: '📊 Database', value: 'MongoDB Connected', inline: true },
                    { name: '🤖 Version', value: '2.1.0', inline: true }
                )
                .setFooter({ text: `Requested by ${message.author.username}` })
                .setTimestamp();

            return message.reply({ embeds: [embed] });
        } catch (error) {
            console.error('Logs command error:', error);
            return message.reply('❌ **Error:** Could not fetch bot statistics.');
        }
    }
};