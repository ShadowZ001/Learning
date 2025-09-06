const User = require('../../models/User');

module.exports = {
    name: 'fixuser',
    description: 'Update user password',
    usage: '!fixuser <username> <newpassword>',
    adminOnly: true,
    async execute(message, args) {
        const username = args[0];
        const newPassword = args[1];
        
        if (!username || !newPassword) {
            return message.reply('❌ **Usage:** `!fixuser <username> <newpassword>`\n**Example:** `!fixuser shadow newpass123`');
        }

        try {
            const user = await User.findOne({ username: username });
            
            if (!user) {
                return message.reply(`❌ **User "${username}" not found in database!**`);
            }

            const oldPassword = user.password;
            user.password = newPassword;
            await user.save();

            console.log(`🔧 Password updated for ${username} by ${message.author.username}`);
            
            return message.reply(`✅ **Password updated for "${username}"**
            
**Old Password:** \`${oldPassword}\`
**New Password:** \`${newPassword}\`

User can now login to dashboard with the new password.`);
            
        } catch (error) {
            console.error('Fix user error:', error);
            return message.reply(`❌ **Error:** ${error.message}`);
        }
    }
};