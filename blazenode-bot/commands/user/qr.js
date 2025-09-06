const { EmbedBuilder } = require('discord.js');

module.exports = {
    name: 'qr',
    description: 'Display QR code for payments',
    adminOnly: false,
    
    async execute(message, args, isAdmin, bot) {
        try {
            console.log(`QR command executed by ${message.author.username}`);
            
            const qrEmbed = new EmbedBuilder()
                .setTitle('💳 Payment QR Code')
                .setDescription('Scan this QR code to make payments to BlazeNode')
                .setImage('https://cdn.discordapp.com/attachments/1413785935207727113/1413802272609140837/qr_code_1130089558734803025_upi3.png?ex=68bd4178&is=68bbeff8&hm=5832a71b1d986960a4fd3a1291b4672ade00dd88b3b39ed435a0ae9f14f2f346&')
                .setColor('#ff6b35')
                .setFooter({ 
                    text: 'BlazeNode Payment System',
                    iconURL: bot.user.displayAvatarURL()
                })
                .setTimestamp();
            
            await message.reply({ embeds: [qrEmbed] });
            
        } catch (error) {
            console.error('QR command error:', error);
            await message.reply('❌ **Error:** Failed to display QR code.');
        }
    }
};