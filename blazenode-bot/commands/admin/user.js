const { EmbedBuilder } = require('discord.js');
const User = require('../../models/User');

module.exports = {
    name: 'user',
    description: 'Get detailed user information',
    usage: '/user <username>',
    adminOnly: true,
    async execute(message, args) {
        const username = args[0];
        if (!username) {
            return message.reply('❌ **Usage:** `/user <username>`\n**Example:** `/user john123`');
        }

        try {
            const user = await User.findOne({ username: username });
            if (!user) {
                return message.reply(`❌ **User not found:** "${username}"`);
            }

            const embed = new EmbedBuilder()
                .setColor(0x8B5CF6)
                .setTitle('👤 User Profile')
                .setDescription(`**Detailed information for ${username}**`)
                .addFields(
                    { name: '👤 Username', value: user.username, inline: true },
                    { name: '💰 Coins', value: user.coins.toString(), inline: true },
                    { name: '🖥️ Servers', value: (user.serverCount || 0).toString(), inline: true },
                    { name: '🔥 Daily Streak', value: user.dailyRewardStreak.toString(), inline: true },
                    { name: '📅 Created', value: user.createdAt.toDateString(), inline: true },
                    { name: '🕐 Last Login', value: user.lastLogin ? user.lastLogin.toDateString() : 'Never', inline: true },
                    { name: '🆔 Database ID', value: user._id.toString().slice(-8), inline: true },
                    { name: '🎮 Pterodactyl ID', value: user.pterodactylUserId ? user.pterodactylUserId.toString() : 'Not created', inline: true },
                    { name: '👑 Created By', value: `<@${user.createdBy}>`, inline: true }
                )
                .setTimestamp();

            return message.reply({ embeds: [embed] });
        } catch (error) {
            console.error('User info command error:', error);
            return message.reply('❌ **Error:** Could not fetch user information from database.');
        }
    }
};