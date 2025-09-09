// cPanel Node.js Startup File
const app = require('./app.js');

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`🚀 BlazeNode Dashboard started on port ${PORT}`);
});