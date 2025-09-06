const mongoose = require('mongoose');
const User = require('../../models/User');

module.exports = {
    name: 'clearindex',
    description: 'Clear problematic database indexes',
    usage: '!clearindex',
    adminOnly: true,
    async execute(message, args) {
        try {
            console.log('🔧 Clearing problematic indexes...');
            
            // Drop all indexes except _id
            await User.collection.dropIndexes();
            console.log('✅ All indexes dropped');
            
            // Recreate only the username index
            await User.collection.createIndex({ username: 1 }, { unique: true });
            console.log('✅ Username index recreated');
            
            // List current indexes
            const indexes = await User.collection.listIndexes().toArray();
            let indexList = '📋 **Current Indexes:**\n';
            indexes.forEach(index => {
                indexList += `• ${index.name}: ${JSON.stringify(index.key)}\n`;
            });
            
            return message.reply(`✅ **Database indexes cleared and recreated!**\n\n${indexList}`);
            
        } catch (error) {
            console.error('Clear index error:', error);
            return message.reply(`❌ **Error:** ${error.message}`);
        }
    }
};