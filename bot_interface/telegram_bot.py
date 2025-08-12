import asyncio
import datetime
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from typing import Dict, List, Optional
import config
import json
import os
import logging

logger = logging.getLogger(__name__)

class TelegramBetBot:
    """
    Telegram bot for posting value bets and managing betting operations
    """
    
    def __init__(self, token: str = None):
        self.token = token or config.TELEGRAM_BOT_TOKEN
        self.bot = Bot(token=self.token)
        self.chat_id = self.load_chat_id() or config.TELEGRAM_CHAT_ID
        self.application = None
        
    async def start(self):
        """Start the Telegram bot"""
        self.application = Application.builder().token(self.token).build()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("setchat", self.set_chat_command))
        self.application.add_handler(CommandHandler("analyze", self.analyze_command))
        self.application.add_handler(CommandHandler("live", self.live_command))
        
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
/analyze - Analyze today's matches
/live - Get live match analysis

💡 Tip: Use /analyze to get instant analysis of today's matches!
        """
        await update.message.reply_text(help_message)

    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze command - analyze today's matches"""
        await update.message.reply_text("🔍 Analyzing today's matches... Please wait.")
        
        try:
            # Import here to avoid circular imports
            from api.unified_api_client import UnifiedAPIClient
            
            client = UnifiedAPIClient()
            
            # Get today's matches
            matches = await client.get_today_matches(include_live=True)
            
            if not matches:
                await update.message.reply_text("📅 No matches found for today.")
                await client.close()
                return
            
            # Analyze first few matches
            analysis_results = []
            subscription_limits = []
            
            for i, match in enumerate(matches[:5]):  # Limit to 5 matches
                try:
                    # Extract basic info
                    home_team, away_team = self.extract_team_names(match)
                    status = self.extract_match_status(match)
                    
                    # Try to get rich data
                    odds = await client.safe_match_odds(match)
                    predictions = await client.safe_predictions(match)
                    stats = await client.safe_fixture_statistics(match)
                    
                    # Determine data quality
                    data_quality = self.assess_data_quality(odds, predictions, stats)
                    
                    analysis_results.append({
                        'match': f"{home_team} vs {away_team}",
                        'status': status,
                        'quality': data_quality,
                        'odds_available': bool(odds),
                        'predictions_available': bool(predictions),
                        'stats_available': bool(stats)
                    })
                    
                    # Check for subscription limitations
                    if not odds and not predictions and not stats:
                        subscription_limits.append(f"{home_team} vs {away_team}")
                        
                except Exception as e:
                    logger.error(f"Error analyzing match {i}: {e}")
                    continue
            
            await client.close()
            
            # Create analysis message
            message = "🔍 Today's Matches Analysis\n\n"
            
            for result in analysis_results:
                quality_emoji = "🟢" if result['quality'] == "High" else "🟡" if result['quality'] == "Medium" else "🔴"
                message += f"{quality_emoji} {result['match']}\n"
                message += f"   📊 Status: {result['status']}\n"
                message += f"   📈 Quality: {result['quality']}\n"
                message += f"   💰 Odds: {'✅' if result['odds_available'] else '❌'}\n"
                message += f"   🔮 Predictions: {'✅' if result['predictions_available'] else '❌'}\n"
                message += f"   📊 Stats: {'✅' if result['stats_available'] else '❌'}\n\n"
            
            # Add subscription information
            if subscription_limits:
                message += "⚠️ Subscription Limitations:\n"
                message += "Some matches have limited data due to subscription plan restrictions.\n"
                message += "Consider upgrading for full access to:\n"
                message += "• Live odds and predictions\n"
                message += "• Detailed statistics\n"
                message += "• Advanced analysis features\n\n"
            
            message += f"📊 Total matches analyzed: {len(analysis_results)}"
            
            await update.message.reply_text(message)
            
        except Exception as e:
            error_msg = f"❌ Analysis failed: {str(e)}"
            await update.message.reply_text(error_msg)
            logger.error(f"Analysis command failed: {e}")

    async def live_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /live command - get live match analysis"""
        await update.message.reply_text("⚽ Getting live match analysis... Please wait.")
        
        try:
            # Import here to avoid circular imports
            from api.unified_api_client import UnifiedAPIClient
            
            client = UnifiedAPIClient()
            
            # Get live matches
            live_matches = await client.get_live_scores()
            
            if not live_matches:
                await update.message.reply_text("📺 No live matches currently.")
                await client.close()
                return
            
            # Analyze live matches
            live_analysis = []
            
            for match in live_matches[:3]:  # Limit to 3 live matches
                try:
                    home_team, away_team = self.extract_team_names(match)
                    status = self.extract_match_status(match)
                    score = self.extract_score(match)
                    
                    # Try to get live odds
                    live_odds = await client.safe_live_odds(match)
                    
                    live_analysis.append({
                        'match': f"{home_team} vs {away_team}",
                        'status': status,
                        'score': f"{score[0]}-{score[1]}",
                        'live_odds': bool(live_odds)
                    })
                    
                except Exception as e:
                    logger.error(f"Error analyzing live match: {e}")
                    continue
            
            await client.close()
            
            # Create live analysis message
            message = "⚽ Live Matches Analysis\n\n"
            
            for analysis in live_analysis:
                message += f"🔥 {analysis['match']}\n"
                message += f"   📊 Status: {analysis['status']}\n"
                message += f"   🎯 Score: {analysis['score']}\n"
                message += f"   💰 Live Odds: {'✅' if analysis['live_odds'] else '❌'}\n\n"
            
            message += f"📺 Total live matches: {len(live_analysis)}"
            
            await update.message.reply_text(message)
            
        except Exception as e:
            error_msg = f"❌ Live analysis failed: {str(e)}"
            await update.message.reply_text(error_msg)
            logger.error(f"Live command failed: {e}")

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
        
        # Save to config and file
        config.TELEGRAM_CHAT_ID = chat_id
        self.save_chat_id(chat_id)
        
        await update.message.reply_text(f"✅ Chat ID set to: {chat_id}")
        print(f"Chat ID set to: {chat_id}")
        print("Chat ID has been saved and will be remembered for future runs!")
    
    async def post_value_bets(self, value_bets: List[Dict], match_info: Dict = None):
        """
        Post value bets to Telegram channel with premium analysis
        
        Args:
            value_bets: List of value bets found
            match_info: Match information (optional)
        """
        if not self.chat_id:
            print("Warning: Chat ID not set. Use /setchat command in bot.")
            print("To fix this:")
            print("1. Start the bot with: python main.py")
            print("2. Send /setchat command to your bot in Telegram")
            print("3. The bot will automatically save your chat ID")
            return
        
        if not value_bets:
            print("No value bets found to post")
            return
        
        # Create premium message
        message = "🎯 PREMIUM VALUE BETS FOUND!\n\n"
        
        # Add analysis summary
        total_bets = len(value_bets)
        avg_edge = sum(bet['edge'] for bet in value_bets) / total_bets * 100
        avg_confidence = sum(bet.get('confidence', 0.7) for bet in value_bets) / total_bets * 100
        
        message += f"📊 Analysis Summary:\n"
        message += f"• Total Value Bets: {total_bets}\n"
        message += f"• Average Edge: {avg_edge:.1f}%\n"
        message += f"• Average Confidence: {avg_confidence:.1f}%\n\n"
        
        # Add each value bet with premium details
        for i, bet in enumerate(value_bets[:5], 1):  # Limit to top 5 bets
            market = bet['market'].replace('_', ' ').title()
            selection = bet['selection'].replace('_', ' ').title()
            odds = bet['odds']
            edge = bet['edge'] * 100  # Convert to percentage
            confidence = bet.get('confidence', 0.7) * 100
            
            # Add match info if available
            if 'match_info' in bet:
                home_team = bet['match_info'].get('home_team', 'Home Team')
                away_team = bet['match_info'].get('away_team', 'Away Team')
                message += f"{i}. ⚽ {home_team} vs {away_team}\n"
            else:
                message += f"{i}. {market} - {selection}\n"
            
            message += f"   🎯 {market} - {selection}\n"
            message += f"   📊 Odds: {odds:.2f}\n"
            message += f"   📈 Edge: {edge:.1f}%\n"
            message += f"   🎯 Confidence: {confidence:.1f}%\n"
            
            # Add premium features if available
            if 'kelly_percentage' in bet:
                kelly = bet['kelly_percentage'] * 100
                message += f"   💰 Kelly %: {kelly:.1f}%\n"
            
            if 'recommended_stake' in bet:
                stake = bet['recommended_stake']
                message += f"   💵 Recommended: £{stake:.2f}\n"
            
            if 'risk_score' in bet:
                risk = bet['risk_score']
                message += f"   ⚠️ Risk Score: {risk:.3f}\n"
            
            message += "\n"
        
        if len(value_bets) > 5:
            message += f"... and {len(value_bets) - 5} more value bets found.\n\n"
        
        # Add premium footer
        message += "🔬 Premium Analysis Features:\n"
        message += "• Multi-model predictions (Elo + xG + Corners)\n"
        message += "• Advanced risk management\n"
        message += "• Kelly Criterion optimization\n"
        message += "• Confidence scoring\n\n"
        
        message += "⚠️ Bet responsibly and never bet more than you can afford to lose."
        
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            print(f"Posted {len(value_bets)} premium value bets to Telegram")
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
    
    async def post_startup_message(self):
        """Post startup message when real-time monitor starts"""
        if not self.chat_id:
            return
        
        message = """
