// cPanel Entry Point for BlazeNode Dashboard
// This file ensures compatibility with cPanel hosting

const app = require('./index.js');

// Export for cPanel
module.exports = app;

// Start server if run directly
if (require.main === module) {
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log(`🚀 BlazeNode Dashboard running on port ${PORT}`);
        console.log(`✅ Discord OAuth2 Login Only`);
        console.log(`🔗 Login URL: http://localhost:${PORT}`);
    });
}