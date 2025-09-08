const mongoose = require('mongoose');

const couponSchema = new mongoose.Schema({
    code: {
        type: String,
        required: true,
        unique: true,
        uppercase: true
    },
    amount: {
        type: Number,
        required: true,
        min: 1
    },
    limit: {
        type: Number,
        required: true,
        min: 1
    },
    used: {
        type: Number,
        default: 0
    },
    usedBy: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User'
    }],
    createdBy: {
        type: String,
        required: true
    },
    createdAt: {
        type: Date,
        default: Date.now
    },
    active: {
        type: Boolean,
        default: true
    }
});

module.exports = mongoose.model('Coupon', couponSchema);