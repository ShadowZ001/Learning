const { EmbedBuilder } = require('discord.js');
const User = require('../../models/User');

module.exports = {
    name: 'users',
    description: 'List all users',
    usage: '/users',
    adminOnly: true,
    async execute(message, args) {
        try {
            const users = await User.find({}).select('username coins serverCount createdAt').sort({ createdAt: -1 }).limit(20);

            if (users.length === 0) {
                return message.reply('❌ **No users found in database!**');
            }

            const embed = new EmbedBuilder()
                .setColor(0x3B82F6)
                .setTitle('📋 User Database')
                .setDescription(`**Total Users:** ${users.length}`)
                .setTimestamp();

            users.forEach((user, index) => {
                embed.addFields({
                    name: `${index + 1}. ${user.username}`,
                    value: `💰 ${user.coins} coins | 🖥️ ${user.serverCount || 0} servers | 📅 ${user.createdAt.toDateString()}`,
                    inline: false
                });
            });

            return message.reply({ embeds: [embed] });
        } catch (error) {
            console.error('Users command error:', error);
            return message.reply('❌ **Error:** Could not fetch users from database.');
        }
    }
};