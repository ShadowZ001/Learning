#!/bin/bash

echo "🚀 Starting all bots..."

# Start Dravon bot
cd /workspaces/Learning/Dravon
python3 main.py &
DRAVON_PID=$!
echo "✅ Dravon bot started (PID: $DRAVON_PID)"

# Start BlazeNode bot
cd /workspaces/Learning/blazenode-bot
node bot.js &
BLAZENODE_PID=$!
echo "✅ BlazeNode bot started (PID: $BLAZENODE_PID)"

# Start BlazeNode dashboard
cd /workspaces/Learning/blazenode-landing
node server.js &
DASHBOARD_PID=$!
echo "✅ Dashboard started (PID: $DASHBOARD_PID)"

# Save PIDs
echo $DRAVON_PID > /tmp/dravon.pid
echo $BLAZENODE_PID > /tmp/blazenode.pid
echo $DASHBOARD_PID > /tmp/dashboard.pid

echo "🎉 All services started!"