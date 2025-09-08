const { spawn } = require('child_process');

// Kill any existing process on port 5504
const { exec } = require('child_process');

console.log('Checking for existing processes on port 5504...');

exec('lsof -ti:5504', (error, stdout, stderr) => {
    if (stdout.trim()) {
        console.log('Killing existing process:', stdout.trim());
        exec(`kill -9 ${stdout.trim()}`, (killError) => {
            if (killError) {
                console.log('Error killing process:', killError.message);
            }
            setTimeout(startServer, 1000);
        });
    } else {
        console.log('No existing process found');
        startServer();
    }
});

function startServer() {
    console.log('Starting server on port 5504...');
    const server = spawn('node', ['server.js'], {
        stdio: 'inherit',
        cwd: __dirname
    });

    server.on('error', (err) => {
        console.error('Server error:', err);
    });

    server.on('close', (code) => {
        console.log(`Server process exited with code ${code}`);
    });
}