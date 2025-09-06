const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
    username: {
        type: String,
        required: true,
        unique: true
    },
    password: {
        type: String,
        required: true
    },
    coins: {
        type: Number,
        default: 100
    },
    pterodactylUserId: {
        type: Number
    },
    discordId: {
        type: String,
        default: null,
        sparse: true
    },
    serverCount: {
        type: Number,
        default: 0
    },
    lastLogin: {
        type: Date,
        default: Date.now
    },
    dailyRewardStreak: {
        type: Number,
        default: 0
    },
    lastDailyReward: {
        type: Date
    },
    createdBy: {
        type: String,
        default: 'web'
    }
}, {
    timestamps: true
});

module.exports = mongoose.model('User', userSchema);