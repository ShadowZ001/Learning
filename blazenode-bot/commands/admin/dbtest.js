const mongoose = require('mongoose');
const User = require('../../models/User');

module.exports = {
    name: 'dbtest',
    description: 'Test database connection',
    usage: '!dbtest',
    adminOnly: true,
    async execute(message, args) {
        try {
            console.log('🔍 Testing database connection...');
            
            // Check mongoose connection
            const dbState = mongoose.connection.readyState;
            const states = {
                0: 'Disconnected',
                1: 'Connected',
                2: 'Connecting',
                3: 'Disconnecting'
            };
            
            console.log(`📊 Database state: ${states[dbState]} (${dbState})`);
            
            if (dbState !== 1) {
                return message.reply(`❌ **Database not connected!** State: ${states[dbState]}`);
            }
            
            // Test user count
            const userCount = await User.countDocuments();
            console.log(`👥 Total users in database: ${userCount}`);
            
            // Test creating a simple document (without saving)
            const testUser = new User({
                username: 'test_user_' + Date.now(),
                password: 'test_password',
                coins: 100,
                createdBy: message.author.id
            });
            
            // Validate without saving
            const validationError = testUser.validateSync();
            if (validationError) {
                console.log('❌ Validation error:', validationError);
                return message.reply(`❌ **Validation Error:** ${validationError.message}`);
            }
            
            return message.reply(`✅ **Database Test Passed!**\n📊 Connection: ${states[dbState]}\n👥 Users: ${userCount}\n✅ Model validation: OK`);
            
        } catch (error) {
            console.error('❌ Database test error:', error);
            return message.reply(`❌ **Database Test Failed:** ${error.message}`);
        }
    }
};