const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
    username: {
        type: String,
        sparse: true
    },
    password: {
        type: String,
        sparse: true
    },
    email: {
        type: String,
        unique: true,
        sparse: true
    },
    discordId: {
        type: String,
        unique: true,
        sparse: true
    },
    clerkId: {
        type: String,
        unique: true,
        sparse: true
    },
    discordUsername: {
        type: String
    },
    discordAvatar: {
        type: String
    },
    discordAccessToken: {
        type: String
    },
    discordRefreshToken: {
        type: String
    },
    loginType: {
        type: String,
        enum: ['username', 'discord', 'local', 'clerk'],
        required: true
    },
    coins: {
        type: Number,
        default: 100
    },
    pterodactylUserId: {
        type: Number
    },
    pterodactylPassword: {
        type: String
    },
    pterodactylEmail: {
        type: String
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
    },
    isAdmin: {
        type: Boolean,
        default: false
    },
    joinedDiscordServer: {
        type: Boolean,
        default: false
    }
}, {
    timestamps: true
});

module.exports = mongoose.model('User', userSchema);