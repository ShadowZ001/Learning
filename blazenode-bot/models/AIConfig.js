const mongoose = require('mongoose');

const aiConfigSchema = new mongoose.Schema({
    guildId: {
        type: String,
        required: true,
        unique: true
    },
    channelId: {
        type: String,
        default: null
    },
    enabled: {
        type: Boolean,
        default: false
    },
    model: {
        type: String,
        default: 'gemini-2.5-pro'
    },
    apiKey: {
        type: String,
        default: 'free-access'
    }
}, {
    timestamps: true
});

module.exports = mongoose.model('AIConfig', aiConfigSchema);