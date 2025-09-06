const User = require('../../models/User');

module.exports = {
    name: 'dbclean',
    description: 'Clean database and show detailed info',
    usage: '!dbclean',
    adminOnly: true,
    async execute(message, args) {
        try {
            console.log('🧹 Cleaning database...');
            
            // Get all users
            const allUsers = await User.find({});
            console.log(`Found ${allUsers.length} users in database`);
            
            // Show detailed user info
            let userInfo = `📊 **Database Status:**\n\n**Total Users:** ${allUsers.length}\n\n`;
            
            if (allUsers.length > 0) {
                userInfo += '**User Details:**\n';
                allUsers.forEach((user, index) => {
                    userInfo += `${index + 1}. **${user.username}**\n`;
                    userInfo += `   🔑 Password: \`${user.password}\`\n`;
                    userInfo += `   💰 Coins: ${user.coins}\n`;
                    userInfo += `   🆔 ID: \`${user._id.toString().slice(-8)}\`\n\n`;
                });
            }
            
            // Check for duplicate usernames
            const usernames = allUsers.map(u => u.username);
            const duplicates = usernames.filter((item, index) => usernames.indexOf(item) !== index);
            
            if (duplicates.length > 0) {
                userInfo += `⚠️ **Duplicate Usernames Found:** ${duplicates.join(', ')}\n\n`;
                
                // Remove duplicates (keep the first one)
                for (const dupUsername of duplicates) {
                    const dupUsers = await User.find({ username: dupUsername });
                    // Delete all but the first one
                    for (let i = 1; i < dupUsers.length; i++) {
                        await User.findByIdAndDelete(dupUsers[i]._id);
                        console.log(`Deleted duplicate user: ${dupUsername} (${dupUsers[i]._id})`);
                    }
                }
                userInfo += `✅ **Duplicates removed!**\n\n`;
            }
            
            // Get updated count
            const finalCount = await User.countDocuments();
            userInfo += `✅ **Final user count:** ${finalCount}`;
            
            // Split message if too long
            if (userInfo.length > 2000) {
                const chunks = userInfo.match(/[\s\S]{1,1900}/g);
                for (const chunk of chunks) {
                    await message.reply(chunk);
                }
            } else {
                return message.reply(userInfo);
            }
            
        } catch (error) {
            console.error('Database clean error:', error);
            return message.reply(`❌ **Error:** ${error.message}`);
        }
    }
};