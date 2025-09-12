# Configuration Template for Dravon Bot
# Copy this file to config.py and fill in your values

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Discord Bot Configuration
TOKEN = os.getenv('DISCORD_TOKEN', 'your_discord_bot_token_here')

# Database Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/dravon')

# Session Configuration
SESSION_SECRET = os.getenv('SESSION_SECRET', 'your_session_secret_here')

# Pterodactyl Panel Configuration (Optional)
PTERODACTYL_API_KEY = os.getenv('PTERODACTYL_API_KEY', 'your_pterodactyl_api_key')
PTERODACTYL_URL = os.getenv('PTERODACTYL_URL', 'https://your-panel.com')

# Discord OAuth2 Configuration
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', 'your_client_id')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET', 'your_client_secret')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'https://your-domain.com/auth/callback')
DISCORD_GUILD_ID = os.getenv('DISCORD_GUILD_ID', 'your_main_guild_id')
DISCORD_INVITE_LINK = os.getenv('DISCORD_INVITE_LINK', 'https://discord.gg/your-invite')

# Lavalink Configuration (Optional - for music features)
LAVALINK_HOST = os.getenv('LAVALINK_HOST', 'localhost')
LAVALINK_PORT = int(os.getenv('LAVALINK_PORT', '2333'))
LAVALINK_PASSWORD = os.getenv('LAVALINK_PASSWORD', 'youshallnotpass')
LAVALINK_SECURE = os.getenv('LAVALINK_SECURE', 'false').lower() == 'true'

# Backup Lavalink Nodes (Optional)
LAVALINK_HOST2 = os.getenv('LAVALINK_HOST2', 'backup.lavalink.server')
LAVALINK_PORT2 = int(os.getenv('LAVALINK_PORT2', '443'))
LAVALINK_PASSWORD2 = os.getenv('LAVALINK_PASSWORD2', 'backup_password')

LAVALINK_HOST3 = os.getenv('LAVALINK_HOST3', 'backup2.lavalink.server')
LAVALINK_PORT3 = int(os.getenv('LAVALINK_PORT3', '443'))
LAVALINK_PASSWORD3 = os.getenv('LAVALINK_PASSWORD3', 'backup2_password')

# Admin Configuration
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
BOT_ADMIN_ID = int(os.getenv('BOT_ADMIN_ID', '123456789012345678'))

# Environment
NODE_ENV = os.getenv('NODE_ENV', 'production')