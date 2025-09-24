const mongoose = require('mongoose');

const levelConfigSchema = new mongoose.Schema({
    guildId: {
        type: String,
        required: true,
        unique: true
    },
    canvaEnabled: {
        type: Boolean,
        default: false
    },
    levelChannel: {
        type: String,
        default: null
    }
}, {
    timestamps: true
});

module.exports = mongoose.model('LevelConfig', levelConfigSchema);