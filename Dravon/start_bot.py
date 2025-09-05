#!/usr/bin/env python3
"""
Dravon Bot Startup Script
Handles all initialization and error checking
"""
import asyncio
import sys
import os
import traceback
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("🚀 DRAVON BOT - STARTING UP")
    print("=" * 60)
    print(f"⏰ Startup Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔧 Checking systems...")

def check_environment():
    """Check if all required environment variables and files exist"""
    print("\n📋 Environment Check:")
    
    # Check .env file
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        return False
    print("✅ .env file found")
    
    # Check config
    try:
        from config import TOKEN
        if not TOKEN:
            print("❌ Discord token not found in config!")
            return False
        print("✅ Discord token configured")
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False
    
    # Create required directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    print("✅ Required directories created")
    
    return True

def check_dependencies():
    """Check if all required packages are installed"""
    print("\n📦 Dependency Check:")
    
    required_packages = [
        ('discord', 'discord.py'),
        ('wavelink', 'wavelink'),
        ('motor', 'motor'),
        ('aiohttp', 'aiohttp'),
        ('dotenv', 'python-dotenv')
    ]
    
    missing = []
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - MISSING")
            missing.append(name)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

async def test_systems():
    """Test critical bot systems"""
    print("\n🔧 System Tests:")
    
    try:
        # Test bot creation
        from main import DravonBot
        bot = DravonBot()
        print("✅ Bot instance created")
        
        # Test database
        try:
            await bot.db.get_prefix(123456789)
            print("✅ Database connection working")
        except Exception as e:
            print(f"⚠️ Database warning: {e}")
        
        # Test emoji handler
        try:
            bot.emoji_handler.replace_emojis("test :smile:")\n            print("✅ Emoji handler working")
        except Exception as e:
            print(f"❌ Emoji handler error: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        traceback.print_exc()
        return False

async def start_bot():
    """Start the bot with proper error handling"""
    print("\n🤖 Starting Dravon Bot...")
    
    try:
        from main import DravonBot
        from config import TOKEN
        
        bot = DravonBot()
        
        print("✅ Bot initialized successfully")
        print("🔗 Connecting to Discord...")
        
        await bot.start(TOKEN)
        
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Bot startup failed: {e}")
        traceback.print_exc()
        return False
    
    return True

async def main():
    """Main startup function"""
    print_banner()
    
    # Environment check
    if not check_environment():
        print("\n❌ Environment check failed!")
        return
    
    # Dependency check
    if not check_dependencies():
        print("\n❌ Dependency check failed!")
        return
    
    # System tests
    if not await test_systems():
        print("\n❌ System tests failed!")
        return
    
    print("\n" + "=" * 60)
    print("✅ ALL CHECKS PASSED - STARTING BOT")
    print("=" * 60)
    
    # Start bot
    await start_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        traceback.print_exc()