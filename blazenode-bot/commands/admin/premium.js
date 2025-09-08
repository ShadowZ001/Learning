module.exports = {
    name: 'premium',
    description: 'Manage premium users',
    adminOnly: true,
    async execute(message, args, isAdmin, bot, botAdmins, isPremium) {
        const { EmbedBuilder } = require('discord.js');
        
        if (!args[0]) {
            const embed = new EmbedBuilder()
                .setTitle('👑 Premium Management')
                .setDescription('**Admin commands for managing premium users**')
                .setColor('#FFD700')
                .addFields(
                    {
                        name: '🔧 Commands',
                        value: '`!premium add <user>` - Grant premium\n`!premium remove <user>` - Remove premium\n`!premium list` - List premium users\n`!premium check <user>` - Check premium status',
                        inline: false
                    }
                )
                .setFooter({ text: 'Admin Only • Premium Management' });
            
            return message.reply({ embeds: [embed] });
        }

        const action = args[0].toLowerCase();
        const User = require('../../models/User');

        try {
            switch (action) {
                case 'add':
                    if (!args[1]) {
                        return message.reply('❌ **Usage:** `!premium add <username>`');
                    }
                    
                    const userToAdd = await User.findOne({ username: args[1] });
                    if (!userToAdd) {
                        return message.reply(`❌ **User not found:** ${args[1]}`);
                    }
                    
                    userToAdd.isPremium = true;
                    userToAdd.premiumExpiry = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000); // 30 days
                    await userToAdd.save();
                    
                    const addEmbed = new EmbedBuilder()
                        .setTitle('✅ Premium Added')
                        .setDescription(`**${args[1]}** now has premium access!`)
                        .setColor('#00FF00')
                        .addFields({
                            name: '📅 Expires',
                            value: userToAdd.premiumExpiry.toLocaleDateString(),
                            inline: true
                        });
                    
                    await message.reply({ embeds: [addEmbed] });
                    break;

                case 'remove':
                    if (!args[1]) {
                        return message.reply('❌ **Usage:** `!premium remove <username>`');
                    }
                    
                    const userToRemove = await User.findOne({ username: args[1] });
                    if (!userToRemove) {
                        return message.reply(`❌ **User not found:** ${args[1]}`);
                    }
                    
                    userToRemove.isPremium = false;
                    userToRemove.premiumExpiry = null;
                    await userToRemove.save();
                    
                    const removeEmbed = new EmbedBuilder()
                        .setTitle('❌ Premium Removed')
                        .setDescription(`**${args[1]}** premium access revoked.`)
                        .setColor('#FF0000');
                    
                    await message.reply({ embeds: [removeEmbed] });
                    break;

                case 'list':
                    const premiumUsers = await User.find({ isPremium: true });
                    
                    const listEmbed = new EmbedBuilder()
                        .setTitle('👑 Premium Users')
                        .setDescription(premiumUsers.length > 0 ? 
                            premiumUsers.map(u => `• **${u.username}** - Expires: ${u.premiumExpiry ? u.premiumExpiry.toLocaleDateString() : 'Never'}`).join('\n') :
                            'No premium users found.')
                        .setColor('#FFD700')
                        .setFooter({ text: `Total: ${premiumUsers.length} premium users` });
                    
                    await message.reply({ embeds: [listEmbed] });
                    break;

                case 'check':
                    if (!args[1]) {
                        return message.reply('❌ **Usage:** `!premium check <username>`');
                    }
                    
                    const userToCheck = await User.findOne({ username: args[1] });
                    if (!userToCheck) {
                        return message.reply(`❌ **User not found:** ${args[1]}`);
                    }
                    
                    const checkEmbed = new EmbedBuilder()
                        .setTitle('🔍 Premium Status Check')
                        .setDescription(`**${args[1]}** premium status`)
                        .setColor(userToCheck.isPremium ? '#00FF00' : '#FF0000')
                        .addFields(
                            {
                                name: '💎 Premium Status',
                                value: userToCheck.isPremium ? '✅ Active' : '❌ Not Active',
                                inline: true
                            },
                            {
                                name: '📅 Expiry Date',
                                value: userToCheck.premiumExpiry ? userToCheck.premiumExpiry.toLocaleDateString() : 'N/A',
                                inline: true
                            }
                        );
                    
                    await message.reply({ embeds: [checkEmbed] });
                    break;

                default:
                    await message.reply('❌ **Invalid action.** Use: `add`, `remove`, `list`, or `check`');
            }
        } catch (error) {
            console.error('Premium management error:', error);
            await message.reply('❌ **Error:** Could not manage premium status.');
        }
    }
};