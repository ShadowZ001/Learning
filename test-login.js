const mongoose = require('mongoose');
const config = require('./blazenode-landing/config');
const User = require('./blazenode-landing/models/User');

async function testLogin() {
    try {
        console.log('Connecting to MongoDB...');
        await mongoose.connect(config.MONGODB_URI, {
            useNewUrlParser: true,
            useUnifiedTopology: true
        });
        console.log('✅ Connected to MongoDB');
        
        // Find all users
        const users = await User.find({});
        console.log(`Found ${users.length} users in database:`);
        
        users.forEach(user => {
            console.log(`- Username: "${user.username}" | Password: "${user.password}"`);
        });
        
        // Test login with shadow/shadow06
        console.log('\nTesting login with shadow/shadow06...');
        
        const testUser = await User.findOne({ 
            username: 'shadow',
            password: 'shadow06'
        });
        
        if (testUser) {
            console.log('✅ Direct query found user:', testUser.username);
        } else {
            console.log('❌ Direct query failed');
            
            // Try case insensitive
            const caseInsensitive = await User.findOne({ 
                username: { $regex: /^shadow$/i },
                password: 'shadow06'
            });
            
            if (caseInsensitive) {
                console.log('✅ Case insensitive found user:', caseInsensitive.username);
            } else {
                console.log('❌ Case insensitive also failed');
            }
        }
        
        process.exit(0);
    } catch (error) {
        console.error('❌ Error:', error.message);
        process.exit(1);
    }
}

testLogin();