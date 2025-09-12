# Dravon Bot Deployment Guide

## 🚀 Pterodactyl Panel Deployment

### Prerequisites
- Python 3.11 or higher
- MongoDB database
- Lavalink server (optional for music)
- Discord Bot Token

### Step 1: Create Server on Pterodactyl
1. Go to your Pterodactyl panel
2. Create a new server with these specifications:
   - **Egg**: Python Generic
   - **Memory**: Minimum 512MB (Recommended: 1GB+)
   - **CPU**: Minimum 50% (Recommended: 100%+)
   - **Disk**: Minimum 1GB (Recommended: 2GB+)

### Step 2: Upload Bot Files
1. Upload all bot files to the server directory
2. Ensure these files are present:
   - `start_dravon.py` (main startup file)
   - `main.py` (bot core)
   - `config.py` (configuration)
   - `requirements.txt` (dependencies)
   - `start.sh` (startup script)
   - All `cogs/` folder contents
   - All `utils/` folder contents

### Step 3: Configure Environment
1. Edit `config.py` with your settings:
   ```python
   TOKEN = "your_discord_bot_token"
   MONGODB_URI = "your_mongodb_connection_string"
   LAVALINK_HOST = "your_lavalink_host"
   LAVALINK_PORT = "your_lavalink_port"
   LAVALINK_PASSWORD = "your_lavalink_password"
   ```

### Step 4: Set Startup Command
In Pterodactyl panel, set the startup command to:
```bash
bash start.sh
```

Or alternatively:
```bash
python start_dravon.py
```

### Step 5: Start the Bot
1. Click "Start" in your Pterodactyl panel
2. Monitor the console for any errors
3. The bot should connect to Discord successfully

## 🐳 Docker Deployment (Alternative)

### Using Docker
```bash
# Build the image
docker build -t dravon-bot .

# Run the container
docker run -d --name dravon-bot \
  -e DISCORD_TOKEN="your_token" \
  -e MONGODB_URI="your_mongodb_uri" \
  dravon-bot
```

## 📋 Required Environment Variables

Create a `.env` file with these variables:
```env
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret

# Database Configuration
MONGODB_URI=your_mongodb_connection_string

# Lavalink Configuration (Optional)
LAVALINK_HOST=localhost
LAVALINK_PORT=2333
LAVALINK_PASSWORD=youshallnotpass
LAVALINK_SECURE=false

# Additional Lavalink Nodes (Optional)
LAVALINK_HOST2=backup.lavalink.server
LAVALINK_PORT2=443
LAVALINK_PASSWORD2=backup_password

LAVALINK_HOST3=backup2.lavalink.server
LAVALINK_PORT3=443
LAVALINK_PASSWORD3=backup2_password
```

## 🔧 Troubleshooting

### Common Issues

1. **Bot won't start**
   - Check if Python 3.11+ is installed
   - Verify all dependencies are installed: `pip install -r requirements.txt`
   - Check Discord token validity

2. **Database connection failed**
   - Verify MongoDB URI is correct
   - Ensure MongoDB server is accessible
   - Check network connectivity

3. **Music not working**
   - Verify Lavalink server is running
   - Check Lavalink configuration in config.py
   - Ensure bot has voice permissions

4. **Permission errors**
   - Make sure start.sh has execute permissions: `chmod +x start.sh`
   - Check file ownership and permissions

### Performance Optimization

1. **Memory Usage**
   - Minimum: 512MB RAM
   - Recommended: 1GB+ RAM for large servers

2. **CPU Usage**
   - Minimum: 50% CPU allocation
   - Recommended: 100%+ for music features

3. **Network**
   - Stable internet connection required
   - Low latency preferred for music streaming

## 📊 Monitoring

### Log Files
- Bot logs are stored in `logs/` directory
- Check `logs/dravon.log` for detailed information
- Monitor console output in Pterodactyl panel

### Health Checks
- Use `/ping` command to check bot status
- Monitor memory and CPU usage in panel
- Check database connectivity regularly

## 🔄 Updates

### Updating the Bot
1. Stop the bot in Pterodactyl panel
2. Upload new files (overwrite existing)
3. Restart the bot
4. Monitor console for successful startup

### Database Migrations
- Bot automatically handles database schema updates
- No manual migration required for most updates

## 🆘 Support

If you encounter issues:
1. Check the console logs in Pterodactyl
2. Verify all configuration settings
3. Ensure all dependencies are installed
4. Contact support with error logs

## 📝 Notes

- Bot requires stable internet connection
- MongoDB database is required for all features
- Lavalink is optional but required for music features
- Premium features require valid premium system setup
- Regular backups of database recommended