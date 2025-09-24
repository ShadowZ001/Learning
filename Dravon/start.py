#!/usr/bin/env python3
import asyncio
import os
import sys

async def main():
    """Simple startup script to ensure bot starts properly"""
    try:
        # Import and run the main bot
        from main import DravonBot
        
        # Create bot instance
        bot = DravonBot()
        
        # Start the bot
        await bot.start()
        
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Bot startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())