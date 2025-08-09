#!/usr/bin/env python3
"""
Telegram Bot Token Validator
This script helps you validate your Telegram bot tokens
"""

import asyncio
from telegram import Bot
import sys

async def validate_token(token):
    """Validate a Telegram bot token"""
    try:
        bot = Bot(token=token)
        bot_info = await bot.get_me()
        
        print(f"✅ Token is VALID!")
        print(f"   Bot Name: {bot_info.first_name}")
        print(f"   Username: @{bot_info.username}")
        print(f"   Bot ID: {bot_info.id}")
        print(f"   Can Join Groups: {bot_info.can_join_groups}")
        print(f"   Can Read Messages: {bot_info.can_read_all_group_messages}")
        
        return True
        
    except Exception as e:
        print(f"❌ Token is INVALID!")
        print(f"   Error: {e}")
        return False

async def main():
    """Main function"""
    print("🤖 Telegram Bot Token Validator")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # Token provided as command line argument
        token = sys.argv[1]
    else:
        # Ask user for token
        token = input("Enter your Telegram bot token: ").strip()
    
    if not token:
        print("❌ No token provided!")
        return
    
    print(f"\n🔍 Validating token: {token[:15]}...")
    print("-" * 30)
    
    is_valid = await validate_token(token)
    
    if is_valid:
        print(f"\n💡 To use this token in your betting system:")
        print(f"   1. Update config.py: TELEGRAM_BOT_TOKEN = \"{token}\"")
        print(f"   2. Or set environment variable: export TELEGRAM_BOT_TOKEN=\"{token}\"")
    else:
        print(f"\n💡 If this token should be valid:")
        print(f"   1. Check if the bot was created properly with @BotFather")
        print(f"   2. Make sure you copied the full token correctly")
        print(f"   3. Verify the bot hasn't been deleted or disabled")

if __name__ == "__main__":
    asyncio.run(main())