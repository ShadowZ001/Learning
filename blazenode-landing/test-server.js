// Simple test server to verify login flow
const app = require('./index.js');

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
    console.log(`🚀 BlazeNode Test Server running on port ${PORT}`);
    console.log(`🔗 Login URL: http://localhost:${PORT}`);
    console.log(`🔍 Debug URL: http://localhost:${PORT}/debug-session`);
    console.log(`📋 Dashboard URL: http://localhost:${PORT}/dashboard.html`);
    console.log('');
    console.log('✅ Ready for Discord OAuth2 testing!');
});