const User = require('../../models/User');

module.exports = {
    name: 'delete',
    description: 'Delete a user',
    usage: '!delete <username>',
    adminOnly: true,
    async execute(message, args) {
        const username = args[0];
        if (!username) {
            return message.reply('❌ **Usage:** `!delete <username>`\n**Example:** `!delete john123`');
        }

        try {
            const user = await User.findOneAndDelete({ username: username });
            if (!user) {
                return message.reply(`❌ **User not found:** "${username}"`);
            }

            console.log(`🗑️ User deleted: ${username} by ${message.author.username}`);
            return message.reply(`✅ **User deleted:** "${username}" has been permanently removed from the database.`);
        } catch (error) {
            console.error('Delete command error:', error);
            return message.reply('❌ **Error:** Could not delete user from database.');
        }
    }
};