const { EmbedBuilder } = require('discord.js');
const User = require('../../models/User');

module.exports = {
    name: 'newuser',
    description: 'Create a completely new user (deletes existing if found)',
    usage: '!newuser <username> <password>',
    adminOnly: true,
    async execute(message, args) {
        const username = args[0];
        const password = args[1];

        if (!username || !password) {
            return message.reply('❌ **Usage:** `!newuser <username> <password>`\n**Example:** `!newuser shadow mypass123`');
        }

        try {
            // Delete existing user if found
            const existingUser = await User.findOneAndDelete({ username: username });
            if (existingUser) {
                console.log(`🗑️ Deleted existing user: ${username}`);
            }

            // Create completely new user
            const newUser = new User({
                username: username,
                password: password,
                coins: 100,
                serverCount: 0,
                dailyRewardStreak: 0,
                createdBy: message.author.id
            });

            const savedUser = await newUser.save();
            console.log(`✅ Created fresh user: ${username} by ${message.author.username}`);

            const embed = new EmbedBuilder()
                .setColor(0x10B981)
                .setTitle('✅ Fresh User Created!')
                .setDescription(`New user **${username}** created successfully!`)
                .addFields(
                    { name: '👤 Username', value: username, inline: true },
                    { name: '🔑 Password', value: password, inline: true },
                    { name: '💰 Coins', value: '100', inline: true },
                    { name: '🖥️ Servers', value: '0', inline: true },
                    { name: '🆔 Database ID', value: savedUser._id.toString().slice(-8), inline: true },
                    { name: '👑 Created By', value: `<@${message.author.id}>`, inline: true }
                )
                .addFields({
                    name: '🧪 Login Instructions',
                    value: `Go to dashboard and login with:\n**Username:** \`${username}\`\n**Password:** \`${password}\``,
                    inline: false
                })
                .setFooter({ text: 'User can now login to dashboard' })
                .setTimestamp();

            return message.reply({ embeds: [embed] });
            
        } catch (error) {
            console.error('New user creation error:', error);
            return message.reply(`❌ **Error creating user:** ${error.message}`);
        }
    }
};