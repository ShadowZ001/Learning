const { EmbedBuilder } = require('discord.js');
const User = require('../../models/User');

module.exports = {
    name: 'coin',
    description: 'Give or remove coins from user',
    usage: '!coin <give|remove> <username> <amount>',
    adminOnly: true,
    async execute(message, args) {
        const action = args[0];
        const username = args[1];
        const amount = parseInt(args[2]);

        if (!action || !username || !amount || isNaN(amount)) {
            return message.reply('❌ **Usage:** `!coin <give|remove> <username> <amount>`\n**Examples:**\n`!coin give john123 50`\n`!coin remove john123 25`');
        }

        if (action !== 'give' && action !== 'remove') {
            return message.reply('❌ **Invalid action!** Use `give` or `remove`');
        }

        try {
            const user = await User.findOne({ username: username });
            if (!user) {
                return message.reply(`❌ **User not found:** "${username}"`);
            }

            const oldCoins = user.coins;

            if (action === 'give') {
                user.coins += amount;
            } else {
                user.coins = Math.max(0, user.coins - amount);
            }

            await user.save();
            console.log(`💰 ${action} ${amount} coins ${action === 'give' ? 'to' : 'from'} ${username}`);

            const embed = new EmbedBuilder()
                .setColor(action === 'give' ? 0x10B981 : 0xEF4444)
                .setTitle(`💰 Coins ${action === 'give' ? 'Added' : 'Removed'}`)
                .setDescription(`Successfully ${action === 'give' ? 'added' : 'removed'} **${amount}** coins ${action === 'give' ? 'to' : 'from'} **${username}**`)
                .addFields(
                    { name: '👤 User', value: username, inline: true },
                    { name: '💰 Previous', value: oldCoins.toString(), inline: true },
                    { name: '💰 New Balance', value: user.coins.toString(), inline: true },
                    { name: '📊 Change', value: `${action === 'give' ? '+' : '-'}${amount}`, inline: true },
                    { name: '👑 By', value: `<@${message.author.id}>`, inline: true },
                    { name: '📅 Date', value: new Date().toDateString(), inline: true }
                )
                .setTimestamp();

            return message.reply({ embeds: [embed] });
        } catch (error) {
            console.error('Coin command error:', error);
            return message.reply('❌ **Error:** Could not update user coins in database.');
        }
    }
};