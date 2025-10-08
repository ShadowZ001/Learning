const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  discordId: { type: String, required: true, unique: true },
  username: { type: String, required: true },
  email: { type: String, required: true },
  password: { type: String, required: true },
  serverId: { type: String, default: null },
  hasServer: { type: Boolean, default: false },
  balance: { type: Number, default: 50 },
  resources: {
    ram: { type: Number, default: 0 },
    cpu: { type: Number, default: 0 },
    disk: { type: Number, default: 0 },
    serverSlots: { type: Number, default: 0 },
    backups: { type: Number, default: 0 },
    ports: { type: Number, default: 0 }
  },
  createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('User', userSchema);