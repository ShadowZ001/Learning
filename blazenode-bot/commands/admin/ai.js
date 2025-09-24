const { EmbedBuilder, ActionRowBuilder, StringSelectMenuBuilder } = require('discord.js');

module.exports = {
    name: 'ai',
    adminOnly: true,
    async execute(message) {
        console.log('🤖 AI command executing...');
        
        const embed = new EmbedBuilder()
            .setTitle('🤖 AI Assistant Configuration')
            .setDescription('**Configure intelligent AI responses for your server**\n\n🧠 **Model:** Gemini 1.5 Flash (Free)\n🔗 **Provider:** Google AI\n⚡ **Status:** Ready to configure')
            .setColor('#6B7280');

        const selectMenu = new StringSelectMenuBuilder()
            .setCustomId('ai_config')
            .setPlaceholder('Choose configuration option')
            .addOptions([
                {
                    label: 'Select Channel',
                    description: 'Set the channel where AI will respond',
                    value: 'select_channel',
                    emoji: '📍'
                },
                {
                    label: 'AI Config',
                    description: 'View and modify AI configuration',
                    value: 'ai_config',
                    emoji: '⚙️'
                },
                {
                    label: 'AI Status',
                    description: 'Check current AI status and settings',
                    value: 'ai_status',
                    emoji: '📊'
                },
                {
                    label: 'AI Enable/Disable',
                    description: 'Toggle AI responses on/off',
                    value: 'ai_toggle',
                    emoji: '🔄'
                }
            ]);

        const row = new ActionRowBuilder().addComponents(selectMenu);
        
        try {
            const reply = await message.reply({ embeds: [embed], components: [row] });
            console.log('✅ AI command sent successfully');
            
            const collector = reply.createMessageComponentCollector({ time: 60000 });

            collector.on('collect', async (interaction) => {
                if (interaction.user.id !== message.author.id) {
                    return interaction.reply({ content: '❌ Only the command user can use this menu.', ephemeral: true });
                }

                try {
                    const AIConfig = require('../../models/AIConfig');
                    const config = await AIConfig.findOne({ guildId: message.guild.id }) || 
                                  new AIConfig({ guildId: message.guild.id });

                    switch (interaction.values[0]) {
                        case 'select_channel':
                            await interaction.reply({ 
                                content: '📍 **Channel Selection**\nMention the channel where AI should respond (e.g., #ai-chat)', 
                                ephemeral: true 
                            });
                            break;

                        case 'ai_config':
                            const configEmbed = new EmbedBuilder()
                                .setTitle('⚙️ AI Configuration')
                                .setColor('#6B7280')
                                .addFields(
                                    { name: 'Model', value: 'gemini-2.5-pro', inline: true },
                                    { name: 'Channel', value: config.channelId ? `<#${config.channelId}>` : 'Not set', inline: true },
                                    { name: 'Status', value: config.enabled ? '✅ Enabled' : '❌ Disabled', inline: true }
                                );
                            await interaction.reply({ embeds: [configEmbed], ephemeral: true });
                            break;

                        case 'ai_status':
                            const statusEmbed = new EmbedBuilder()
                                .setTitle('📊 AI Status')
                                .setColor(config.enabled ? '#10B981' : '#EF4444')
                                .addFields(
                                    { name: 'Status', value: config.enabled ? '🟢 Online' : '🔴 Offline', inline: true },
                                    { name: 'Channel', value: config.channelId ? `<#${config.channelId}>` : 'Not configured', inline: true },
                                    { name: 'Model', value: 'Gemini 2.5 Pro', inline: true }
                                );
                            await interaction.reply({ embeds: [statusEmbed], ephemeral: true });
                            break;

                        case 'ai_toggle':
                            config.enabled = !config.enabled;
                            await config.save();
                            
                            const toggleEmbed = new EmbedBuilder()
                                .setTitle('🔄 AI Toggle')
                                .setDescription(`AI has been **${config.enabled ? 'enabled' : 'disabled'}**`)
                                .setColor(config.enabled ? '#10B981' : '#EF4444');
                            await interaction.reply({ embeds: [toggleEmbed], ephemeral: true });
                            break;
                    }
                } catch (error) {
                    console.error('❌ Interaction error:', error);
                    await interaction.reply({ content: '❌ An error occurred.', ephemeral: true });
                }
            });

            collector.on('end', () => {
                const disabledRow = new ActionRowBuilder()
                    .addComponents(selectMenu.setDisabled(true));
                reply.edit({ components: [disabledRow] }).catch(() => {});
            });
            
        } catch (error) {
            console.error('❌ AI command error:', error);
            await message.reply('❌ Failed to execute AI command.');
        }
    }
};