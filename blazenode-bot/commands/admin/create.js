const { EmbedBuilder } = require('discord.js');
const User = require('../../models/User');

module.exports = {
    name: 'create',
    description: 'Create a new user',
    usage: '!create <username> <password>',
    adminOnly: true,
    async execute(message, args) {
        const username = args[0];
        const password = args[1];

        console.log(`🔧 Create command called with args: [${args.join(', ')}]`);
        console.log(`👤 Username: ${username}, Password: ${password}`);

        if (!username || !password) {
            console.log('❌ Missing username or password');
            return message.reply('❌ **Usage:** `!create <username> <password>`\n**Example:** `!create john123 mypassword`');
        }

        try {
            console.log('🔍 Checking if user exists...');
            // Check if user exists
            const existing = await User.findOne({ username: username });
            if (existing) {
                console.log(`❌ User ${username} already exists`);
                return message.reply(`❌ **User already exists:** "${username}"\nTry a different username.`);
            }

            console.log('✅ User does not exist, creating new user...');
            
            // Create user object
            const userData = {
                username: username,
                password: password,
                coins: 100,
                serverCount: 0,
                dailyRewardStreak: 0,
                createdBy: message.author.id
            };
            
            console.log('📝 User data to save:', userData);

            // Create and save user
            const newUser = new User(userData);
            console.log('💾 Saving user to database...');
            
            const savedUser = await newUser.save();
            console.log('✅ User saved successfully:', savedUser._id);

            const embed = new EmbedBuilder()
                .setColor(0x10B981)
                .setTitle('✅ User Created Successfully!')
                .setDescription(`New user **${username}** has been created!`)
                .addFields(
                    { name: '👤 Username', value: username, inline: true },
                    { name: '🔑 Password', value: password, inline: true },
                    { name: '💰 Starting Coins', value: '100', inline: true },
                    { name: '👑 Created By', value: `<@${message.author.id}>`, inline: true },
                    { name: '📅 Created At', value: new Date().toDateString(), inline: true },
                    { name: '🆔 User ID', value: savedUser._id.toString().slice(-8), inline: true }
                )
                .setFooter({ text: 'User can now login to dashboard' })
                .setTimestamp();

            return message.reply({ embeds: [embed] });
            
        } catch (error) {
            console.error('❌ Create user error details:', error);
            console.error('❌ Error name:', error.name);
            console.error('❌ Error message:', error.message);
            console.error('❌ Error stack:', error.stack);
            
            // Check specific error types
            if (error.name === 'ValidationError') {
                return message.reply(`❌ **Validation Error:** ${error.message}`);
            } else if (error.code === 11000) {
                return message.reply(`❌ **Duplicate Error:** Username "${username}" already exists!`);
            } else if (error.name === 'MongoNetworkError') {
                return message.reply('❌ **Database Connection Error:** Cannot connect to database.');
            } else {
                return message.reply(`❌ **Database Error:** ${error.message}\n*Check console for details.*`);
            }
        }
    }
};