const mongoose = require('mongoose');

const blacklistSchema = new mongoose.Schema({
  discordId: { type: String, required: true, unique: true },
  username: { type: String, required: true },
  reason: { type: String, default: 'No reason provided' },
  blacklistedBy: { type: String, required: true },
  blacklistedAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Blacklist', blacklistSchema);