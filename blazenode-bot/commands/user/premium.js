module.exports = {
    name: 'premium',
    description: 'Premium commands help with categories',
    premiumOnly: true,
    async execute(message, args, isAdmin, bot, botAdmins, isPremium) {
        const { EmbedBuilder, ActionRowBuilder, StringSelectMenuBuilder } = require('discord.js');
        
        if (args[0] === 'help') {
            const embed = new EmbedBuilder()
                .setTitle('💎 Premium Commands Help')
                .setDescription('**Premium users can use commands without prefix!**\nJust type the letter directly: `a`, `b`, `c`, etc.')
                .setColor('#FFD700')
                .addFields(
                    {
                        name: '🎮 Gaming Commands',
                        value: '`a` - Advanced stats\n`g` - Game launcher\n`s` - Server status',
                        inline: true
                    },
                    {
                        name: '💰 Economy Commands', 
                        value: '`c` - Coins balance\n`e` - Economy stats\n`t` - Transfer coins',
                        inline: true
                    },
                    {
                        name: '🛠️ Utility Commands',
                        value: '`u` - User info\n`q` - Quick actions\n`h` - Help menu',
                        inline: true
                    },
                    {
                        name: '🎵 Music Commands',
                        value: '`p` - Play music\n`m` - Music controls\n`v` - Volume control',
                        inline: true
                    },
                    {
                        name: '🔧 Server Commands',
                        value: '`r` - Restart server\n`l` - Server logs\n`b` - Backup server',
                        inline: true
                    },
                    {
                        name: '👑 Premium Exclusive',
                        value: '`x` - Premium stats\n`z` - Premium tools',
                        inline: true
                    }
                )
                .setFooter({ text: 'Premium Feature • No prefix required for premium users' })
                .setTimestamp();

            const selectMenu = new StringSelectMenuBuilder()
                .setCustomId('premium_category')
                .setPlaceholder('Select a category for detailed commands')
                .addOptions([
                    {
                        label: '🎮 Gaming Commands',
                        description: 'Advanced gaming and server commands',
                        value: 'gaming'
                    },
                    {
                        label: '💰 Economy Commands',
                        description: 'Coin management and economy features',
                        value: 'economy'
                    },
                    {
                        label: '🛠️ Utility Commands',
                        description: 'Useful utility and information commands',
                        value: 'utility'
                    },
                    {
                        label: '🎵 Music Commands',
                        description: 'Music playback and control commands',
                        value: 'music'
                    },
                    {
                        label: '🔧 Server Commands',
                        description: 'Server management and control',
                        value: 'server'
                    },
                    {
                        label: '👑 Premium Exclusive',
                        description: 'Exclusive premium-only features',
                        value: 'exclusive'
                    }
                ]);

            const row = new ActionRowBuilder().addComponents(selectMenu);

            await message.reply({ embeds: [embed], components: [row] });
        } else {
            const embed = new EmbedBuilder()
                .setTitle('💎 Premium Status')
                .setDescription(`**${message.author.username}**, you have premium access!`)
                .setColor('#FFD700')
                .addFields(
                    {
                        name: '✨ Premium Benefits',
                        value: '• No prefix required for commands\n• Access to exclusive commands\n• Priority support\n• Advanced features',
                        inline: false
                    },
                    {
                        name: '📖 How to Use',
                        value: 'Type `!premium help` for detailed command list\nOr just use single letters: `a`, `b`, `c`, etc.',
                        inline: false
                    }
                )
                .setFooter({ text: 'Premium Feature Active' })
                .setTimestamp();

            await message.reply({ embeds: [embed] });
        }
    }
};