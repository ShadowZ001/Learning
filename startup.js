// cPanel Node.js Startup File
const { spawn } = require('child_process');
const path = require('path');

// Start the application
const app = spawn('node', ['app.js'], {
    cwd: __dirname,
    stdio: 'inherit'
});

app.on('close', (code) => {
    console.log(`BlazeNode Dashboard process exited with code ${code}`);
});

app.on('error', (err) => {
    console.error('Failed to start BlazeNode Dashboard:', err);
});

console.log('🚀 BlazeNode Dashboard startup initiated for cPanel');