#!/bin/bash

# Start Node.js Canvacard service in background
echo "🚀 Starting Canvacard service..."
cd /workspaces/Learning/Dravon/canvacard-service
npm start &
CANVA_PID=$!

# Wait for service to start
sleep 3

# Start Python Discord bot
echo "🤖 Starting Discord bot..."
cd /workspaces/Learning/Dravon
python main.py &
BOT_PID=$!

echo "✅ Both services started!"
echo "📊 Canvacard service PID: $CANVA_PID"
echo "🤖 Discord bot PID: $BOT_PID"

# Keep script running
wait