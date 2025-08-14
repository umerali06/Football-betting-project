#!/usr/bin/env python3
"""
Simple test script for Telegram bot functionality
Tests imports, basic connectivity, and command handling
"""

import os
import sys
import asyncio
import logging

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_bot():
    """Test the Telegram bot"""
    try:
        print("🔧 Testing Telegram bot...")
        
        # Test imports
        print("📦 Testing imports...")
        from bot_interface.telegram_bot import TelegramBetBot
        print("✅ All imports successful")
        
        # Test bot creation
        print("🤖 Creating bot instance...")
        bot = TelegramBetBot()
        print("✅ Bot instance created")
        
        # Test bot status
        print("📊 Checking bot status...")
        status = bot.get_bot_status()
        print(f"✅ Bot status: {status}")
        
        # Test connectivity
        print("🌐 Testing connectivity...")
        connectivity = await bot.test_connectivity()
        if connectivity:
            print("✅ Bot connectivity test passed!")
        else:
            print("❌ Bot connectivity test failed!")
            return
        
        print("\n🎯 Bot is ready! Starting...")
        print("📱 Send /start to your bot in Telegram")
        print("🔍 Then try /analyze for fast predictions")
        print("⚽ Use /live for live match analysis")
        
        # Start the bot
        await bot.run()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Starting Telegram Bot Test...")
    print("=" * 50)
    
    try:
        asyncio.run(test_bot())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
