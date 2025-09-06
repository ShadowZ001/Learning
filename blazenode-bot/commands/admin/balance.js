const User = require('../../models/User');

module.exports = {
    name: 'balance',
    description: 'Check user balance',
    usage: '!balance <username>',
    adminOnly: true,
    async execute(message, args) {
        const username = args[0];
        if (!username) {
            return message.reply('❌ **Usage:** `!balance <username>`\n**Example:** `!balance john123`');
        }

        try {
            const user = await User.findOne({ username: username });
            if (!user) {
                return message.reply(`❌ **User not found:** "${username}"`);
            }

            return message.reply(`💰 **${username}** has **${user.coins}** BlazeCoins`);
        } catch (error) {
            console.error('Balance command error:', error);
            return message.reply('❌ **Error:** Could not fetch user balance from database.');
        }
    }
};