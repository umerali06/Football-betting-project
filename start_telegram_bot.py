#!/usr/bin/env python3
"""
FIXORA PRO Telegram Bot Startup Script
This script starts the Telegram bot with proper error handling
"""

import os
import sys
import asyncio
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def start_bot():
    """Start the Telegram bot"""
    try:
        print("🤖 Starting FIXORA PRO Telegram Bot...")
        print("=" * 50)
        
        # Import and create bot from the correct location
        from telegram_bot import TelegramBetBot
        
        bot = TelegramBetBot()
        
        # Start the bot
        print("\n🚀 Starting bot...")
        await bot.start()
        
        if bot.is_active():
            print("✅ Bot started successfully!")
            print("🔗 Send /start to your bot in Telegram to begin")
            
            # Keep the bot running
            try:
                while bot.is_active():
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping bot...")
                await bot.stop()
        else:
            print("❌ Bot failed to start")
            return False
        
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Failed to start bot: {e}")
        logger.exception("Bot startup error")
        return False

async def main():
    """Main function"""
    print("FIXORA PRO Telegram Bot Launcher")
    print("=" * 40)
    
    # Check if config exists
    try:
        import config
        print("✅ Configuration loaded")
        print(f"   Bot token: {'✅ Set' if config.TELEGRAM_BOT_TOKEN else '❌ Missing'}")
    except ImportError:
        print("❌ Configuration file not found")
        print("   Please ensure config.py exists in the project root")
        return
    
    # Check if required modules exist
    required_modules = [
        'telegram_bot',
        'api.unified_api_client',
        'config'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}: Available")
        except ImportError:
            print(f"❌ {module}: Missing")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Missing required modules: {', '.join(missing_modules)}")
        print("   Please ensure all dependencies are installed")
        return
    
    print("\n🎯 All requirements met. Starting bot...")
    
    # Start the bot
    success = await start_bot()
    
    if success:
        print("\n✅ Bot startup completed successfully")
    else:
        print("\n❌ Bot startup failed")
        print("\n🔧 Troubleshooting:")
        print("   1. Check network connectivity")
        print("   2. Verify bot token is correct")
        print("   3. Try a different network")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Launcher interrupted by user")
    except Exception as e:
        print(f"\n❌ Launcher failed: {e}")
        logger.exception("Launcher error")
