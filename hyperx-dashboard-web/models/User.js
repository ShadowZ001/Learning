const mongoose = require('mongoose');

const transactionSchema = new mongoose.Schema({
    type: { type: String, enum: ['received', 'sent'], required: true },
    label: { type: String, required: true },
    amount: { type: Number, required: true },
    time: { type: String, required: true },
    timestamp: { type: Date, default: Date.now }
});

const userSchema = new mongoose.Schema({
    discordId: { type: String, required: true, unique: true },
    username: { type: String, required: true },
    discriminator: { type: String, required: true },
    avatar: { type: String },
    coins: { type: Number, default: 0 },
    transactions: [transactionSchema],
    signupBonusReceived: { type: Boolean, default: false },
    lastLogin: { type: Date, default: Date.now },
    createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('User', userSchema);