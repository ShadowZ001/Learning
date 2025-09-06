const { EmbedBuilder } = require('discord.js');
const User = require('../../models/User');

module.exports = {
    name: 'forcecreate',
    description: 'Force create user (bypasses all checks)',
    usage: '!forcecreate <username> <password>',
    adminOnly: true,
    async execute(message, args) {
        const username = args[0];
        const password = args[1];

        if (!username || !password) {
            return message.reply('❌ **Usage:** `!forcecreate <username> <password>`\n**Example:** `!forcecreate hello mypass123`');
        }

        try {
            console.log('🚀 Force creating user...');
            
            // Delete any existing user with same username
            const deleted = await User.deleteMany({ username: username });
            if (deleted.deletedCount > 0) {
                console.log(`🗑️ Deleted ${deleted.deletedCount} existing users with username: ${username}`);
            }
            
            // Clear any problematic indexes first
            try {
                await User.collection.dropIndex('discordId_1');
                console.log('✅ Dropped discordId index');
            } catch (e) {
                console.log('ℹ️ discordId index not found (already dropped)');
            }
            
            // Create user directly with insertOne to bypass mongoose validation issues
            const userData = {
                username: username,
                password: password,
                coins: 100,
                serverCount: 0,
                dailyRewardStreak: 0,
                createdBy: message.author.id,
                createdAt: new Date(),
                updatedAt: new Date()
            };
            
            const result = await User.collection.insertOne(userData);
            console.log('✅ User inserted directly into database:', result.insertedId);
            
            // Verify the user was created
            const createdUser = await User.findById(result.insertedId);
            
            const embed = new EmbedBuilder()
                .setColor(0x10B981)
                .setTitle('✅ User Force Created!')
                .setDescription(`User **${username}** created successfully!`)
                .addFields(
                    { name: '👤 Username', value: username, inline: true },
                    { name: '🔑 Password', value: password, inline: true },
                    { name: '💰 Coins', value: '100', inline: true },
                    { name: '🆔 Database ID', value: result.insertedId.toString().slice(-8), inline: true },
                    { name: '👑 Created By', value: `<@${message.author.id}>`, inline: true },
                    { name: '📅 Created', value: new Date().toDateString(), inline: true }
                )
                .addFields({
                    name: '🧪 Login Test',
                    value: `Username: \`${username}\`\nPassword: \`${password}\``,
                    inline: false
                })
                .setFooter({ text: 'User can now login to dashboard' })
                .setTimestamp();

            return message.reply({ embeds: [embed] });
            
        } catch (error) {
            console.error('Force create error:', error);
            return message.reply(`❌ **Force create failed:** ${error.message}`);
        }
    }
};