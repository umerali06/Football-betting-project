import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from typing import Dict, List, Optional
import config
import json
import os

class TelegramBetBot:
    """
    Telegram bot for posting value bets and managing betting operations
    """
    
    def __init__(self, token: str = None):
        self.token = token or config.TELEGRAM_BOT_TOKEN
        self.bot = Bot(token=self.token)
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.application = None
        
    async def start(self):
        """Start the Telegram bot"""
        self.application = Application.builder().token(self.token).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("setchat", self.set_chat_command))
        
        # Start the bot
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        print("Telegram bot started successfully!")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 Football Betting Bot Started!

This bot will post daily value bets based on xG + Elo ratings analysis.

Commands:
/start - Start the bot
/help - Show help
/status - Check bot status
/setchat - Set chat ID for bet notifications

The bot will automatically post value bets when found.
        """
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📚 Football Betting Bot Help

This bot analyzes football matches using:
• Expected Goals (xG) model
• Elo rating system
• Value betting analysis

Supported Markets:
• Match Result (Home/Draw/Away)
• Both Teams to Score (BTTS)
• Over/Under Goals
• Corners

Value bets are posted when the model probability exceeds bookmaker odds by 5% or more.

Commands:
/start - Start the bot
/help - Show this help
/status - Check bot status
/setchat - Set chat ID for notifications
        """
        await update.message.reply_text(help_message)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        status_message = f"""
📊 Bot Status

✅ Bot is running
🔑 API Key: {'✅ Set' if self.token else '❌ Missing'}
💬 Chat ID: {'✅ Set' if self.chat_id else '❌ Not set'}

To set chat ID for notifications, use /setchat
        """
        await update.message.reply_text(status_message)
    
    async def set_chat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /setchat command to set chat ID for notifications"""
        chat_id = update.message.chat_id
        self.chat_id = chat_id
        
        # Save to config
        config.TELEGRAM_CHAT_ID = chat_id
        
        await update.message.reply_text(f"✅ Chat ID set to: {chat_id}")
        print(f"Chat ID set to: {chat_id}")
    
    async def post_value_bets(self, value_bets: List[Dict], match_info: Dict = None):
        """
        Post value bets to Telegram channel
        
        Args:
            value_bets: List of value bets found
            match_info: Match information (optional)
        """
        if not self.chat_id:
            print("Warning: Chat ID not set. Use /setchat command in bot.")
            return
        
        if not value_bets:
            return
        
        # Create message
        message = "🎯 VALUE BETS FOUND!\n\n"
        
        if match_info:
            home_team = match_info.get('home_team', 'Home Team')
            away_team = match_info.get('away_team', 'Away Team')
            match_time = match_info.get('match_time', 'TBD')
            
            message += f"⚽ {home_team} vs {away_team}\n"
            message += f"🕐 {match_time}\n\n"
        
        # Add each value bet
        for i, bet in enumerate(value_bets[:5], 1):  # Limit to top 5 bets
            market = bet['market'].replace('_', ' ').title()
            selection = bet['selection'].replace('_', ' ').title()
            odds = bet['odds']
            edge = bet['edge'] * 100  # Convert to percentage
            confidence = bet['confidence'] * 100
            
            message += f"{i}. {market} - {selection}\n"
            message += f"   📊 Odds: {odds:.2f}\n"
            message += f"   📈 Edge: {edge:.1f}%\n"
            message += f"   🎯 Confidence: {confidence:.1f}%\n\n"
        
        if len(value_bets) > 5:
            message += f"... and {len(value_bets) - 5} more value bets found.\n\n"
        
        message += "⚠️ Bet responsibly and never bet more than you can afford to lose."
        
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            print(f"Posted {len(value_bets)} value bets to Telegram")
        except Exception as e:
            print(f"Failed to post to Telegram: {e}")
    
    async def post_daily_summary(self, summary_data: Dict):
        """
        Post daily betting summary
        
        Args:
            summary_data: Dictionary with summary statistics
        """
        if not self.chat_id:
            return
        
        message = "📊 Daily Betting Summary\n\n"
        
        # Add summary statistics
        total_bets = summary_data.get('total_bets', 0)
        value_bets_found = summary_data.get('value_bets_found', 0)
        avg_edge = summary_data.get('average_edge', 0) * 100
        total_roi = summary_data.get('total_roi', 0) * 100
        
        message += f"🎯 Total Bets Analyzed: {total_bets}\n"
        message += f"💎 Value Bets Found: {value_bets_found}\n"
        message += f"📈 Average Edge: {avg_edge:.1f}%\n"
        message += f"💰 Total ROI: {total_roi:.1f}%\n\n"
        
        message += "📅 Next analysis scheduled for tomorrow."
        
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            print("Posted daily summary to Telegram")
        except Exception as e:
            print(f"Failed to post daily summary: {e}")
    
    async def post_error_message(self, error_message: str):
        """Post error message to Telegram"""
        if not self.chat_id:
            return
        
        message = f"❌ Bot Error\n\n{error_message}"
        
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
        except Exception as e:
            print(f"Failed to post error message: {e}")
    
    def stop(self):
        """Stop the Telegram bot"""
        if self.application:
            asyncio.create_task(self.application.stop())
            print("Telegram bot stopped")
