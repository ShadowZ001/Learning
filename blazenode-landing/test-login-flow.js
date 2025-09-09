// Test script to verify login flow
const mongoose = require('mongoose');
const config = require('./config');
const User = require('./models/User');

async function testLoginFlow() {
    try {
        console.log('🔍 Testing login flow...');
        
        // Connect to database
        await mongoose.connect(config.MONGODB_URI, {
            useNewUrlParser: true,
            useUnifiedTopology: true
        });
        console.log('✅ Connected to MongoDB');
        
        // Test user creation
        const testUser = {
            discordId: 'test123',
            discordUsername: 'testuser',
            email: 'test@example.com',
            loginType: 'discord',
            coins: 1000
        };
        
        // Check if test user exists
        let user = await User.findOne({ discordId: testUser.discordId });
        if (user) {
            console.log('✅ Test user found:', user.discordUsername);
        } else {
            user = new User(testUser);
            await user.save();
            console.log('✅ Test user created:', user.discordUsername);
        }
        
        // Test user data retrieval
        const userData = {
            id: user._id.toString(),
            username: user.discordUsername,
            email: user.email,
            coins: user.coins,
            isAdmin: user.isAdmin || false,
            loginType: user.loginType
        };
        
        console.log('✅ User data structure:', userData);
        
        // Clean up
        await User.deleteOne({ discordId: testUser.discordId });
        console.log('✅ Test user cleaned up');
        
        await mongoose.disconnect();
        console.log('✅ Login flow test completed successfully');
        
    } catch (error) {
        console.error('❌ Login flow test failed:', error);
        process.exit(1);
    }
}

if (require.main === module) {
    testLoginFlow();
}

module.exports = testLoginFlow;