🚀 Real-Time Betting Monitor Started!

✅ System is now running and monitoring for new matches
🔄 Checking every 5 minutes for new matches
💎 Value bets will be posted automatically when found
📊 Real-time analysis using live API data

🔧 Features:
• Live match monitoring
• Real-time odds analysis
• Multi-model predictions (Elo + xG + Corners)
• Automatic value bet detection
• Instant Telegram notifications

⏰ Started at: {time}
        """.format(time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            print("Posted startup message to Telegram")
        except Exception as e:
            print(f"Failed to post startup message: {e}")
    
    async def post_no_matches_message(self):
        """Post message when no matches are found"""
        if not self.chat_id:
            return
        
        message = """
🔍 No Matches Found

Currently no matches available for analysis.

The system will automatically check again in 5 minutes.

⏰ Last checked: {time}

💡 Tips:
• Check back later for new matches
• The system analyzes matches from major leagues
• Value bets are posted automatically when found

🔧 Available Commands:
• /analyze - Analyze today's matches
• /live - Get live match analysis
• /status - Check bot status
        """.format(time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
        
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            print("Posted 'no matches' message to Telegram")
        except Exception as e:
            print(f"Failed to post no matches message: {e}")

    async def post_subscription_upgrade_message(self, limited_features: List[str]):
        """Post message about subscription limitations and upgrade suggestions"""
        if not self.chat_id:
            return
        
        message = """
