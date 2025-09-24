#!/bin/bash

echo "🛑 Stopping all bots..."

# Stop processes by PID
if [ -f /tmp/dravon.pid ]; then
    kill $(cat /tmp/dravon.pid) 2>/dev/null
    rm /tmp/dravon.pid
    echo "✅ Dravon bot stopped"
fi

if [ -f /tmp/blazenode.pid ]; then
    kill $(cat /tmp/blazenode.pid) 2>/dev/null
    rm /tmp/blazenode.pid
    echo "✅ BlazeNode bot stopped"
fi

if [ -f /tmp/dashboard.pid ]; then
    kill $(cat /tmp/dashboard.pid) 2>/dev/null
    rm /tmp/dashboard.pid
    echo "✅ Dashboard stopped"
fi

# Fallback: kill by process name
pkill -f "python3 main.py" 2>/dev/null
pkill -f "node bot.js" 2>/dev/null
pkill -f "node server.js" 2>/dev/null

echo "🎉 All services stopped!"