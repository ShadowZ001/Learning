const User = require('../../models/User');

module.exports = {
    name: 'checkuser',
    description: 'Check specific user details',
    usage: '!checkuser <username>',
    adminOnly: true,
    async execute(message, args) {
        const username = args[0];
        if (!username) {
            return message.reply('❌ **Usage:** `!checkuser <username>`\n**Example:** `!checkuser shadow`');
        }

        try {
            const user = await User.findOne({ username: username });
            
            if (!user) {
                return message.reply(`❌ **User "${username}" not found in database!**`);
            }

            const userInfo = `🔍 **User Details for "${username}":**

**📋 Basic Info:**
👤 Username: \`${user.username}\`
🔑 Password: \`${user.password}\`
💰 Coins: ${user.coins}
🖥️ Servers: ${user.serverCount || 0}

**📊 Activity:**
🔥 Daily Streak: ${user.dailyRewardStreak}
🕐 Last Login: ${user.lastLogin ? user.lastLogin.toDateString() : 'Never'}
📅 Last Reward: ${user.lastDailyReward ? user.lastDailyReward.toDateString() : 'Never'}

**🔧 Technical:**
🆔 Database ID: \`${user._id}\`
🎮 Pterodactyl ID: ${user.pterodactylUserId || 'Not created'}
👑 Created By: <@${user.createdBy}>
📅 Created: ${user.createdAt.toDateString()}
📝 Updated: ${user.updatedAt.toDateString()}

**🧪 Login Test:**
Try logging in with:
Username: \`${user.username}\`
Password: \`${user.password}\``;

            return message.reply(userInfo);
            
        } catch (error) {
            console.error('Check user error:', error);
            return message.reply(`❌ **Error:** ${error.message}`);
        }
    }
};