⚠️ Subscription Limitations Detected

Some features are limited due to your current subscription plan.

Limited Features:
{limited_features}

🚀 Upgrade Benefits:
• Full access to live odds and predictions
• Detailed match statistics and xG data
• Advanced analysis features
• Priority API access
• No rate limiting

💡 Current Plan Features:
• Basic match information
• Limited odds data
• Basic predictions
• Standard API access

🔧 Commands Available:
• /analyze - Basic match analysis
• /live - Live match status
• /status - Bot status

To upgrade, visit your API provider's website or contact support.
        """.format(limited_features="\n".join([f"• {feature}" for feature in limited_features]))
        
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            print("Posted subscription upgrade message to Telegram")
        except Exception as e:
            print(f"Failed to post subscription message: {e}")

    async def post_data_quality_summary(self, analysis_results: List[Dict]):
        """Post summary of data quality across matches"""
        if not self.chat_id:
            return
        
        # Count data quality levels
        high_quality = sum(1 for r in analysis_results if r['quality'] == 'High')
        medium_quality = sum(1 for r in analysis_results if r['quality'] == 'Medium')
        basic_quality = sum(1 for r in analysis_results if r['quality'] == 'Basic')
        
        # Count available features
        total_odds = sum(1 for r in analysis_results if r['odds_available'])
        total_predictions = sum(1 for r in analysis_results if r['predictions_available'])
        total_stats = sum(1 for r in analysis_results if r['stats_available'])
        
        message = f"""
📊 Data Quality Summary

📈 Quality Breakdown:
• 🟢 High Quality: {high_quality} matches
• 🟡 Medium Quality: {medium_quality} matches  
• 🔴 Basic Quality: {basic_quality} matches

🔧 Feature Availability:
• 💰 Odds: {total_odds}/{len(analysis_results)} matches
• 🔮 Predictions: {total_predictions}/{len(analysis_results)} matches
• 📊 Statistics: {total_stats}/{len(analysis_results)} matches

