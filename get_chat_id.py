#!/usr/bin/env python3
"""
Simple script to get your Telegram chat ID
Run this and send a message to your bot to get your chat ID
"""

import asyncio
import logging
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def start_command(update: Update, context):
    """Handle /start command"""
    await update.message.reply_text(
        "Hello! I'm the FIXORA PRO bot. Send me any message to get your chat ID."
    )

async def help_command(update: Update, context):
    """Handle /help command"""
    await update.message.reply_text(
        "Send me any message and I'll show you your chat ID."
    )

async def handle_message(update: Update, context):
    """Handle any message to get chat ID"""
    chat_id = update.message.chat_id
    chat_type = update.message.chat.type
    user_name = update.message.from_user.username or update.message.from_user.first_name
    
    response = f"""
Chat ID: {chat_id}
Chat Type: {chat_type}
User: {user_name}

Copy this chat ID and update your config.py file:
TELEGRAM_CHAT_ID = "{chat_id}"
    """.strip()
    
    await update.message.reply_text(response)
    logger.info(f"Chat ID requested: {chat_id} by {user_name}")

async def main():
    """Main function"""
    if not config.TELEGRAM_BOT_TOKEN:
        print("ERROR: No Telegram bot token configured in config.py")
        return
    
    # Create application
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    print("Starting bot to get chat ID...")
    print("1. Send any message to your bot @Percentvaluebot")
    print("2. Copy the chat ID from the response")
    print("3. Update config.py with the chat ID")
    print("4. Stop this script with Ctrl+C")
    
    await application.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped. Update your config.py with the chat ID you received.")
    except Exception as e:
        print(f"Error: {e}")
