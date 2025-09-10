#!/usr/bin/env python3
"""
Dravon Bot Startup Script
Enhanced startup with error handling and logging
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/dravon.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('Dravon')

def check_requirements():
    """Check if all required files and dependencies exist"""
    required_files = [
        'main.py',
        'config.py',
        '.env',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"Missing required files: {', '.join(missing_files)}")
        return False
    
    # Check if logs directory exists
    if not os.path.exists('logs'):
        os.makedirs('logs')
        logger.info("Created logs directory")
    
    return True

async def start_bot():
    """Start the Dravon bot with error handling"""
    try:
        logger.info("=" * 50)
        logger.info("🤖 Starting Dravon Bot...")
        logger.info(f"📅 Startup Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 50)
        
        # Check requirements
        if not check_requirements():
            logger.error("❌ Requirements check failed!")
            return
        
        logger.info("✅ Requirements check passed")
        
        # Import and start the bot
        from main import main
        await main()
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Fatal error occurred: {e}")
        logger.exception("Full error traceback:")
    finally:
        logger.info("🔄 Bot shutdown complete")

def main():
    """Main entry point"""
    try:
        # Run the bot
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()