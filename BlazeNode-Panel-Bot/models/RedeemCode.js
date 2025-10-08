const mongoose = require('mongoose');

const redeemCodeSchema = new mongoose.Schema({
  code: { type: String, required: true, unique: true },
  coins: { type: Number, required: true },
  maxUses: { type: Number, required: true },
  currentUses: { type: Number, default: 0 },
  usedBy: [{ type: String }],
  createdBy: { type: String, required: true },
  createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('RedeemCode', redeemCodeSchema);