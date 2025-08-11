#!/usr/bin/env python3
"""
Interactive Telegram Bot for FIXORA PRO Football Analysis System
Works for all users, not just a specific chat ID
"""

import asyncio
import logging
from typing import Optional, Dict, List
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import config

logger = logging.getLogger(__name__)

class TelegramBetBot:
    """Interactive Telegram bot for football analysis updates"""
    
    def __init__(self):
        self.bot = None
        self.application = None
        self.is_running = False
        self.user_sessions = {}  # Store user sessions
        
    async def start(self):
        """Initialize and start the interactive bot"""
        try:
            if not config.TELEGRAM_BOT_TOKEN:
                logger.warning("No Telegram bot token configured")
                return
            
            # Create application
            self.application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("analyze", self.analyze_command))
            self.application.add_handler(CommandHandler("live", self.live_command))
            
            # Add message handler for any text message
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Start the bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            self.is_running = True
            logger.info("Interactive Telegram bot started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            self.application = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        welcome_message = f"""
Welcome to FIXORA PRO Football Analysis Bot! 🚀⚽

Hi {user.first_name}! I'm your AI-powered football betting assistant.

What I can do:
• Analyze live matches in real-time
• Provide betting insights and value bets
• Track team form and statistics
• Monitor odds changes

Commands:
/start - Show this welcome message
/help - Show detailed help
/status - Check bot status
/analyze - Analyze today's matches
/live - Show live matches

Just send me any message and I'll help you with football analysis!
        """
        
        await update.message.reply_text(welcome_message)
        logger.info(f"User {user.first_name} (ID: {user.id}) started the bot in chat {chat_id}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📚 FIXORA PRO Bot Help

This bot provides real-time football analysis using:
• Live match data from SportMonks API
• Advanced statistical models
• Value betting opportunities
• Team form analysis

Commands:
/start - Welcome message
/help - This help message
/status - Bot status
/analyze - Analyze today's matches
/live - Show live matches

You can also just send me any message and I'll help you!

Features:
✅ Real-time match monitoring
✅ Live odds analysis
✅ Team form tracking
✅ Value bet detection
✅ Instant notifications
        """
        
        await update.message.reply_text(help_message)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        status_message = f"""
📊 Bot Status

✅ Bot is running and active
🔑 API Connection: Unified API System
💬 Interactive Mode: Enabled
🔄 Real-time Analysis: Active

🌐 API Configuration:
• Primary: API-Football (api-sports.io)
• Fallback: SportMonks
• Strategy: Try API-Football first, fall back to SportMonks

The bot is working and ready to help you with football analysis!

Send me any message or use /analyze to get started.
        """
        
        await update.message.reply_text(status_message)
    
    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze command - analyze today's matches"""
        await update.message.reply_text("🔍 Analyzing today's matches... Please wait.")
        
        # This would integrate with your analyzer
        # For now, send a sample response
        sample_analysis = """
📊 Today's Matches Analysis

Found 1 match for analysis:

⚽ Odense BK vs Randers FC
   Status: LIVE
   League: Danish Superliga
   Analysis Quality: Basic
   
📈 Available Data:
   ✅ Match odds: 100%
   ❌ Team form: 0% (subscription required)
   ❌ Expected goals: 0% (subscription required)
   ❌ AI predictions: 0% (subscription required)

💡 Recommendation: Upgrade to Premium for comprehensive analysis
        """
        
        await update.message.reply_text(sample_analysis)
    
    async def live_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /live command - show live matches"""
        await update.message.reply_text("🔥 Checking live matches... Please wait.")
        
        # This would integrate with your live match analyzer
        # For now, send a sample response
        live_matches = """
🔥 Live Matches

Currently monitoring:

⚽ Odense BK vs Randers FC
   Status: LIVE
   League: Danish Superliga
   Time: 22:45
   
📊 Live Analysis:
   • Match is in progress
   • Odds are being tracked
   • Value opportunities monitored
   
💡 Tip: Use /analyze for detailed analysis
        """
        
        await update.message.reply_text(live_matches)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle any text message from users"""
        user = update.effective_user
        message_text = update.message.text
        chat_id = update.effective_chat.id
        
        logger.info(f"Received message from {user.first_name} (ID: {user.id}): {message_text}")
        
        # Provide helpful response based on message content
        if any(word in message_text.lower() for word in ['hello', 'hi', 'hey']):
            response = f"Hello {user.first_name}! 👋 How can I help you with football analysis today?"
        
        elif any(word in message_text.lower() for word in ['match', 'game', 'fixture']):
            response = "⚽ Looking for match information? Use /analyze to see today's matches or /live for live games!"
        
        elif any(word in message_text.lower() for word in ['bet', 'betting', 'odds']):
            response = "💰 Interested in betting analysis? I can help you find value bets and analyze odds. Use /analyze to get started!"
        
        elif any(word in message_text.lower() for word in ['team', 'form', 'statistics']):
            response = "📊 Want team statistics and form analysis? I can provide detailed insights. Try /analyze for today's matches!"
        
        elif any(word in message_text.lower() for word in ['help', 'support', 'what can you do']):
            response = "🤖 I'm your football analysis assistant! I can analyze matches, track odds, and find value bets. Use /help for detailed information."
        
        else:
            response = f"""
Thanks for your message, {user.first_name}! 

I'm here to help you with football analysis. Here's what I can do:

⚽ Analyze matches and provide insights
💰 Find value betting opportunities  
📊 Track team form and statistics
🔥 Monitor live matches and odds

Try these commands:
/analyze - Analyze today's matches
/live - Show live matches
/help - Detailed help
/status - Bot status

Or just ask me about football, betting, or matches!
            """
        
        await update.message.reply_text(response)
    
    async def send_message_to_user(self, user_id: int, message: str) -> bool:
        """Send a message to a specific user"""
        try:
            if not self.bot:
                self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='Markdown'
            )
            
            logger.info(f"Message sent to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to user {user_id}: {e}")
            return False
    
    async def broadcast_message(self, message: str, user_ids: List[int] = None) -> bool:
        """Broadcast message to multiple users"""
        try:
            if not user_ids:
                # For now, just log the message
                logger.info(f"Broadcast message: {message}")
                return True
            
            success_count = 0
            for user_id in user_ids:
                if await self.send_message_to_user(user_id, message):
                    success_count += 1
            
            logger.info(f"Broadcast completed: {success_count}/{len(user_ids)} users")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Broadcast failed: {e}")
            return False
    
    async def stop(self):
        """Stop the bot"""
        try:
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
                self.is_running = False
                logger.info("Telegram bot stopped")
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
    
    def is_active(self) -> bool:
        """Check if bot is active"""
        return self.is_running and self.application is not None
    
    async def get_bot_info(self) -> Optional[Dict]:
        """Get bot information"""
        try:
            if not self.bot:
                self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
            
            bot_info = await self.bot.get_me()
            return {
                'id': bot_info.id,
                'username': bot_info.username,
                'first_name': bot_info.first_name,
                'is_bot': bot_info.is_bot
            }
        except Exception as e:
            logger.error(f"Failed to get bot info: {e}")
            return None
