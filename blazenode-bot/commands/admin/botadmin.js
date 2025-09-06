module.exports = {
    name: 'botadmin',
    description: 'Manage bot administrators',
    usage: '/botadmin <add|remove|list> [@user]',
    adminOnly: true,
    async execute(message, args, isAdmin, bot, botAdmins) {
        const action = args[0];
        const ADMIN_ID = '1037768611126841405';

        if (action === 'list') {
            let adminList = '👑 **Bot Administrators:**\n\n';
            botAdmins.forEach((adminId, index) => {
                adminList += `**${index + 1}.** <@${adminId}> \`(${adminId})\`\n`;
            });
            return message.reply(adminList);

        } else if (action === 'add') {
            const targetUser = message.mentions.users.first();
            if (!targetUser) {
                return message.reply('❌ **Usage:** `/botadmin add <@user>`\n**Example:** `/botadmin add @username`');
            }

            if (botAdmins.includes(targetUser.id)) {
                return message.reply(`❌ **${targetUser.username}** is already a bot administrator!`);
            }

            botAdmins.push(targetUser.id);
            console.log(`👑 Admin added: ${targetUser.username} by ${message.author.username}`);
            return message.reply(`✅ **${targetUser.username}** has been added as a bot administrator!`);

        } else if (action === 'remove') {
            const targetUser = message.mentions.users.first();
            if (!targetUser) {
                return message.reply('❌ **Usage:** `/botadmin remove <@user>`\n**Example:** `/botadmin remove @username`');
            }

            if (targetUser.id === ADMIN_ID) {
                return message.reply('❌ **Cannot remove the main administrator!**');
            }

            const index = botAdmins.indexOf(targetUser.id);
            if (index === -1) {
                return message.reply(`❌ **${targetUser.username}** is not a bot administrator!`);
            }

            botAdmins.splice(index, 1);
            console.log(`👑 Admin removed: ${targetUser.username} by ${message.author.username}`);
            return message.reply(`✅ **${targetUser.username}** has been removed as a bot administrator!`);

        } else {
            return message.reply('❌ **Usage:** `/botadmin <add|remove|list>`\n**Examples:**\n`/botadmin list`\n`/botadmin add @user`\n`/botadmin remove @user`');
        }
    }
};