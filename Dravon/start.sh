#!/bin/bash

# Pterodactyl startup script for Dravon Bot
echo "Starting Dravon Bot..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip."
    exit 1
fi

# Install requirements if they don't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create logs directory if it doesn't exist
mkdir -p logs

# Set permissions
chmod +x start_dravon.py

# Start the bot
echo "Starting Dravon Bot..."
python start_dravon.py