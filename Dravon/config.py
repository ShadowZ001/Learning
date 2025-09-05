import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
MONGODB_URL = os.getenv('MONGODB_URL', None)  # Optional MongoDB connection