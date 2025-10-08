const mongoose = require('mongoose');

const adminSchema = new mongoose.Schema({
  discordId: { type: String, required: true, unique: true },
  username: { type: String, required: true },
  addedBy: { type: String, required: true },
  addedAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Admin', adminSchema);