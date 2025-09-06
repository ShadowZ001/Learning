const { EmbedBuilder } = require('discord.js');
const User = require('../../models/User');

module.exports = {
    name: 'coins',
    description: 'Check coin balance',
    usage: '!coins <username>',
    adminOnly: false,
    async execute(message, args) {
        const username = args[0];
        if (!username) {
            return message.reply('❌ **Usage:** `!coins <username>`\n**Example:** `!coins john123`');
        }

        try {
            const user = await User.findOne({ username: username });
            if (!user) {
                return message.reply(`❌ **User not found:** "${username}"\nMake sure the username is correct.`);
            }

            const embed = new EmbedBuilder()
                .setColor(0xF59E0B)
                .setTitle('💰 Coin Balance')
                .setDescription(`**${username}** has **${user.coins}** BlazeCoins`)
                .addFields(
                    { name: '💰 Coins', value: user.coins.toString(), inline: true },
                    { name: '🖥️ Servers', value: (user.serverCount || 0).toString(), inline: true },
                    { name: '🔥 Streak', value: user.dailyRewardStreak.toString(), inline: true },
                    { name: '📅 Last Login', value: user.lastLogin ? user.lastLogin.toDateString() : 'Never', inline: true },
                    { name: '📊 Created', value: user.createdAt.toDateString(), inline: true },
                    { name: '👤 Created By', value: `<@${user.createdBy}>`, inline: true }
                )
                .setFooter({ text: 'BlazeNode Dashboard' })
                .setTimestamp();

            return message.reply({ embeds: [embed] });
        } catch (error) {
            console.error('Coins command error:', error);
            return message.reply('❌ **Error:** Could not fetch user data from database.');
        }
    }
};