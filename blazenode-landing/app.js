// cPanel Entry Point for BlazeNode Dashboard
const app = require('./index');

// cPanel will handle the port automatically
const PORT = process.env.PORT || 3000;

const server = app.listen(PORT, () => {
    console.log(`🚀 BlazeNode Dashboard running on cPanel`);
    console.log(`📊 Port: ${PORT}`);
});

// Export for cPanel
module.exports = app;