const User = require('../../models/User');

module.exports = {
    name: 'testlogin',
    description: 'Test login credentials for dashboard',
    usage: '!testlogin <username> <password>',
    adminOnly: true,
    async execute(message, args) {
        const username = args[0];
        const password = args[1];

        if (!username || !password) {
            return message.reply('❌ **Usage:** `!testlogin <username> <password>`\n**Example:** `!testlogin shadow mypass123`');
        }

        try {
            console.log('🧪 Testing login credentials...');
            
            // Check if user exists
            const user = await User.findOne({ username: username });
            if (!user) {
                return message.reply(`❌ **User "${username}" not found in database!**`);
            }

            // Test password match
            const passwordMatch = user.password === password;
            
            const testResult = `🧪 **Login Test Results for "${username}":**

**Database Check:**
✅ User exists in database
🆔 Database ID: \`${user._id}\`
📅 Created: ${user.createdAt.toDateString()}

**Credential Check:**
👤 Username: \`${user.username}\`
🔑 Stored Password: \`${user.password}\`
🔑 Test Password: \`${password}\`
${passwordMatch ? '✅' : '❌'} Password Match: ${passwordMatch ? 'YES' : 'NO'}

**User Data:**
💰 Coins: ${user.coins}
🖥️ Servers: ${user.serverCount || 0}
🎮 Pterodactyl ID: ${user.pterodactylUserId || 'Not created'}
👑 Created By: <@${user.createdBy}>

**Dashboard Login:**
${passwordMatch ? '✅ Should work' : '❌ Will fail - password mismatch'}

**Test URL:** http://localhost:5503
**Login with:** Username: \`${user.username}\` | Password: \`${user.password}\``;

            return message.reply(testResult);
            
        } catch (error) {
            console.error('Test login error:', error);
            return message.reply(`❌ **Error:** ${error.message}`);
        }
    }
};