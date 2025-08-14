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
        
        # Import and create bot
        from bot_interface.telegram_bot import TelegramBetBot
        
        bot = TelegramBetBot()
        
        # Test connectivity first
        print("🔍 Testing bot connectivity...")
        if await bot.test_connectivity():
            print("✅ Bot connectivity test passed!")
        else:
            print("❌ Bot connectivity test failed!")
            print("\n🔧 Network connectivity issues detected.")
            print("   This usually means:")
            print("   • Firewall/proxy blocking Telegram")
            print("   • Corporate network restrictions")
            print("   • Regional blocking")
            print("   • DNS resolution issues")
            print("\n💡 Try these solutions:")
            print("   1. Use a different network (mobile hotspot)")
            print("   2. Try using a VPN")
            print("   3. Check firewall settings")
            print("   4. Change DNS servers (8.8.8.8, 1.1.1.1)")
            print("\n⚠️  The bot cannot start without Telegram connectivity.")
            print("   However, the core system works offline!")
            return False
        
        # Start the bot
        print("\n🚀 Starting bot...")
        await bot.run()
        
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
        'realtime_analyzer',
        'api.unified_api_client',
        'bot_interface.telegram_bot'
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
        print("   1. Run: python test_telegram_bot_comprehensive.py")
        print("   2. Check network connectivity")
        print("   3. Verify bot token is correct")
        print("   4. Try a different network")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Launcher interrupted by user")
    except Exception as e:
        print(f"\n❌ Launcher failed: {e}")
        logger.exception("Launcher error")
