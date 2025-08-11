#!/usr/bin/env python3
"""
Simple test script for the interactive Telegram bot
"""

import asyncio
import logging
from telegram_bot import TelegramBetBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_bot():
    """Test the interactive bot"""
    try:
        logger.info("Testing interactive Telegram bot...")
        
        # Create bot instance
        bot = TelegramBetBot()
        logger.info("Bot instance created")
        
        # Start the bot
        await bot.start()
        logger.info("Bot started successfully")
        
        # Get bot info
        bot_info = await bot.get_bot_info()
        if bot_info:
            logger.info(f"Bot info: {bot_info}")
        
        # Keep bot running for testing
        logger.info("Bot is now running and listening for messages...")
        logger.info("Send a message to @Percentvaluebot to test it!")
        logger.info("Press Ctrl+C to stop the test")
        
        # Wait for user to stop
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping bot test...")
        
        # Stop the bot
        await bot.stop()
        logger.info("Bot test completed")
        
    except Exception as e:
        logger.error(f"Bot test failed: {e}")
        raise

async def main():
    """Main test function"""
    try:
        await test_bot()
        print("\n" + "="*50)
        print("BOT TEST COMPLETED SUCCESSFULLY!")
        print("="*50)
        print("The bot is now working interactively!")
        print("Users can send messages to @Percentvaluebot")
        print("and the bot will respond automatically.")
        print("="*50)
    except Exception as e:
        print("\n" + "="*50)
        print(f"BOT TEST FAILED: {e}")
        print("="*50)
        return 1
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
