const { EmbedBuilder } = require('discord.js');

module.exports = {
    name: 'help',
    description: 'Show all available commands',
    usage: '!help',
    adminOnly: false,
    async execute(message, args, isAdmin, bot, botAdmins, isPremium) {
        const embed = new EmbedBuilder()
            .setColor(0x3B82F6)
            .setTitle('🤖 BlazeNode Bot Commands')
            .setDescription('**Available Commands:**')
            .addFields({
                name: '👤 **User Commands**',
                value: '`!coins <username>` - Check coin balance\n`!help` - Show this help menu\n`!qr <text>` - Generate QR code',
                inline: false
            });
            
        if (isPremium) {
            embed.addFields({
                name: '💎 **Premium Commands** (No prefix needed!)',
                value: '`premium help` - Premium command guide\n`x` - Premium analytics\n`z` - Premium tools\nUse any single letter A-Z without prefix!',
                inline: false
            });
        }

        if (isAdmin) {
            embed.addFields({
                name: '🔧 **Admin Commands**',
                value: 
                    '`!create <username> <password>` - Create new user\n' +
                    '`!coin give <username> <amount>` - Give coins\n' +
                    '`!coin remove <username> <amount>` - Remove coins\n' +
                    '`!balance <username>` - Check balance\n' +
                    '`!users` - List all users\n' +
                    '`!delete <username>` - Delete user\n' +
                    '`!user <username>` - User details\n' +
                    '`!logs` - Bot statistics\n' +
                    '`!channel <#channel>` - Set channel\n' +
                    '`!set <setting> <value>` - Bot settings\n' +
                    '`!premium add/remove <user>` - Manage premium\n' +
                    '`!botadmin add <@user>` - Add admin',
                inline: false
            });
        }

        embed.setFooter({ text: `Requested by ${message.author.username}${isPremium ? ' • Premium User' : ''}` });
        return message.reply({ embeds: [embed] });
    }
};