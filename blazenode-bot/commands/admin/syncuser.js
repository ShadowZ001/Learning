const User = require('../../models/User');

module.exports = {
    name: 'syncuser',
    description: 'Sync user between bot and dashboard',
    usage: '!syncuser <username> <password>',
    adminOnly: true,
    async execute(message, args) {
        const username = args[0];
        const password = args[1];

        if (!username || !password) {
            return message.reply('❌ **Usage:** `!syncuser <username> <password>`\n**Example:** `!syncuser shadow mypass123`');
        }

        try {
            console.log('🔄 Syncing user between bot and dashboard...');
            
            // Delete any existing user with same username
            await User.deleteMany({ username: username });
            console.log(`🗑️ Deleted any existing users with username: ${username}`);
            
            // Create fresh user with exact credentials
            const userData = {
                username: username,
                password: password,
                coins: 100,
                serverCount: 0,
                dailyRewardStreak: 0,
                pterodactylUserId: null,
                lastLogin: null,
                lastDailyReward: null,
                createdBy: message.author.id,
                createdAt: new Date(),
                updatedAt: new Date()
            };
            
            // Insert directly to avoid any validation issues
            const result = await User.collection.insertOne(userData);
            console.log('✅ User inserted with ID:', result.insertedId);
            
            // Verify the user was created correctly
            const createdUser = await User.findById(result.insertedId);
            
            const syncResult = `🔄 **User Sync Complete!**

**Created User:**
👤 Username: \`${createdUser.username}\`
🔑 Password: \`${createdUser.password}\`
💰 Coins: ${createdUser.coins}
🆔 Database ID: \`${createdUser._id}\`
📅 Created: ${createdUser.createdAt.toDateString()}

**Dashboard Login:**
🌐 URL: http://localhost:5503
👤 Username: \`${createdUser.username}\`
🔑 Password: \`${createdUser.password}\`

**Status:** ✅ Ready for dashboard login!`;

            return message.reply(syncResult);
            
        } catch (error) {
            console.error('Sync user error:', error);
            return message.reply(`❌ **Sync failed:** ${error.message}`);
        }
    }
};