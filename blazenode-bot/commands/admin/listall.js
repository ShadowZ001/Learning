const User = require('../../models/User');

module.exports = {
    name: 'listall',
    description: 'List all users with passwords (debug)',
    usage: '!listall',
    adminOnly: true,
    async execute(message, args) {
        try {
            const users = await User.find({}).select('username password coins createdBy createdAt').limit(10);
            
            if (users.length === 0) {
                return message.reply('❌ **No users found in database!**');
            }

            let userList = '📋 **All Users in Database:**\n\n';
            users.forEach((user, index) => {
                userList += `**${index + 1}. ${user.username}**\n`;
                userList += `   🔑 Password: \`${user.password}\`\n`;
                userList += `   💰 Coins: ${user.coins}\n`;
                userList += `   👑 Created by: <@${user.createdBy}>\n`;
                userList += `   📅 Created: ${user.createdAt.toDateString()}\n\n`;
            });

            // Split message if too long
            if (userList.length > 2000) {
                const chunks = userList.match(/[\s\S]{1,1900}/g);
                for (const chunk of chunks) {
                    await message.reply(chunk);
                }
            } else {
                return message.reply(userList);
            }
            
        } catch (error) {
            console.error('List all users error:', error);
            return message.reply(`❌ **Error:** ${error.message}`);
        }
    }
};