const mongoose = require('mongoose');

const userResourcesSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true,
        unique: true
    },
    availableRam: {
        type: Number,
        default: 2048 // 2GB default
    },
    availableCpu: {
        type: Number,
        default: 100 // 100% default
    },
    availableDisk: {
        type: Number,
        default: 8192 // 8GB default
    },
    serverSlots: {
        type: Number,
        default: 2 // 2 slots default
    },
    purchasedRam: {
        type: Number,
        default: 0
    },
    purchasedCpu: {
        type: Number,
        default: 0
    },
    purchasedDisk: {
        type: Number,
        default: 0
    },
    purchasedSlots: {
        type: Number,
        default: 0
    }
});

module.exports = mongoose.model('UserResources', userResourcesSchema);