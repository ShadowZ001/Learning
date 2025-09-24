#!/bin/bash
# Stop all bot processes

echo "🛑 Stopping all bot processes..."

# Kill all python processes
pkill -f python
pkill -f node

# Force kill if needed
sleep 2
pkill -9 -f python
pkill -9 -f node

echo "✅ All bot processes stopped!"