💡 Quality Indicators:
• 🟢 High: 2+ premium features available
• 🟡 Medium: 1 premium feature available
• 🔴 Basic: Basic match info only

{self._get_subscription_recommendation(high_quality, len(analysis_results))}
        """
        
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            print("Posted data quality summary to Telegram")
        except Exception as e:
            print(f"Failed to post data quality summary: {e}")

    def _get_subscription_recommendation(self, high_quality: int, total_matches: int) -> str:
        """Get subscription recommendation based on data quality"""
        quality_percentage = (high_quality / total_matches * 100) if total_matches > 0 else 0
        
        if quality_percentage >= 80:
            return "✅ Excellent data quality! Your current plan is working well."
        elif quality_percentage >= 50:
            return "⚠️ Moderate data quality. Consider upgrading for better analysis."
        else:
            return "❌ Limited data quality. Upgrade recommended for full features."
    
    def stop(self):
        """Stop the Telegram bot"""
        if self.application:
            asyncio.create_task(self.application.stop())
            print("Telegram bot stopped")
    
    def save_chat_id(self, chat_id: int):
        """Save chat ID to a file for persistence"""
        try:
            with open('telegram_chat_id.txt', 'w') as f:
                f.write(str(chat_id))
            print(f"Chat ID {chat_id} saved to file")
        except Exception as e:
            print(f"Failed to save chat ID: {e}")
    
    def load_chat_id(self) -> Optional[int]:
        """Load chat ID from file"""
        try:
            if os.path.exists('telegram_chat_id.txt'):
                with open('telegram_chat_id.txt', 'r') as f:
                    chat_id = int(f.read().strip())
                    print(f"Loaded chat ID from file: {chat_id}")
                    return chat_id
        except Exception as e:
            print(f"Failed to load chat ID: {e}")
        return None

    def assess_data_quality(self, odds, predictions, stats) -> str:
        """Assess the quality of available data"""
        available_features = sum([bool(odds), bool(predictions), bool(stats)])
        
        if available_features >= 2:
            return "High"
        elif available_features == 1:
            return "Medium"
        else:
            return "Basic"

    def extract_team_names(self, fixture: Dict) -> tuple:
        """Extract team names from fixture data"""
        try:
            # Try API-Football format first
            if 'teams' in fixture:
                home_team = fixture['teams'].get('home', {}).get('name', 'Home Team')
                away_team = fixture['teams'].get('away', {}).get('name', 'Away Team')
                return home_team, away_team
            
            # Try SportMonks format
            elif 'participants' in fixture:
                home_team = "Home Team"
                away_team = "Away Team"
                for participant in fixture['participants']:
                    if participant.get('meta', {}).get('location') == 'home':
                        home_team = participant.get('name', 'Home Team')
                    elif participant.get('meta', {}).get('location') == 'away':
                        away_team = participant.get('name', 'Away Team')
                return home_team, away_team
            
            else:
                return "Home Team", "Away Team"
                
        except Exception:
            return "Home Team", "Away Team"

    def extract_match_status(self, fixture: Dict) -> str:
        """Extract match status from fixture data"""
        try:
            # Try API-Football format
            if 'fixture' in fixture and 'status' in fixture['fixture']:
                return fixture['fixture']['status']['short']
            
            # Try SportMonks format
            elif 'time' in fixture and 'status' in fixture['time']:
                return fixture['time']['status']
            
            # Fallback
            return "Unknown"
            
        except Exception:
            return "Unknown"

    def extract_score(self, fixture: Dict) -> tuple:
        """Extract current score from fixture data"""
        try:
            # Try API-Football format
            if 'goals' in fixture:
                home_score = fixture['goals'].get('home', 0)
                away_score = fixture['goals'].get('away', 0)
                return home_score, away_score
            
            # Try SportMonks format
            elif 'scores' in fixture and fixture['scores']:
                for score in fixture['scores']:
                    if score.get('description') == 'CURRENT':
                        home_score = score.get('score', {}).get('participant_1', 0)
                        away_score = score.get('score', {}).get('participant_2', 0)
                        return home_score, away_score
            
            # Fallback
            return 0, 0
            
        except Exception:
            return 0, 0
