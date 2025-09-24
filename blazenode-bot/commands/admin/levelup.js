const { EmbedBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle, AttachmentBuilder } = require('discord.js');
const { Rank } = require('canvacard');

module.exports = {
    name: 'levelup',
    adminOnly: true,
    async execute(message, args) {
        if (args[0] === 'canva') {
            await handleCanvaSetup(message);
        } else {
            await handleNormalSetup(message);
        }
    }
};

async function handleCanvaSetup(message) {
    try {
        // Create preview Canvacard
        const rank = new Rank()
            .setAvatar(message.author.displayAvatarURL({ format: 'png' }))
            .setCurrentXP(750)
            .setRequiredXP(1000)
            .setLevel(5)
            .setRank(12)
            .setProgressBar('#FFFFFF', 'COLOR')
            .setUsername(message.author.username)
            .setDiscriminator(message.author.discriminator || '0000');

        const buffer = await rank.build();
        const attachment = new AttachmentBuilder(buffer, { name: 'levelup-preview.png' });

        const embed = new EmbedBuilder()
            .setTitle('🎨 Canvacard Level System')
            .setDescription('**Preview of Canvacard level up cards**\n\nThis creates beautiful visual level up notifications with user avatars, XP bars, and custom styling.')
            .setImage('attachment://levelup-preview.png')
            .setColor('#7289DA');

        const row = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('canva_enable')
                    .setLabel('Enable Canvacard')
                    .setStyle(ButtonStyle.Success)
                    .setEmoji('✅'),
                new ButtonBuilder()
                    .setCustomId('canva_disable')
                    .setLabel('Disable Canvacard')
                    .setStyle(ButtonStyle.Danger)
                    .setEmoji('❌')
            );

        const reply = await message.reply({ embeds: [embed], files: [attachment], components: [row] });

        const collector = reply.createMessageComponentCollector({ time: 60000 });

        collector.on('collect', async (interaction) => {
            if (interaction.user.id !== message.author.id) {
                return interaction.reply({ content: '❌ Only the command user can use this.', ephemeral: true });
            }

            const LevelConfig = require('../../models/LevelConfig');
            let config = await LevelConfig.findOne({ guildId: message.guild.id });
            if (!config) {
                config = new LevelConfig({ guildId: message.guild.id });
            }

            if (interaction.customId === 'canva_enable') {
                config.canvaEnabled = true;
                await config.save();
                await interaction.reply({ content: '✅ **Canvacard enabled!** Level up messages will now use beautiful visual cards.', ephemeral: true });
            } else {
                config.canvaEnabled = false;
                await config.save();
                await interaction.reply({ content: '❌ **Canvacard disabled!** Level up messages will use normal text embeds.', ephemeral: true });
            }
        });

    } catch (error) {
        console.error('❌ Canva setup error:', error);
        await message.reply('❌ Failed to create Canvacard preview.');
    }
}

async function handleNormalSetup(message) {
    const embed = new EmbedBuilder()
        .setTitle('📈 Level System Setup')
        .setDescription('**Configure the level system for your server**\n\n🎯 **Commands:**\n`>levelup` - Normal setup\n`>levelup canva` - Canvacard setup with visual cards')
        .addFields(
            { name: '📊 Normal Mode', value: 'Simple text-based level notifications', inline: true },
            { name: '🎨 Canvacard Mode', value: 'Beautiful visual level up cards', inline: true }
        )
        .setColor('#00FF00');

    await message.reply({ embeds: [embed] });
}