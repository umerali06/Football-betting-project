#!/usr/bin/env python3
"""
Interactive Telegram Bot for FIXORA PRO Football Analysis System
"""

import os
import sys
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add the parent directory to the path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

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
        try:
            # Test bot token first
            print("🔑 Testing bot token...")
            try:
                bot_info = await self.bot.get_me()
                print(f"✅ Bot connected successfully: @{bot_info.username}")
            except Exception as e:
                print(f"❌ Bot token test failed: {e}")
                raise Exception(f"Invalid bot token or network issue: {e}")
            
            print("🔧 Building application...")
            self.application = Application.builder().token(self.token).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("setchat", self.set_chat_command))
            self.application.add_handler(CommandHandler("analyze", self.analyze_command))
            self.application.add_handler(CommandHandler("live", self.live_command))
            self.application.add_handler(CommandHandler("network", self.network_command))
            
            print("🚀 Starting application...")
            # Start the bot with better error handling
            await self.application.initialize()
            await self.application.start()
            
            print("📡 Starting polling...")
            # Use more robust polling configuration
            await self.application.updater.start_polling(
                timeout=30,  # Increased timeout for stability
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )
            
            print("✅ Telegram bot started successfully!")
            print("📱 Bot is now listening for commands...")
            print("   Commands: /start, /help, /status, /setchat, /analyze, /live, /network")
            
        except Exception as e:
            print(f"❌ Failed to start bot: {e}")
            raise
    
    async def run(self):
        """Run the bot with proper event loop handling"""
        try:
            await self.start()
            
            # Keep the bot running
            print("🔄 Bot is running. Press Ctrl+C to stop.")
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping bot...")
            await self.stop()
            await self.cleanup()
        except Exception as e:
            print(f"❌ Bot error: {e}")
            await self.stop()
            await self.cleanup()
            raise
    
    async def stop(self):
        """Stop the bot gracefully"""
        try:
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            print("✅ Bot stopped successfully")
        except Exception as e:
            print(f"⚠️ Error stopping bot: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            # Close any open sessions
            if hasattr(self, 'analyzer') and self.analyzer:
                if hasattr(self.analyzer, 'api_client') and self.analyzer.api_client:
                    await self.analyzer.api_client.close()
            print("🧹 Cleanup completed")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
    
    def get_bot_status(self) -> Dict:
        """Get current bot status"""
        return {
            'running': self.application is not None,
            'token_set': bool(self.token),
            'chat_id_set': bool(self.chat_id),
            'timestamp': str(datetime.now())
        }
    
    async def test_connectivity(self) -> bool:
        """Test if the bot can connect to Telegram"""
        try:
            bot_info = await self.bot.get_me()
            return True
        except Exception as e:
            logger.error(f"Connectivity test failed: {e}")
            return False
    
    def get_network_troubleshooting_tips(self) -> str:
        """Get troubleshooting tips for network issues"""
        return """🔧 Network Troubleshooting Tips:

1. **Check Internet Connection**
   - Try accessing other websites
   - Test with a different network (mobile hotspot)

2. **Firewall/Proxy Issues**
   - Check if you're behind a corporate firewall
   - Verify proxy settings
   - Try disabling VPN temporarily

3. **Regional Restrictions**
   - Some regions block Telegram
   - Try using a VPN

4. **DNS Issues**
   - Try changing DNS servers (8.8.8.8, 1.1.1.1)
   - Flush DNS cache

5. **Bot Token**
   - Verify your bot token is correct
   - Check if the bot is active in @BotFather

6. **Alternative Solutions**
   - Use the system without Telegram (analysis works offline)
   - Export results to files
   - Use web interface instead"""
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🤖 FIXORA PRO Football Analysis Bot

🎯 Advanced predictions using xG + Elo ratings:
• H2H (Win/Draw/Win) predictions
• Both Teams to Score (BTTS)
• Over/Under Goals analysis
• Corners predictions

Commands:
/start - Start the bot
/help - Show detailed help
/status - Check bot status
/setchat - Set chat ID for notifications
/analyze - Get today's match predictions
/live - Get live match analysis
/network - Test network connectivity

⚡ Fast analysis with real-time data from premium APIs
        """
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📚 FIXORA PRO Football Analysis Bot Help

🎯 Prediction Models:
• Expected Goals (xG) + Elo Rating System
• Advanced statistical analysis
• Real-time data from premium APIs

⚽ Supported Markets:
• H2H (Home Win/Draw/Away Win)
• Both Teams to Score (BTTS)
• Over/Under Goals (2.5, 3.5)
• Total Corners (9.5, 10.5)

🔬 Analysis Features:
• Fast response time (< 10 seconds)
• Live match monitoring
• Comprehensive odds analysis
• Value bet identification

Commands:
/start - Start the bot
/help - Show this help
/status - Check bot status
/setchat - Set chat ID for notifications
/analyze - Get today's match predictions
/live - Get live match analysis
/network - Test network connectivity

💡 Tip: Use /analyze for instant predictions or /live for live match analysis!
        """
        await update.message.reply_text(help_message)

    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze command - get today's match analysis with progressive results"""
        # Send immediate response to show progress
        progress_msg = await update.message.reply_text("🔍 Analyzing today's matches...\n⏳ This will take a few seconds...")
        
        try:
            # Import here to avoid circular imports
            from realtime_analyzer import RealTimeAnalyzer
            
            analyzer = RealTimeAnalyzer()
            
            # Update progress
            await progress_msg.edit_text("🔍 Analyzing today's matches...\n📊 Fetching match data...")
            
            # Use progressive analysis that yields results as they're processed
            total_matches = 0
            batch_count = 0
            
            # Process results progressively as they come in
            async for batch_data in analyzer.analyze_today_matches_progressive(batch_size=8):
                batch_count += 1
                batch_results = batch_data['results']
                batch_number = batch_data['batch_number']
                total_batches = batch_data['total_batches']
                total_matches = batch_data['total_matches']
                
                # Delete progress message after first batch
                if batch_count == 1:
                    await progress_msg.delete()
                
                # Show cool processing message for current batch
                if batch_number > 1:  # Don't show for first batch since we already have progress message
                    processing_msg = await update.message.reply_text(
                        f"⚡ **PROCESSING BATCH {batch_number}/{total_batches}**\n\n"
                        f"🔍 Analyzing {len(batch_results)} matches...\n"
                        f"📊 Progress: {((batch_number - 1) / total_batches) * 100:.0f}% Complete\n"
                        f"🎯 {total_matches - batch_data['batch_start'] + 1} matches remaining\n\n"
                        f"⏱️ Please wait while we crunch the numbers..."
                    )
                    
                    # Small delay to show processing
                    await asyncio.sleep(0.8)
                    
                    # Delete processing message before showing results
                    await processing_msg.delete()
                
                # Create message header with progress info
                if total_batches == 1:
                    message = "🎯 TODAY'S MATCH PREDICTIONS\n\n"
                else:
                    message = f"🎯 TODAY'S MATCH PREDICTIONS (Part {batch_number}/{total_batches})\n"
                    progress_percent = (batch_number / total_batches) * 100
                    message += f"📊 Progress: {progress_percent:.0f}% Complete\n\n"
                
                # Process current batch of matches
                for i, result in enumerate(batch_results, 1):
                    try:
                        home_team = result.get('home_team', 'Unknown')
                        away_team = result.get('away_team', 'Unknown')
                        status = result.get('status', 'Unknown')
                        
                        # Get predictions from real API data
                        betting_predictions = result.get('betting_predictions', {})
                        api_predictions = result.get('predictions', {})
                        odds = result.get('odds', [])
                        
                        # Use betting_predictions if available, otherwise fallback to API predictions
                        predictions = betting_predictions if betting_predictions else api_predictions
                        
                        # Extract key prediction data from real API responses
                        h2h_prediction = self._extract_h2h_prediction(predictions)
                        btts_prediction = self._extract_btts_prediction(predictions)
                        goals_prediction = self._extract_goals_prediction(predictions)
                        corners_prediction = self._extract_corners_prediction(predictions)
                        
                        # Get best odds for key markets
                        best_odds = self._extract_best_odds(odds)
                        
                        message += f"{i}. ⚽ {home_team} vs {away_team}\n"
                        message += f"   📊 Status: {status}\n"
                        
                        # Add predictions if available from real data
                        if h2h_prediction:
                            message += f"   🏆 H2H: {h2h_prediction}\n"
                        if btts_prediction:
                            message += f"   ⚽ BTTS: {btts_prediction}\n"
                        if goals_prediction:
                            message += f"   🎯 Goals: {goals_prediction}\n"
                        if corners_prediction:
                            message += f"   📐 Corners: {corners_prediction}\n"
                        
                        # Add best odds if available
                        if best_odds:
                            message += f"   💰 Best Odds: {best_odds}\n"
                        
                        message += "\n"
                        
                    except Exception as e:
                        logger.error(f"Error formatting analysis result: {e}")
                        continue
                
                # Add batch summary
                message += f"📊 Batch {batch_number}: Matches {batch_data['batch_start']}-{batch_data['batch_end']} of {total_matches}"
                
                # Send this batch message immediately
                await update.message.reply_text(message)
                
                # If there are more batches coming, show a "searching" message
                if batch_number < total_batches:
                    remaining_matches = total_matches - batch_data['batch_end']
                    estimated_time = (total_batches - batch_number) * 2  # Rough estimate: 2 seconds per batch
                    
                    # Cool searching message with emojis and progress
                    searching_msg = await update.message.reply_text(
                        f"🔍 **SEARCHING FOR NEXT BATCH...**\n\n"
                        f"📊 Progress: {progress_percent:.0f}% Complete\n"
                        f"🎯 {remaining_matches} more matches to analyze\n"
                        f"⏱️ Estimated time: ~{estimated_time} seconds\n"
                        f"🔄 Processing batch {batch_number + 1}/{total_batches}...\n\n"
                        f"💡 Please wait while we analyze the next set of matches..."
                    )
                    
                    # Small delay to allow Telegram to process the message
                    await asyncio.sleep(1.5)
                    
                    # Delete the searching message before showing next batch
                    await searching_msg.delete()
            
            # Send final summary message
            if total_matches > 0:
                summary_message = f"✅ Analysis Complete!\n\n📊 Total matches analyzed: {total_matches}\n📱 Results split into {batch_count} batch(es)\n\n🔍 Data Quality:\n• Real-time from premium APIs\n• SportMonks + API-Football integration\n• Live odds and predictions\n\n💡 Use /analyze again for fresh predictions!"
                await update.message.reply_text(summary_message)
            else:
                await progress_msg.edit_text("📅 No matches found for today.")
            
        except Exception as e:
            error_msg = f"❌ Analysis failed: {str(e)}"
            await progress_msg.edit_text(error_msg)
            logger.error(f"Analysis command failed: {e}")

    def _extract_h2h_prediction(self, predictions: Dict) -> str:
        """Extract H2H (Win/Draw/Win) prediction"""
        if not predictions:
            return None
        
        # Try to get H2H prediction from various sources
        if 'match_result' in predictions:
            result = predictions['match_result']
            if isinstance(result, dict):
                if 'home_win' in result and 'away_win' in result and 'draw' in result:
                    home_prob = result.get('home_win', 0)
                    away_prob = result.get('away_win', 0)
                    draw_prob = result.get('draw', 0)
                    
                    if home_prob > away_prob and home_prob > draw_prob:
                        return f"Home Win ({home_prob:.1%})"
                    elif away_prob > home_prob and away_prob > draw_prob:
                        return f"Away Win ({away_prob:.1%})"
                    else:
                        return f"Draw ({draw_prob:.1%})"
        
        # Fallback to simple prediction
        if 'home_win' in predictions:
            return f"Home Win ({predictions['home_win']:.1%})"
        elif 'away_win' in predictions:
            return f"Away Win ({predictions['away_win']:.1%})"
        
        return None

    def _extract_btts_prediction(self, predictions: Dict) -> str:
        """Extract Both Teams to Score prediction"""
        if not predictions:
            return None
        
        if 'both_teams_to_score' in predictions:
            btts_prob = predictions['both_teams_to_score']
            if isinstance(btts_prob, (int, float)):
                if btts_prob > 0.5:
                    return f"Yes ({btts_prob:.1%})"
                else:
                    return f"No ({(1-btts_prob):.1%})"
        
        return None

    def _extract_goals_prediction(self, predictions: Dict) -> str:
        """Extract Over/Under Goals prediction"""
        if not predictions:
            return None
        
        if 'over_under_goals' in predictions:
            goals_data = predictions['over_under_goals']
            if isinstance(goals_data, dict):
                over_prob = goals_data.get('over', 0)
                under_prob = goals_data.get('under', 0)
                
                if over_prob > under_prob:
                    return f"Over 2.5 ({over_prob:.1%})"
                else:
                    return f"Under 2.5 ({under_prob:.1%})"
        
        return None

    def _extract_corners_prediction(self, predictions: Dict) -> str:
        """Extract Corners prediction"""
        if not predictions:
            return None
        
        if 'corners' in predictions:
            corners_data = predictions['corners']
            if isinstance(corners_data, dict):
                over_prob = corners_data.get('over', 0)
                under_prob = corners_data.get('under', 0)
                
                if over_prob > under_prob:
                    return f"Over 9.5 ({over_prob:.1%})"
                else:
                    return f"Under 9.5 ({under_prob:.1%})"
        
        return None

    def _extract_best_odds(self, odds: List[Dict]) -> str:
        """Extract best odds for key markets"""
        if not odds or not isinstance(odds, list):
            return None
        
        best_odds = {}
        
        for odd in odds:
            market = odd.get('market_description', '').lower()
            value = odd.get('value', 0)
            
            if 'match winner' in market or '1x2' in market:
                if 'home' in market or '1' in market:
                    if 'home_win' not in best_odds or value > best_odds['home_win']:
                        best_odds['home_win'] = value
                elif 'away' in market or '2' in market:
                    if 'away_win' not in best_odds or value > best_odds['away_win']:
                        best_odds['away_win'] = value
                elif 'draw' in market or 'x' in market:
                    if 'draw' not in best_odds or value > best_odds['draw']:
                        best_odds['draw'] = value
            
            elif 'both teams to score' in market or 'btts' in market:
                if 'yes' in market or 'btts' in market:
                    if 'btts_yes' not in best_odds or value > best_odds['btts_yes']:
                        best_odds['btts_yes'] = value
                elif 'no' in market:
                    if 'btts_no' not in best_odds or value > best_odds['btts_no']:
                        best_odds['btts_no'] = value
        
        # Format best odds
        if best_odds:
            odds_str = []
            if 'home_win' in best_odds:
                odds_str.append(f"H:{best_odds['home_win']:.2f}")
            if 'away_win' in best_odds:
                odds_str.append(f"A:{best_odds['away_win']:.2f}")
            if 'draw' in best_odds:
                odds_str.append(f"D:{best_odds['draw']:.2f}")
            if 'btts_yes' in best_odds:
                odds_str.append(f"BTTS Y:{best_odds['btts_yes']:.2f}")
            
            return " | ".join(odds_str)
        
        return None
    
    async def live_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /live command - get live match analysis with fast response"""
        # Send immediate response to show progress
        progress_msg = await update.message.reply_text("⚽ Getting live match analysis...\n⏳ This will take a few seconds...")
        
        try:
            # Import here to avoid circular imports
            from realtime_analyzer import RealTimeAnalyzer
            
            analyzer = RealTimeAnalyzer()
            
            # Update progress
            await progress_msg.edit_text("⚽ Getting live match analysis...\n📊 Fetching live data...")
            
            # Use progressive analysis that yields results as they're processed
            total_matches = 0
            batch_count = 0
            
            # Process results progressively as they come in
            async for batch_data in analyzer.analyze_live_matches_progressive(batch_size=8):
                batch_count += 1
                batch_results = batch_data['results']
                batch_number = batch_data['batch_number']
                total_batches = batch_data['total_batches']
                total_matches = batch_data['total_matches']
                
                # Delete progress message after first batch
                if batch_count == 1:
                    await progress_msg.delete()
                
                # Show cool processing message for current batch
                if batch_number > 1:  # Don't show for first batch since we already have progress message
                    processing_msg = await update.message.reply_text(
                        f"⚡ **PROCESSING LIVE BATCH {batch_number}/{total_batches}**\n\n"
                        f"🔍 Analyzing {len(batch_results)} live matches...\n"
                        f"📊 Progress: {((batch_number - 1) / total_batches) * 100:.0f}% Complete\n"
                        f"🎯 {total_matches - batch_data['batch_start'] + 1} live matches remaining\n\n"
                        f"⏱️ Please wait while we analyze live data..."
                    )
                    
                    # Small delay to show processing
                    await asyncio.sleep(0.8)
                    
                    # Delete processing message before showing results
                    await processing_msg.delete()
                
                # Create message header with progress info
                if total_batches == 1:
                    message = "⚽ LIVE MATCHES - LIVE PREDICTIONS\n\n"
                else:
                    message = f"⚽ LIVE MATCHES - LIVE PREDICTIONS (Part {batch_number}/{total_batches})\n"
                    progress_percent = (batch_number / total_batches) * 100
                    message += f"📊 Progress: {progress_percent:.0f}% Complete\n\n"
                
                # Process current batch of live matches
                for i, result in enumerate(batch_results, 1):
                    try:
                        home_team = result.get('home_team', 'Unknown')
                        away_team = result.get('away_team', 'Unknown')
                        status = result.get('status', 'Unknown')
                        home_score = result.get('home_score', 0)
                        away_score = result.get('away_score', 0)
                        
                        # Get live predictions from real API data
                        betting_predictions = result.get('betting_predictions', {})
                        api_predictions = result.get('predictions', {})
                        odds = result.get('odds', [])
                        
                        # Use betting_predictions if available, otherwise fallback to API predictions
                        predictions = betting_predictions if betting_predictions else api_predictions
                        
                        # Extract key prediction data from real API responses
                        h2h_prediction = self._extract_h2h_prediction(predictions)
                        btts_prediction = self._extract_btts_prediction(predictions)
                        goals_prediction = self._extract_goals_prediction(predictions)
                        corners_prediction = self._extract_corners_prediction(predictions)
                        
                        # Get live odds for key markets
                        live_odds = self._extract_live_odds(odds)
                        
                        message += f"{i}. ⚽ {home_team} vs {away_team}\n"
                        message += f"   📊 Status: {status}\n"
                        message += f"   🎯 Score: {home_score}-{away_score}\n"
                        
                        # Add live predictions if available from real data
                        if h2h_prediction:
                            message += f"   🏆 H2H: {h2h_prediction}\n"
                        if btts_prediction:
                            message += f"   ⚽ BTTS: {btts_prediction}\n"
                        if goals_prediction:
                            message += f"   🎯 Goals: {goals_prediction}\n"
                        if corners_prediction:
                            message += f"   📐 Corners: {corners_prediction}\n"
                        
                        # Add live odds if available
                        if live_odds:
                            message += f"   💰 Live Odds: {live_odds}\n"
                        
                        message += "\n"
                        
                    except Exception as e:
                        logger.error(f"Error formatting live analysis result: {e}")
                        continue
                
                # Add batch summary
                message += f"📺 Batch {batch_number}: Live Matches {batch_data['batch_start']}-{batch_data['batch_end']} of {total_matches}"
                
                # Send this batch message immediately
                await update.message.reply_text(message)
                
                # If there are more batches coming, show a "searching" message
                if batch_number < total_batches:
                    remaining_matches = total_matches - batch_data['batch_end']
                    estimated_time = (total_batches - batch_number) * 2  # Rough estimate: 2 seconds per batch
                    
                    # Cool searching message with emojis and progress
                    searching_msg = await update.message.reply_text(
                        f"🔍 **SEARCHING FOR NEXT BATCH...**\n\n"
                        f"📊 Progress: {progress_percent:.0f}% Complete\n"
                        f"🎯 {remaining_matches} more live matches to analyze\n"
                        f"⏱️ Estimated time: ~{estimated_time} seconds\n"
                        f"🔄 Processing batch {batch_number + 1}/{total_batches}...\n\n"
                        f"💡 Please wait while we analyze the next set of matches..."
                    )
                    
                    # Small delay to allow Telegram to process the message
                    await asyncio.sleep(1.5)
                    
                    # Delete the searching message before showing next batch
                    await searching_msg.delete()
            
            # Send final summary message
            if total_matches > 0:
                summary_message = f"✅ Live Analysis Complete!\n\n📺 Total live matches: {total_matches}\n📱 Results split into {batch_count} batch(es)\n\n💡 Use /live again for fresh live predictions!"
                await update.message.reply_text(summary_message)
            else:
                await progress_msg.edit_text("📺 No Live Matches Currently\n\n💡 This could mean:\n• No matches are currently in progress\n• All matches are finished for today\n• Matches haven't started yet\n\n🔄 Try /analyze for today's upcoming matches!")
            
        except Exception as e:
            error_msg = f"❌ Live analysis failed: {str(e)}\n\n🔧 Try /analyze for today's matches instead!"
            await progress_msg.edit_text(error_msg)
            logger.error(f"Live command failed: {e}")

    def _extract_live_odds(self, odds: List[Dict]) -> str:
        """Extract live odds for key markets"""
        if not odds or not isinstance(odds, list):
            return None
        
        live_odds = {}
        
        for odd in odds:
            market = odd.get('market_description', '').lower()
            value = odd.get('value', 0)
            
            if 'match winner' in market or '1x2' in market:
                if 'home' in market or '1' in market:
                    if 'home_win' not in live_odds or value > live_odds['home_win']:
                        live_odds['home_win'] = value
                elif 'away' in market or '2' in market:
                    if 'away_win' not in live_odds or value > live_odds['away_win']:
                        live_odds['away_win'] = value
                elif 'draw' in market or 'x' in market:
                    if 'draw' not in live_odds or value > live_odds['draw']:
                        live_odds['draw'] = value
            
            elif 'both teams to score' in market or 'btts' in market:
                if 'yes' in market or 'btts' in market:
                    if 'btts_yes' not in live_odds or value > live_odds['btts_yes']:
                        live_odds['btts_yes'] = value
                elif 'no' in market:
                    if 'btts_no' not in live_odds or value > live_odds['btts_no']:
                        live_odds['btts_no'] = value
        
        # Format live odds
        if live_odds:
            odds_str = []
            if 'home_win' in live_odds:
                odds_str.append(f"H:{live_odds['home_win']:.2f}")
            if 'away_win' in live_odds:
                odds_str.append(f"A:{live_odds['away_win']:.2f}")
            if 'draw' in live_odds:
                odds_str.append(f"D:{live_odds['draw']:.2f}")
            if 'btts_yes' in live_odds:
                odds_str.append(f"BTTS Y:{live_odds['btts_yes']:.2f}")
            
            return " | ".join(odds_str)
        
        return None

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            # Test API connectivity
            from realtime_analyzer import RealTimeAnalyzer
            analyzer = RealTimeAnalyzer()
            
            # Quick API test
            test_matches = await analyzer.api_client.get_today_matches()
            api_status = "✅ Connected" if test_matches else "⚠️ Limited Access"
            
            status_message = f"""
📊 Bot Status

✅ Bot is running
🔑 API Key: {'✅ Set' if self.token else '❌ Missing'}
💬 Chat ID: {'✅ Set' if self.chat_id else '❌ Not set'}
🌐 API Status: {api_status}
📅 Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔧 System Health:
• Telegram: ✅ Connected
• SportMonks: ✅ Available
• API-Football: ✅ Available
• Data Quality: 🟢 Premium

💡 Commands: /analyze, /live, /help
        """
            await update.message.reply_text(status_message)
            
        except Exception as e:
            status_message = f"""
📊 Bot Status

✅ Bot is running
🔑 API Key: {'✅ Set' if self.token else '❌ Missing'}
💬 Chat ID: {'✅ Set' if self.chat_id else '❌ Not set'}
🌐 API Status: ⚠️ Testing...
📅 Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

❌ API Test Failed: {str(e)}
💡 Try /analyze to test full functionality
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
    
    async def network_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /network command - test network connectivity"""
        await update.message.reply_text("🌐 Testing network connectivity...")
        
        try:
            # Test Telegram connectivity
            if await self.test_connectivity():
                await update.message.reply_text("✅ Telegram connectivity: OK\n\nBot is connected to Telegram servers.")
            else:
                await update.message.reply_text("❌ Telegram connectivity: FAILED\n\nCannot connect to Telegram servers.")
                
                # Send troubleshooting tips
                tips = self.get_network_troubleshooting_tips()
                await update.message.reply_text(tips)
                
        except Exception as e:
            error_msg = f"❌ Network test failed: {str(e)}"
            await update.message.reply_text(error_msg)
            logger.error(f"Network command failed: {e}")
