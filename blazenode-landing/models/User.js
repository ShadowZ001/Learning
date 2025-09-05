const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
    discordId: {
        type: String,
        required: true,
        unique: true
    },
    username: {
        type: String,
        required: true
    },
    discriminator: {
        type: String,
        default: '0'
    },
    email: {
        type: String,
        required: true
    },
    avatar: {
        type: String
    },
    coins: {
        type: Number,
        default: 100
    },
    joinedServer: {
        type: Boolean,
        default: false
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
    }
}, {
    timestamps: true
});

module.exports = mongoose.model('User', userSchema);