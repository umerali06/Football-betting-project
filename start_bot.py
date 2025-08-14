#!/usr/bin/env python3
"""
Simple startup script for FIXORA PRO Telegram Bot
"""

import os
import sys
import asyncio
import logging

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def start_bot():
    """Start the Telegram bot"""
    try:
        print("🚀 Starting FIXORA PRO Telegram Bot...")
        print("=" * 50)
        
        # Test imports
        print("📦 Testing imports...")
        from bot_interface.telegram_bot import TelegramBetBot
        print("✅ Imports successful")
        
        # Create bot
        print("🤖 Creating bot...")
        bot = TelegramBetBot()
        print("✅ Bot created")
        
        # Test connectivity
        print("🌐 Testing connectivity...")
        if await bot.test_connectivity():
            print("✅ Connected to Telegram!")
        else:
            print("❌ Cannot connect to Telegram")
            print("🔧 Check your internet connection and bot token")
            return
        
        print("\n🎯 Bot is ready!")
        print("📱 Instructions:")
        print("   1. Open Telegram and find your bot")
        print("   2. Send /start to begin")
        print("   3. Use /analyze for fast predictions")
        print("   4. Use /live for live match analysis")
        print("\n⚡ Features:")
        print("   • H2H (Win/Draw/Win) predictions")
        print("   • BTTS (Both Teams to Score)")
        print("   • Over/Under Goals analysis")
        print("   • Corners predictions")
        print("   • Fast response time (< 10 seconds)")
        
        print("\n🔄 Starting bot... Press Ctrl+C to stop")
        print("=" * 50)
        
        # Start the bot
        await bot.run()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Make sure all dependencies are installed:")
        print("   pip install python-telegram-bot aiohttp")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔧 Check your config.py file and bot token")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
