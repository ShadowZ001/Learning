const { EmbedBuilder } = require('discord.js');

module.exports = {
    name: 'help',
    description: 'Show all available commands',
    usage: '!help',
    adminOnly: false,
    async execute(message, args, isAdmin) {
        const embed = new EmbedBuilder()
            .setColor(0x3B82F6)
            .setTitle('🤖 BlazeNode Bot Commands')
            .setDescription('**Available Commands:**')
            .addFields({
                name: '👤 **User Commands**',
                value: '`!coins <username>` - Check coin balance\n`!help` - Show this help menu',
                inline: false
            });

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
                    '`!botadmin add <@user>` - Add admin\n' +
                    '`!botadmin remove <@user>` - Remove admin\n' +
                    '`!botadmin list` - List admins',
                inline: false
            });
        }

        embed.setFooter({ text: `Requested by ${message.author.username}` });
        return message.reply({ embeds: [embed] });
    }
};