const User = require('../../models/User');

module.exports = {
    name: 'deleteall',
    description: 'Delete all users (DANGER)',
    usage: '!deleteall CONFIRM',
    adminOnly: true,
    async execute(message, args) {
        const confirmation = args[0];
        
        if (confirmation !== 'CONFIRM') {
            return message.reply('❌ **Usage:** `!deleteall CONFIRM`\n⚠️ **WARNING:** This will delete ALL users from database!');
        }

        try {
            const result = await User.deleteMany({});
            console.log(`🗑️ Deleted ${result.deletedCount} users by ${message.author.username}`);
            return message.reply(`✅ **Deleted ${result.deletedCount} users from database.**`);
            
        } catch (error) {
            console.error('Delete all users error:', error);
            return message.reply(`❌ **Error:** ${error.message}`);
        }
    }
};