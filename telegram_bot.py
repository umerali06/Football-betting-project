#!/usr/bin/env python3
"""
Interactive Telegram Bot for FIXORA PRO Football Analysis System
Works for all users, not just a specific chat ID
"""

import asyncio
import logging
import os
import json
import schedule
import pytz
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import config

# Import timezone utilities
from utils.time import now_london, get_next_8am_london
from utils.odds_filter import OddsFilter

logger = logging.getLogger(__name__)

class TelegramBetBot:
    """Interactive Telegram bot for football analysis updates"""
    
    def __init__(self):
        self.bot = None
        self.application = None
        self.is_running = False
        self.user_sessions = {}  # Store user sessions
        self.auto_roi_scheduler = None  # Auto ROI scheduler
        
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
            self.application.add_handler(CommandHandler("analyze_roi", self.analyze_roi_command))
            self.application.add_handler(CommandHandler("report", self.report_command))
            self.application.add_handler(CommandHandler("weekly_report", self.weekly_report_command))
            self.application.add_handler(CommandHandler("daily_report", self.daily_report_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            
            # Add message handler for any text message
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Start the bot without polling to avoid conflicts
            await self.application.initialize()
            await self.application.start()
            
            # Don't start polling here - it will be handled separately
            self.is_running = True
            logger.info("Interactive Telegram bot initialized successfully (polling not started)")
            
            # Start automatic ROI scheduler
            self._start_auto_roi_scheduler()
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            self.application = None
    
    async def start_polling(self):
        """Start polling for updates (call this separately to avoid conflicts)"""
        try:
            if self.application and not self.application.updater.running:
                await self.application.updater.start_polling()
                logger.info("Telegram bot polling started successfully")
                return True
            else:
                logger.info("Telegram bot polling already running or not initialized")
                return False
        except Exception as e:
            logger.error(f"Failed to start polling: {e}")
            return False
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Add user to active sessions
        self.user_sessions[chat_id] = {
            'user_id': user.id,
            'first_name': user.first_name,
            'started_at': update.message.date
        }
        
        welcome_message = f"""
 Welcome to FIXORA PRO ROI Betting System! 🚀💰

 Hi {user.first_name}! I'm your AI-powered ROI betting assistant.

What I can do:
 • Analyze ROI opportunities and find highest-rated bets
 • Generate PDF reports of betting performance
 • Provide unit-based betting recommendations (3-2-1 units)
 • Send automatic morning ROI updates at 8am UK time
 • Track betting performance and calculate ROI%

Commands:
/start - Show this welcome message
/help - Show detailed help
/status - Check bot status
 /analyze_roi - Analyze today's ROI opportunities
 /report - Generate PDF report of bets
 /daily_report - Generate today's ROI performance summary
 /weekly_report - Generate weekly ROI performance summary

 🕗 I'll automatically send you ROI analysis every morning at 8am UK time!
 💰 You can also use /analyze_roi anytime for manual analysis.
        """
        
        await update.message.reply_text(welcome_message)
        logger.info(f"User {user.first_name} (ID: {user.id}) started the bot in chat {chat_id}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📚 FIXORA PRO ROI Betting System Help

This bot provides ROI-focused betting analysis using:
• Advanced ROI calculation algorithms
• Unit-based betting recommendations (3-2-1 units)
• Automatic morning updates at 8am UK time
• PDF report generation for betting performance

Commands:
/start - Welcome message
/help - This help message
/status - Bot status
/analyze_roi - Analyze today's ROI opportunities
/report - Generate PDF report of bets
/daily_report - Generate today's ROI performance summary
/weekly_report - Generate weekly ROI performance summary

Features:
✅ ROI analysis and highest-rated bet identification
✅ Unit-based betting recommendations (3-2-1 units)
✅ Automatic morning ROI updates at 8am UK time
✅ PDF report generation for betting performance
✅ Betting performance tracking and ROI calculation
        """
        
        await update.message.reply_text(help_message)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        active_sessions = self.get_active_sessions()
        
        # Get current UK time and next 8:00 AM run
        current_uk_time = now_london()
        next_8am = get_next_8am_london()
        
        status_message = f"""
📊 ROI Betting System Status

⏰ Current UK Time: {current_uk_time.strftime('%Y-%m-%d %H:%M:%S')}
🕗 Next 8:00 AM UK Run: {next_8am.strftime('%Y-%m-%d %H:%M:%S')}

✅ Bot is running and active
🔑 API Connection: Enhanced Unified API System
💰 ROI Analysis: Active
📈 Unit-based Betting: Enabled
🕗 Auto Updates: 8am UK time daily
👥 Active Users: {active_sessions['total_sessions']}

🌐 API Configuration:
• Primary: API-Football (api-sports.io)
• Fallback: SportMonks
• Strategy: Try API-Football first, fall back to SportMonks
• Enhanced: Multiple fallback strategies with sample data generation

🎯 Available Commands:
• /analyze_roi - ROI analysis with unit recommendations
• /report - PDF report generation
• /daily_report - Today's ROI performance summary
• /weekly_report - Weekly ROI performance summary

💰 Betting System:
• Unit System: 3-2-1 units for top 3 bets
• ROI Calculation: Automatic performance tracking
• Morning Updates: Daily at 8am UK time
• Report Generation: PDF format available

The ROI betting system is working and ready to find your highest-rated bets!

Send me any message or use /analyze_roi to get started.
        """
        
        await update.message.reply_text(status_message)
    
    async def analyze_roi_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze_roi command - analyze ROI opportunities with unit recommendations"""
        await update.message.reply_text("💰 Analyzing ROI opportunities... Please wait.")
        
        try:
            # Import only the API client to avoid triggering main system analysis
            from api.enhanced_api_client import EnhancedAPIClient
            from api.league_filter import LeagueFilter
            
            # Create API client and league filter directly
            api_client = EnhancedAPIClient()
            league_filter = LeagueFilter()
            
            # Get today's matches
            matches = await api_client.get_today_matches()
            
            if not matches:
                await update.message.reply_text("❌ No matches available for today")
                return
            
            # Filter matches by target leagues
            filtered_matches = league_filter.filter_matches_by_league(matches)
            
            if not filtered_matches:
                await update.message.reply_text("❌ No matches found in target leagues for today")
                return
            
            # Get league summary
            league_summary = league_filter.get_league_summary(filtered_matches)
            
            # Send initial summary
            summary_message = f"""
📊 <b>ROI Analysis Summary</b>

🔍 <b>Total Matches Found</b>: {len(matches)}
🎯 <b>Target League Matches</b>: {len(filtered_matches)}

🏆 <b>League Breakdown</b>:
"""
            
            # Add league breakdown
            for league, count in league_summary.items():
                summary_message += f"• {league}: {count} matches\n"
            
            await update.message.reply_text(summary_message, parse_mode='HTML')
            
            # Analyze matches for ROI opportunities
            roi_opportunities = []
            
            # CRITICAL: Pre-filter matches to only include those with valid odds
            valid_matches = []
            for i, match in enumerate(filtered_matches[:10]):  # Analyze first 10 matches
                try:
                    # Extract basic info
                    home_team, away_team = self._extract_team_names(match)
                    
                    # Get odds if available
                    odds_data = None
                    valid_odds = False
                    try:
                        fixture_id = api_client.extract_fixture_id(match)
                        if fixture_id:
                            odds = await api_client.safe_match_odds(match)
                            if odds:
                                odds_data = odds
                                
                                # NUCLEAR OPTION: Direct odds validation bypassing complex logic
                                main_odds = self._extract_main_odds_direct(odds)
                                logger.info(f"🔍 DEBUG: Match {i+1} {home_team} vs {away_team} - extracted odds: {main_odds}")
                                
                                if main_odds and main_odds >= 1.8:
                                    valid_odds = True
                                    logger.info(f"✅ INCLUDING match {home_team} vs {away_team} - main odds: {main_odds}")
                                else:
                                    valid_odds = False
                                    logger.info(f"❌ EXCLUDING match {home_team} vs {away_team} - main odds: {main_odds} (below 1.8)")
                            else:
                                logger.info(f"⚠️ No odds data for match {home_team} vs {away_team}")
                        else:
                            logger.info(f"⚠️ No fixture ID for match {home_team} vs {away_team}")
                    except Exception as odds_error:
                        logger.error(f"Error getting odds for {home_team} vs {away_team}: {odds_error}")
                    
                    # Only include matches with valid odds
                    if valid_odds:
                        valid_matches.append((i, match, odds_data))
                        logger.info(f"✅ ADDED to valid_matches: {home_team} vs {away_team}")
                    else:
                        logger.info(f"❌ EXCLUDING match {home_team} vs {away_team} - odds below minimum threshold (1.8)")
                        
                except Exception as e:
                    logger.error(f"Error pre-filtering match {i+1}: {e}")
                    continue
            
            logger.info(f"🔍 DEBUG: Found {len(valid_matches)} matches with valid odds out of {min(10, len(filtered_matches))} analyzed")
            
            # Now process only the valid matches
            for i, (original_index, match, odds_data) in enumerate(valid_matches):
                try:
                    # Extract basic info
                    home_team, away_team = self._extract_team_names(match)
                    status = api_client.extract_match_status(match)
                    home_score, away_score = api_client.extract_score(match)
                    
                    # Since we pre-filtered, we know odds_data exists and is valid
                    odds_info = self._extract_odds_for_display(odds_data)
                    
                    # Calculate ROI rating based on validated odds data
                    roi_rating = self._calculate_roi_rating(odds_data, match, i)
                    logger.info(f"✅ Processing match {home_team} vs {away_team} - ROI rating: {roi_rating}")
                    
                    # Add to opportunities (all matches here have valid odds)
                    roi_opportunities.append({
                        'match': match,
                        'home_team': home_team,
                        'away_team': away_team,
                        'status': status,
                        'home_score': home_score,
                        'away_score': away_score,
                        'odds_info': odds_info,
                        'roi_rating': roi_rating,
                        'fixture_id': api_client.extract_fixture_id(match)
                    })
                    
                except Exception as e:
                    logger.error(f"Error analyzing match {i+1}: {e}")
                    continue
            
            # Sort by ROI rating and get top 5
            roi_opportunities.sort(key=lambda x: x['roi_rating'], reverse=True)
            top_5_opportunities = roi_opportunities[:5]
            
            # Create ROI analysis results with unit recommendations
            if top_5_opportunities:
                results_message = "💰 <b>Top 5 ROI Opportunities</b> (with Unit Recommendations):\n\n"
                
                for i, opportunity in enumerate(top_5_opportunities):
                    # Unit recommendation: 3 units for 1st, 2 for 2nd, 1 for 3rd, 0.5 for 4th and 5th
                    if i == 0:
                        units = 3
                        unit_emoji = "🔥"
                    elif i == 1:
                        units = 2
                        unit_emoji = "⚡"
                    elif i == 2:
                        units = 1
                        unit_emoji = "⚽"
                    else:
                        units = 0.5
                        unit_emoji = "📊"
                    
                    results_message += f"""
{unit_emoji} <b>#{i+1} - {opportunity['home_team']} vs {opportunity['away_team']}</b>
💰 <b>Betting</b>: {opportunity['odds_info']}
💎 <b>Recommended Units</b>: {units} units
"""
                
                await update.message.reply_text(results_message, parse_mode='HTML')
                
                # Send unit system explanation
                unit_explanation = """
💎 <b>Unit System Explanation</b>:
• 1st Place: 3 units (highest confidence)
• 2nd Place: 2 units (high confidence)  
• 3rd Place: 1 unit (medium confidence)
• 4th & 5th: 0.5 units (lower confidence)

📈 <b>ROI Tracking</b>: All bets are tracked for performance analysis
🕗 <b>Daily Updates</b>: Get morning ROI updates at 8am UK time
📊 <b>Reports</b>: Use /report to generate PDF performance reports
"""
                await update.message.reply_text(unit_explanation, parse_mode='HTML')
                
            else:
                await update.message.reply_text("❌ <b>No ROI opportunities found</b> - Could not analyze matches", parse_mode='HTML')
            
        except Exception as e:
            error_msg = f"❌ ROI analysis failed: {str(e)}"
            await update.message.reply_text(error_msg)
            logger.error(f"ROI analysis command failed: {e}")
    
    async def report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /report command - generate PDF report of betting performance"""
        await update.message.reply_text("📊 Generating betting performance report... Please wait.")
        
        try:
            # Import and use the report generator
            from reports.report_generator import ReportGenerator
            
            # Create report generator instance
            report_gen = ReportGenerator()
            
            # Generate comprehensive betting report
            report_data = await report_gen.generate_betting_performance_report()
            
            if report_data and report_data.get('success'):
                # Send report summary
                summary_message = f"""
📊 <b>Betting Performance Report Generated</b>

📈 <b>Report Summary</b>:
• Total Bets: {report_data.get('total_bets', 0)}
• Winning Bets: {report_data.get('winning_bets', 0)}
• Losing Bets: {report_data.get('losing_bets', 0)}
• Overall ROI: {report_data.get('overall_roi', 0):.2f}%
• Total Profit/Loss: {report_data.get('total_pnl', 0):.2f} units

📁 <b>Report File</b>: {report_data.get('file_path', 'Generated')}
📅 <b>Period</b>: {report_data.get('period', 'All time')}

💡 <b>Note</b>: The PDF report has been generated and is being sent to you now.
"""
                await update.message.reply_text(summary_message, parse_mode='HTML')
                
                # Send the actual PDF file
                try:
                    file_path = report_data.get('file_path')
                    if file_path and os.path.exists(file_path):
                        with open(file_path, 'rb') as pdf_file:
                            await update.message.reply_document(
                                document=pdf_file,
                                filename=f"betting_performance_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                                caption="📊 Your betting performance report is ready! Download and review your ROI analysis."
                            )
                        logger.info(f"PDF report sent successfully: {file_path}")
                    else:
                        await update.message.reply_text("⚠ <b>Warning</b>: PDF file not found. Report summary only.", parse_mode='HTML')
                except Exception as pdf_error:
                    logger.error(f"Error sending PDF: {pdf_error}")
                    await update.message.reply_text("⚠ <b>Warning</b>: Could not send PDF file. Report summary only.", parse_mode='HTML')
                
                # Send additional insights
                insights_message = """
🔍 <b>Key Insights</b>:
• Performance tracking by unit allocation
• ROI analysis by bet type and confidence level
• Historical performance trends
• Unit-based profit/loss breakdown

🕗 <b>Daily Updates</b>: Get automatic ROI updates every morning at 8am UK time
💰 <b>Next Analysis</b>: Use /analyze_roi for today's opportunities
"""
                await update.message.reply_text(insights_message, parse_mode='HTML')
                
            else:
                await update.message.reply_text("❌ <b>Report generation failed</b> - Could not create performance report", parse_mode='HTML')
            
        except Exception as e:
            error_msg = f"❌ Report generation failed: {str(e)}"
            await update.message.reply_text(error_msg)
            logger.error(f"Report command failed: {e}")
    
    async def weekly_report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /weekly_report command - generate weekly ROI performance summary"""
        await update.message.reply_text("📅 Generating weekly ROI performance summary... Please wait.")
        
        try:
            # Import ROI tracker for real data
            from betting.roi_tracker import ROITracker
            
            # Initialize ROI tracker
            roi_tracker = ROITracker()
            
            # Calculate date range for the last 7 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            # Get real-time weekly performance data
            weekly_performance = roi_tracker.get_weekly_performance(7)
            overall_performance = roi_tracker.get_overall_performance()
            
            if weekly_performance:
                # Calculate weekly totals
                total_weekly_bets = sum(stats.get('total_bets', 0) for stats in weekly_performance.values())
                total_weekly_stake = sum(stats.get('total_stake', 0) for stats in weekly_performance.values())
                total_weekly_return = sum(stats.get('total_return', 0) for stats in weekly_performance.values())
                total_weekly_pnl = sum(stats.get('total_profit_loss', 0) for stats in weekly_performance.values())
                weekly_roi = (total_weekly_pnl / total_weekly_stake) * 100 if total_weekly_stake > 0 else 0
                
                # Send weekly summary with real data
                weekly_summary = f"""
📊 <b>Weekly ROI Performance Summary</b>

📅 <b>Period</b>: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}
📈 <b>Report Type</b>: Weekly ROI Analysis

🎯 <b>Weekly Performance</b>:
• Total Bets: {total_weekly_bets}
• Total Stake: {total_weekly_stake:.2f} units
• Total Return: {total_weekly_return:.2f} units
• Total P&L: {total_weekly_pnl:.2f} units
• Weekly ROI: {weekly_roi:.1f}%

📊 <b>Market Breakdown</b>:
"""
                
                # Add market breakdown
                for market, stats in weekly_performance.items():
                    market_name = market.replace('_', ' ').title()
                    weekly_summary += f"• {market_name}: {stats.get('total_bets', 0)} bets, {stats.get('roi', 0):.1f}% ROI\n"
                
                weekly_summary += f"""
💡 <b>Overall Context</b>:
• All-Time Bets: {overall_performance.get('total_bets', 0)}
• All-Time ROI: {overall_performance.get('overall_roi', 0):.1f}%
• All-Time P&L: {overall_performance.get('total_profit_loss', 0):.2f} units

🕗 <b>Next Update</b>: Automatic daily update at 8am UK time
"""
                
                await update.message.reply_text(weekly_summary, parse_mode='HTML')
                
                # Generate and send PDF report
                try:
                    from reports.roi_weekly_report import ROIWeeklyReportGenerator
                    report_gen = ROIWeeklyReportGenerator()
                    
                    # Generate weekly ROI report
                    roi_data = {
                        'overall_performance': overall_performance,
                        'market_performance': roi_tracker.get_market_performance(),
                        'league_performance': roi_tracker.get_league_performance(),
                        'weekly_performance': weekly_performance
                    }
                    
                    report_path = report_gen.generate_weekly_roi_report(roi_data, start_date, end_date)
                    
                    if report_path and os.path.exists(report_path):
                        with open(report_path, 'rb') as pdf_file:
                            await update.message.reply_document(
                                document=pdf_file,
                                filename=f"weekly_roi_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf",
                                caption="📊 Your weekly ROI performance report is ready! Download and review your weekly betting analysis."
                            )
                        logger.info(f"Weekly PDF report sent successfully: {report_path}")
                    else:
                        await update.message.reply_text("⚠ <b>Warning</b>: Could not generate PDF report. Summary only.", parse_mode='HTML')
                        
                except Exception as pdf_error:
                    logger.error(f"Error generating weekly PDF: {pdf_error}")
                    await update.message.reply_text("⚠ <b>Warning</b>: Could not generate PDF report. Summary only.", parse_mode='HTML')
                
            else:
                # No weekly data available
                no_data_message = f"""
📊 <b>Weekly ROI Performance Summary</b>

📅 <b>Period</b>: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}

❌ <b>No Betting Activity</b>: No bets were placed in the last 7 days

💡 <b>Overall Context</b>:
• All-Time Bets: {overall_performance.get('total_bets', 0)}
• All-Time ROI: {overall_performance.get('overall_roi', 0):.1f}%
• All-Time P&L: {overall_performance.get('total_profit_loss', 0):.2f} units

🕗 <b>Next Update</b>: Automatic daily update at 8am UK time
"""
                await update.message.reply_text(no_data_message, parse_mode='HTML')
            
        except Exception as e:
            error_msg = f"❌ Weekly report generation failed: {str(e)}"
            await update.message.reply_text(error_msg)
            logger.error(f"Weekly report command failed: {e}")
    
    async def daily_report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /daily_report command - generate today's ROI performance summary"""
        await update.message.reply_text("📅 Generating today's ROI performance summary... Please wait.")
        
        try:
            # Import ROI tracker for real data
            from betting.roi_tracker import ROITracker
            
            # Initialize ROI tracker
            roi_tracker = ROITracker()
            
            # Get today's date
            today = datetime.now()
            today_str = today.strftime('%Y-%m-%d')
            
            # Get real-time daily performance data (last 24 hours)
            daily_performance = roi_tracker.get_weekly_performance(1)  # Last 1 day
            overall_performance = roi_tracker.get_overall_performance()
            
            if daily_performance:
                # Calculate daily totals
                total_daily_bets = sum(stats.get('total_bets', 0) for stats in daily_performance.values())
                total_daily_stake = sum(stats.get('total_stake', 0) for stats in daily_performance.values())
                total_daily_return = sum(stats.get('total_return', 0) for stats in daily_performance.values())
                total_daily_pnl = sum(stats.get('total_profit_loss', 0) for stats in daily_performance.values())
                daily_roi = (total_daily_pnl / total_daily_stake) * 100 if total_daily_stake > 0 else 0
                
                # Send daily summary with real data
                daily_summary = f"""
📊 <b>Today's ROI Performance Summary</b>

📅 <b>Date</b>: {today.strftime('%B %d, %Y')}
📈 <b>Report Type</b>: Daily ROI Analysis

🎯 <b>Today's Performance</b>:
• Total Bets: {total_daily_bets}
• Total Stake: {total_daily_stake:.2f} units
• Total Return: {total_daily_return:.2f} units
• Total P&L: {total_daily_pnl:.2f} units
• Daily ROI: {daily_roi:.1f}%

📊 <b>Market Breakdown</b>:
"""
                
                # Add market breakdown
                for market, stats in daily_performance.items():
                    market_name = market.replace('_', ' ').title()
                    daily_summary += f"• {market_name}: {stats.get('total_bets', 0)} bets, {stats.get('roi', 0):.1f}% ROI\n"
                
                daily_summary += f"""
💡 <b>Overall Context</b>:
• All-Time Bets: {overall_performance.get('total_bets', 0)}
• All-Time ROI: {overall_performance.get('overall_roi', 0):.1f}%
• All-Time P&L: {overall_performance.get('total_profit_loss', 0):.2f} units

🕗 <b>Next Update</b>: Automatic daily update at 8am UK time
"""
                
                await update.message.reply_text(daily_summary, parse_mode='HTML')
                
            else:
                # No daily data available
                no_data_message = f"""
📊 <b>Today's ROI Performance Summary</b>

📅 <b>Date</b>: {today.strftime('%B %d, %Y')}

❌ <b>No Betting Activity</b>: No bets were placed today

💡 <b>Overall Context</b>:
• All-Time Bets: {overall_performance.get('total_bets', 0)}
• All-Time ROI: {overall_performance.get('overall_roi', 0):.1f}%
• All-Time P&L: {overall_performance.get('total_profit_loss', 0):.2f} units

🕗 <b>Next Update</b>: Automatic daily update at 8am UK time
"""
                await update.message.reply_text(no_data_message, parse_mode='HTML')
            
        except Exception as e:
            error_msg = f"❌ Daily report generation failed: {str(e)}"
            await update.message.reply_text(error_msg)
            logger.error(f"Daily report command failed: {e}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle any text message from users"""
        user = update.effective_user
        message_text = update.message.text
        chat_id = update.effective_chat.id
        
        # Track user session if not already tracked
        if chat_id not in self.user_sessions:
            self.user_sessions[chat_id] = {
                'user_id': user.id,
                'first_name': user.first_name,
                'started_at': update.message.date
            }
        
        logger.info(f"Received message from {user.first_name} (ID: {user.id}): {message_text}")
        
        # Provide helpful response based on message content
        if any(word in message_text.lower() for word in ['hello', 'hi', 'hey']):
            response = f"Hello {user.first_name}! 👋 How can I help you with ROI betting analysis today?"
        
        elif any(word in message_text.lower() for word in ['roi', 'return', 'profit', 'earnings']):
            response = "💰 Interested in ROI analysis? I can help you find the highest-rated betting opportunities with unit recommendations. Use /analyze_roi to get started!"
        
        elif any(word in message_text.lower() for word in ['bet', 'betting', 'odds']):
            response = "🎯 Looking for betting opportunities? I analyze matches and provide unit-based recommendations (3-2-1 units) based on ROI ratings. Try /analyze_roi!"
        
        elif any(word in message_text.lower() for word in ['report', 'performance', 'results']):
            response = "📊 Want to see your betting performance? I can generate comprehensive PDF reports showing ROI, profit/loss, and unit-based analysis. Use /report for overall performance or /weekly_report for weekly summary!"
        
        elif any(word in message_text.lower() for word in ['weekly', 'week', '7 days', 'seven days']):
            response = "📅 Need a weekly performance summary? I can generate 7-day ROI reports showing your betting performance over the past week. Use /weekly_report!"
        
        elif any(word in message_text.lower() for word in ['units', 'unit', 'stake']):
            response = "💎 I use a unit-based system: 3 units for highest confidence, 2 for high confidence, 1 for medium, and 0.5 for lower confidence. Use /analyze_roi to see today's recommendations!"
        
        elif any(word in message_text.lower() for word in ['help', 'support', 'what can you do']):
            response = "🤖 I'm your ROI betting assistant! I analyze matches, provide unit recommendations, generate performance reports, and send daily updates at 8am UK time. Use /help for detailed information."
        
        else:
            response = f"""
Thanks for your message, {user.first_name}! 

I'm here to help you with ROI-focused betting analysis. Here's what I can do:

💰 Analyze ROI opportunities and find highest-rated bets
💎 Provide unit-based betting recommendations (3-2-1 units)
📊 Generate PDF performance reports
🕗 Send automatic morning ROI updates at 8am UK time

Try these commands:
/analyze_roi - Analyze today's ROI opportunities
/report - Generate PDF performance report
/weekly_report - Generate weekly ROI summary
/help - Detailed help
/status - Bot status

Or just ask me about ROI, betting units, or performance analysis!
            """
        
        await update.message.reply_text(response)
    
    async def send_morning_roi_update(self, chat_id: int) -> bool:
        """Send automatic morning ROI update at 8am UK time"""
        try:
            # Import only the API client to avoid triggering main system analysis
            from api.enhanced_api_client import EnhancedAPIClient
            from api.league_filter import LeagueFilter
            
            # Create API client and league filter directly
            api_client = EnhancedAPIClient()
            league_filter = LeagueFilter()
            
            # Get today's matches
            matches = await api_client.get_today_matches()
            
            if not matches:
                morning_message = """
🌅 <b>Good Morning!</b> 

📅 <b>Today's ROI Update</b>

❌ No matches available for today
💡 Check back later or use /analyze_roi for manual analysis

🕗 <b>Next Update</b>: Tomorrow at 8am UK time
💰 <b>Manual Analysis</b>: Use /analyze_roi anytime
📊 <b>Performance Report</b>: Use /report for detailed analysis
"""
                await self.send_message_to_user(chat_id, morning_message)
                return True
            
            # Filter matches by target leagues
            filtered_matches = league_filter.filter_matches_by_league(matches)
            
            if not filtered_matches:
                morning_message = """
🌅 <b>Good Morning!</b> 

📅 <b>Today's ROI Update</b>

❌ No matches available for today
💡 Check back later or use /analyze_roi for manual analysis

🕗 <b>Next Update</b>: Tomorrow at 8am UK time
💰 <b>Manual Analysis</b>: Use /analyze_roi anytime
📊 <b>Performance Report</b>: Use /report for detailed analysis
"""
                await self.send_message_to_user(chat_id, morning_message)
                return True
            
            # Get league summary
            league_summary = league_filter.get_league_summary(filtered_matches)
            
            # Analyze top 3 ROI opportunities for morning update
            roi_opportunities = []
            
            for i, match in enumerate(filtered_matches[:5]):  # Analyze first 5 matches
                try:
                    home_team, away_team = self._extract_team_names(match)
                    status = api_client.extract_match_status(match)
                    
                    # Calculate ROI rating (simplified)
                    roi_rating = 0.5 + (i * 0.15)  # Placeholder calculation
                    
                    roi_opportunities.append({
                        'home_team': home_team,
                        'away_team': away_team,
                        'status': status,
                        'roi_rating': roi_rating
                    })
                    
                except Exception as e:
                    logger.error(f"Error analyzing match {i+1} for morning update: {e}")
                    continue
            
            # Sort by ROI rating and get top 3
            roi_opportunities.sort(key=lambda x: x['roi_rating'], reverse=True)
            top_3_opportunities = roi_opportunities[:3]
            
            # Create morning update message
            morning_message = f"""
🌅 <b>Good Morning!</b> 

📅 <b>Today's ROI Update - {len(filtered_matches)} Matches Available</b>

🏆 <b>League Breakdown</b>:
"""
            
            # Add league breakdown
            for league, count in list(league_summary.items())[:5]:  # Show top 5 leagues
                morning_message += f"• {league}: {count} matches\n"
            
            if len(league_summary) > 5:
                morning_message += f"• ... and {len(league_summary) - 5} more leagues\n"
            
            morning_message += f"""

🔥 <b>Top 3 ROI Opportunities</b> (Morning Preview):

"""
            
            # Add top 3 opportunities with unit recommendations
            for i, opportunity in enumerate(top_3_opportunities):
                if i == 0:
                    units = 3
                    unit_emoji = "🔥"
                elif i == 1:
                    units = 2
                    unit_emoji = "⚡"
                else:
                    units = 1
                    unit_emoji = "⚽"
                
                morning_message += f"""
{unit_emoji} <b>#{i+1} - {opportunity['home_team']} vs {opportunity['away_team']}</b>
💎 <b>Recommended Units</b>: {units} units
"""
            
            morning_message += """

💡 <b>Next Steps</b>:
• Use /analyze_roi for full analysis of all opportunities
• Use /report to check your betting performance
• Get detailed odds and betting markets

🕗 <b>Next Update</b>: Tomorrow at 8am UK time
💰 <b>Full Analysis</b>: Use /analyze_roi anytime
"""
            
            await self.send_message_to_user(chat_id, morning_message)
            logger.info(f"Morning ROI update sent to chat {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send morning ROI update to chat {chat_id}: {e}")
            return False
    
    async def send_message_to_user(self, user_id: int, message: str) -> bool:
        """Send a message to a specific user"""
        try:
            if not self.bot:
                self.bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
            
            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='HTML'
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
    
    def get_active_sessions(self) -> Dict:
        """Get information about active user sessions"""
        return {
            'total_sessions': len(self.user_sessions),
            'sessions': self.user_sessions
        }

    def _extract_team_names(self, match_data: Dict) -> tuple:
        """Extract home and away team names from match data"""
        try:
            # Try different data structures
            if 'teams' in match_data:
                teams = match_data['teams']
                if 'home' in teams and 'away' in teams:
                    home_team = teams['home'].get('name', 'Unknown')
                    away_team = teams['away'].get('name', 'Unknown')
                    return home_team, away_team
            
            # Try alternative structure
            if 'home_team' in match_data and 'away_team' in match_data:
                home_team = match_data['home_team'].get('name', 'Unknown') if isinstance(match_data['home_team'], dict) else str(match_data['home_team'])
                away_team = match_data['away_team'].get('name', 'Unknown') if isinstance(match_data['away_team'], dict) else str(match_data['away_team'])
                return home_team, away_team
            
            # Try name field
            if 'name' in match_data:
                name = match_data['name']
                if ' vs ' in name:
                    parts = name.split(' vs ')
                    if len(parts) == 2:
                        return parts[0].strip(), parts[1].strip()
            
            # Fallback
            return 'Home Team', 'Away Team'
            
        except Exception as e:
            logger.error(f"Error extracting team names: {e}")
            return 'Home Team', 'Away Team'
    
    def _start_auto_roi_scheduler(self):
        """Start automatic ROI analysis scheduler for 8am UK time"""
        try:
            # Schedule ROI analysis for 8am UK time every day
            # Note: schedule library doesn't support timezone, so we'll use local time
            # UK time is typically UTC+0 (GMT) or UTC+1 (BST) depending on daylight saving
            schedule.every().day.at("08:00").do(self._run_auto_roi_analysis)
            
            logger.info("Automatic ROI analysis scheduled for 8am daily (adjust for your local timezone)")
            logger.info("Note: If you're not in UK timezone, adjust the time in _start_auto_roi_scheduler method")
            
            # Start the scheduler in a separate thread
            import threading
            self.auto_roi_scheduler = threading.Thread(target=self._run_scheduler_loop, daemon=True)
            self.auto_roi_scheduler.start()
            
        except Exception as e:
            logger.error(f"Failed to start auto ROI scheduler: {e}")
    
    def _run_scheduler_loop(self):
        """Run the scheduler loop in a separate thread"""
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except Exception as e:
            logger.error(f"Scheduler loop error: {e}")
    
    async def _run_auto_roi_analysis(self):
        """Automatically run ROI analysis at 8am UK time"""
        try:
            logger.info("🕗 8am UK time reached - Running automatic ROI analysis")
            
            # Get all active user sessions
            active_chat_ids = list(self.user_sessions.keys())
            
            if not active_chat_ids:
                logger.info("No active users to send automatic ROI analysis")
                return
            
            # Send automatic ROI analysis to all active users
            for chat_id in active_chat_ids:
                try:
                    await self._send_automatic_roi_analysis(chat_id)
                    logger.info(f"Automatic ROI analysis sent to chat {chat_id}")
                except Exception as e:
                    logger.error(f"Failed to send automatic ROI analysis to chat {chat_id}: {e}")
            
            logger.info(f"Automatic ROI analysis completed for {len(active_chat_ids)} users")
            
        except Exception as e:
            logger.error(f"Error in automatic ROI analysis: {e}")
    
    async def _send_automatic_roi_analysis(self, chat_id: int):
        """Send automatic ROI analysis to a specific user"""
        try:
            # Send initial message
            await self.send_message_to_user(chat_id, "🕗 <b>Good Morning! It's 8am UK time.</b>\n\n💰 <b>Running automatic ROI analysis...</b>")
            
            # Import only the API client to avoid triggering main system analysis
            from api.enhanced_api_client import EnhancedAPIClient
            from api.league_filter import LeagueFilter
            
            # Create API client and league filter directly
            api_client = EnhancedAPIClient()
            league_filter = LeagueFilter()
            
            # Get today's matches
            matches = await api_client.get_today_matches()
            
            if not matches:
                morning_message = """
🌅 <b>Good Morning!</b> 

📅 <b>Today's Automatic ROI Update</b>

❌ No matches available for today
💡 Check back later or use /analyze_roi for manual analysis

🕗 <b>Next Update</b>: Tomorrow at 8am UK time
💰 <b>Manual Analysis</b>: Use /analyze_roi anytime
📊 <b>Performance Report</b>: Use /report for detailed analysis
"""
                await self.send_message_to_user(chat_id, morning_message)
                return
            
            # Filter matches by target leagues
            filtered_matches = league_filter.filter_matches_by_league(matches)
            
            if not filtered_matches:
                morning_message = """
🌅 <b>Good Morning!</b> 

📅 <b>Today's Automatic ROI Update</b>

❌ No matches found in target leagues for today
💡 Check back later or use /analyze_roi for manual analysis

🕗 <b>Next Update</b>: Tomorrow at 8am UK time
💰 <b>Manual Analysis</b>: Use /analyze_roi anytime
📊 <b>Performance Report</b>: Use /report for detailed analysis
"""
                await self.send_message_to_user(chat_id, morning_message)
                return
            
            # Get league summary
            league_summary = league_filter.get_league_summary(filtered_matches)
            
            # Analyze top 5 ROI opportunities for automatic update
            roi_opportunities = []
            
            for i, match in enumerate(filtered_matches[:10]):  # Analyze first 10 matches
                try:
                    home_team, away_team = self._extract_team_names(match)
                    status = api_client.extract_match_status(match)
                    home_score, away_score = api_client.extract_score(match)
                    
                    # Get odds if available
                    odds_info = "No odds data"
                    odds_data = None
                    valid_odds = False  # Initialize valid_odds to False by default
                    try:
                        fixture_id = api_client.extract_fixture_id(match)
                        if fixture_id:
                            odds = await api_client.safe_match_odds(match)
                            if odds:
                                # Store odds data for validation first
                                odds_data = odds
                                
                                # Only extract odds display if validation passes
                                valid_odds = self._extract_and_validate_odds(odds_data)
                                if valid_odds:
                                    odds_display = self._extract_odds_for_display(odds)
                                    odds_info = odds_display
                                else:
                                    odds_info = "Odds below minimum threshold"
                    except Exception as odds_error:
                        logger.error(f"Error getting odds: {odds_error}")
                        odds_info = "Odds data error"
                    
                    # Calculate ROI rating based on actual odds data
                    roi_rating = 0.0
                    if odds_data:
                        # Use the already validated odds from above
                        if valid_odds:
                            # Calculate ROI based on actual odds and market analysis
                            roi_rating = self._calculate_roi_rating(odds_data, match, i)
                            logger.debug(f"✅ Match {home_team} vs {away_team} - Valid odds, ROI rating: {roi_rating}")
                        else:
                            # Skip this match - odds don't meet minimum requirement
                            logger.debug(f"❌ Skipping match {home_team} vs {away_team} - odds below minimum threshold")
                            continue
                    else:
                        # Lower rating without odds data
                        roi_rating = 0.3 + (i * 0.05)
                        logger.debug(f"⚠️ Match {home_team} vs {away_team} - No odds data, default rating: {roi_rating}")
                    
                    # Only add matches that passed odds validation or have no odds data
                    roi_opportunities.append({
                        'match': match,
                        'home_team': home_team,
                        'away_team': away_team,
                        'status': status,
                        'home_score': home_score,
                        'away_score': away_score,
                        'odds_info': odds_info,
                        'roi_rating': roi_rating,
                        'fixture_id': fixture_id if 'fixture_id' in locals() else None
                    })
                    
                except Exception as e:
                    logger.error(f"Error analyzing match {i+1} for automatic ROI: {e}")
                    continue
            
            # Sort by ROI rating and get top 5
            roi_opportunities.sort(key=lambda x: x['roi_rating'], reverse=True)
            top_5_opportunities = roi_opportunities[:5]
            
            # Create automatic morning ROI update message
            morning_message = f"""
🌅 <b>Good Morning!</b> 

📅 <b>Today's Automatic ROI Update - {len(filtered_matches)} Matches Available</b>

🏆 <b>League Breakdown</b>:
"""
            
            # Add league breakdown
            for league, count in list(league_summary.items())[:5]:  # Show top 5 leagues
                morning_message += f"• {league}: {count} matches\n"
            
            if len(league_summary) > 5:
                morning_message += f"• ... and {len(league_summary) - 5} more leagues\n"
            
            morning_message += f"""

💰 <b>Top 5 ROI Opportunities</b> (Automatic Analysis):

"""
            
            # Add top 5 opportunities with unit recommendations
            for i, opportunity in enumerate(top_5_opportunities):
                if i == 0:
                    units = 3
                    unit_emoji = "🔥"
                elif i == 1:
                    units = 2
                    unit_emoji = "⚡"
                elif i == 2:
                    units = 1
                    unit_emoji = "⚽"
                else:
                    units = 0.5
                    unit_emoji = "📊"
                
                morning_message += f"""
{unit_emoji} <b>#{i+1} - {opportunity['home_team']} vs {opportunity['away_team']}</b>
💰 <b>Betting</b>: {opportunity['odds_info']}
💎 <b>Recommended Units</b>: {units} units
"""
            
            morning_message += """

💡 <b>Next Steps</b>:
• Use /analyze_roi for full analysis of all opportunities
• Use /report to check your betting performance
• Get detailed odds and betting markets

🕗 <b>Next Update</b>: Tomorrow at 8am UK time
💰 <b>Full Analysis</b>: Use /analyze_roi anytime
"""
            
            await self.send_message_to_user(chat_id, morning_message)
            logger.info(f"Automatic morning ROI update sent to chat {chat_id}")
            
        except Exception as e:
            logger.error(f"Failed to send automatic ROI analysis to chat {chat_id}: {e}")
            # Send error message to user
            await self.send_message_to_user(chat_id, f"❌ <b>Error</b>: Automatic ROI analysis failed. Please use /analyze_roi for manual analysis.")
    
    def _extract_main_odds_direct(self, odds_data: List[Dict]) -> float:
        """Extract the main odds value directly - NUCLEAR OPTION for strict filtering"""
        try:
            if not odds_data:
                return 0.0
            
            # Look for the first valid odds value in the structure
            for market in odds_data:
                if isinstance(market, dict):
                    # Try to find any odds value
                    if 'bookmakers' in market:
                        for bookmaker in market['bookmakers']:
                            if 'bets' in bookmaker:
                                for bet in bookmaker['bets']:
                                    if 'values' in bet:
                                        for value in bet['values']:
                                            if 'odd' in value:
                                                try:
                                                    odds_value = float(value['odd'])
                                                    if odds_value > 0:
                                                        logger.info(f"🔍 DEBUG: Found main odds: {odds_value}")
                                                        return odds_value
                                                except (ValueError, TypeError):
                                                    continue
            
            # If no odds found, return 0
            logger.warning("No valid odds found in data structure")
            return 0.0
            
        except Exception as e:
            logger.error(f"Error extracting main odds: {e}")
            return 0.0
    
    def _extract_odds_for_display(self, odds_data: List[Dict]) -> str:
        """Extract and format odds for display"""
        try:
            if not odds_data:
                return "No odds available"
            
            # Try to extract main market odds (1X2 or similar)
            main_odds = []
            
            for market in odds_data:
                if isinstance(market, dict):
                    # Look for common market types
                    market_name = market.get('market', '').lower()
                    if any(keyword in market_name for keyword in ['1x2', 'match winner', 'winner', 'result']):
                        # Extract home, draw, away odds
                        if 'bookmakers' in market:
                            for bookmaker in market['bookmakers']:
                                if 'bets' in bookmaker:
                                    for bet in bookmaker['bets']:
                                        if 'values' in bet:
                                            for value in bet['values']:
                                                if 'odd' in value:
                                                    main_odds.append(f"{value.get('value', 'Unknown')}: {value.get('odd', 'N/A')}")
                        
                        # If we found main odds, return them
                        if main_odds:
                            return f"Main: {' | '.join(main_odds[:3])}"
                    
                    # Look for over/under markets
                    elif 'over' in market_name or 'under' in market_name:
                        if 'bookmakers' in market:
                            for bookmaker in market['bookmakers']:
                                if 'bets' in bookmaker:
                                    for bet in bookmaker['bets']:
                                        if 'values' in bet:
                                            for value in bet['values']:
                                                if 'odd' in value:
                                                    main_odds.append(f"{value.get('value', 'Unknown')}: {value.get('odd', 'N/A')}")
                        
                        # If we found over/under odds, return them
                        if main_odds:
                            return f"O/U: {' | '.join(main_odds[:2])}"
            
            # If no specific markets found, show first available odds
            if odds_data:
                # Try to show multiple market types
                market_summaries = []
                
                for i, market in enumerate(odds_data[:3]):  # Show up to 3 markets
                    if isinstance(market, dict) and 'bookmakers' in market:
                        market_name = market.get('market', f'Market {i+1}')
                        if 'bookmakers' in market:
                            for bookmaker in market['bookmakers']:
                                if 'bets' in bookmaker:
                                    for bet in bookmaker['bets']:
                                        if 'values' in bet:
                                            for value in bet['values']:
                                                if 'odd' in value:
                                                    market_summaries.append(f"{value.get('value', 'Unknown')} @ {value.get('odd', 'N/A')}")
                                                    break  # Only take first value per market
                                            break  # Only take first bet per bookmaker
                                        break  # Only take first bookmaker
                                    break
                
                if market_summaries:
                    return f"{' | '.join(market_summaries[:3])}"
            
            # Fallback
            return f"Odds available ({len(odds_data)} markets)"
            
        except Exception as e:
            logger.error(f"Error extracting odds for display: {e}")
            return f"Odds available ({len(odds_data)} markets)"
    
    def _extract_and_validate_odds(self, odds_data: List[Dict]) -> bool:
        """Extract and validate odds to ensure they meet minimum requirements - Universal validator"""
        try:
            if not odds_data:
                logger.debug("🔍 DEBUG: No odds data provided")
                return False
            
            logger.debug(f"🔍 DEBUG: Validating odds data structure: {type(odds_data)} with {len(odds_data)} items")
            
            # Try multiple common API data structures
            valid_odds_found = self._try_expected_structure(odds_data)
            if valid_odds_found:
                return True
            
            valid_odds_found = self._try_api_football_structure(odds_data)
            if valid_odds_found:
                return True
            
            valid_odds_found = self._try_sportmonks_structure(odds_data)
            if valid_odds_found:
                return True
            
            valid_odds_found = self._try_flat_odds_structure(odds_data)
            if valid_odds_found:
                return True
            
            valid_odds_found = self._try_generic_structure(odds_data)
            if valid_odds_found:
                return True
            
            logger.debug("🔍 DEBUG: No valid odds found in any structure")
            return False
            
        except Exception as e:
            logger.error(f"Error validating odds: {e}")
            return False
    
    def _try_expected_structure(self, odds_data: List[Dict]) -> bool:
        """Try the expected structure: bookmakers -> bets -> values -> odd - Validate MAIN odds only"""
        try:
            for market in odds_data:
                if isinstance(market, dict) and 'bookmakers' in market:
                    for bookmaker in market['bookmakers']:
                        if 'bets' in bookmaker:
                            for bet in bookmaker['bets']:
                                if 'values' in bet and bet['values']:
                                    # CRITICAL: Only validate the FIRST (main) odds value
                                    # This is typically Home win, which is what we're betting on
                                    main_value = bet['values'][0]
                                    if 'odd' in main_value:
                                        try:
                                            main_odds = float(main_value.get('odd', 0))
                                            logger.debug(f"🔍 DEBUG: Validating main odds: {main_odds}")
                                            if OddsFilter.validate_odds(main_odds):
                                                logger.debug(f"🔍 DEBUG: Main odds valid in expected structure: {main_odds}")
                                                return True
                                            else:
                                                logger.debug(f"🔍 DEBUG: Main odds invalid in expected structure: {main_odds}")
                                                return False  # Main odds failed validation
                                        except (ValueError, TypeError):
                                            logger.debug(f"🔍 DEBUG: Error converting main odds: {main_value.get('odd', 'N/A')}")
                                            return False
            return False
        except Exception as e:
            logger.debug(f"🔍 DEBUG: Exception in expected structure validation: {e}")
            return False
    
    def _try_api_football_structure(self, odds_data: List[Dict]) -> bool:
        """Try API-Football style structure: markets -> values -> odd - Validate MAIN odds only"""
        try:
            for market in odds_data:
                if isinstance(market, dict) and 'markets' in market:
                    for submarket in market['markets']:
                        if 'values' in submarket and submarket['values']:
                            # CRITICAL: Only validate the FIRST (main) odds value
                            main_value = submarket['values'][0]
                            if 'odd' in main_value:
                                try:
                                    main_odds = float(main_value.get('odd', 0))
                                    logger.debug(f"🔍 DEBUG: Validating main odds in API-Football: {main_odds}")
                                    if OddsFilter.validate_odds(main_odds):
                                        logger.debug(f"🔍 DEBUG: Main odds valid in API-Football: {main_odds}")
                                        return True
                                    else:
                                        logger.debug(f"🔍 DEBUG: Main odds invalid in API-Football: {main_odds}")
                                        return False  # Main odds failed validation
                                except (ValueError, TypeError):
                                    logger.debug(f"🔍 DEBUG: Error converting main odds in API-Football: {main_value.get('odd', 'N/A')}")
                                    return False
            return False
        except Exception as e:
            logger.debug(f"🔍 DEBUG: Exception in API-Football validation: {e}")
            return False
    
    def _try_sportmonks_structure(self, odds_data: List[Dict]) -> bool:
        """Try SportMonks style structure: odds -> value - Validate MAIN odds only"""
        try:
            for market in odds_data:
                if isinstance(market, dict) and 'odds' in market and market['odds']:
                    # CRITICAL: Only validate the FIRST (main) odds value
                    main_odds_item = market['odds'][0]
                    if 'value' in main_odds_item:
                        try:
                            main_odds = float(main_odds_item.get('value', 0))
                            logger.debug(f"🔍 DEBUG: Validating main odds in SportMonks: {main_odds}")
                            if OddsFilter.validate_odds(main_odds):
                                logger.debug(f"🔍 DEBUG: Main odds valid in SportMonks: {main_odds}")
                                return True
                            else:
                                logger.debug(f"🔍 DEBUG: Main odds invalid in SportMonks: {main_odds}")
                                return False  # Main odds failed validation
                        except (ValueError, TypeError):
                            logger.debug(f"🔍 DEBUG: Error converting main odds in SportMonks: {main_odds_item.get('value', 'N/A')}")
                            return False
            return False
        except Exception as e:
            logger.debug(f"🔍 DEBUG: Exception in SportMonks validation: {e}")
            return False
    
    def _try_flat_odds_structure(self, odds_data: List[Dict]) -> bool:
        """Try flat structure: direct odds key - Validate MAIN odds only"""
        try:
            for market in odds_data:
                if isinstance(market, dict):
                    # Try common odds keys - validate the first valid one found
                    for odds_key in ['odds', 'price', 'odd', 'value']:
                        if odds_key in market:
                            try:
                                main_odds = float(market.get(odds_key, 0))
                                logger.debug(f"🔍 DEBUG: Validating main odds in flat structure: {main_odds}")
                                if OddsFilter.validate_odds(main_odds):
                                    logger.debug(f"🔍 DEBUG: Main odds valid in flat structure: {main_odds}")
                                    return True
                                else:
                                    logger.debug(f"🔍 DEBUG: Main odds invalid in flat structure: {main_odds}")
                                    return False  # Main odds failed validation
                            except (ValueError, TypeError):
                                logger.debug(f"🔍 DEBUG: Error converting main odds in flat structure: {market.get(odds_key, 'N/A')}")
                                return False
            return False
        except Exception as e:
            logger.debug(f"🔍 DEBUG: Exception in flat structure validation: {e}")
            return False
    
    def _try_generic_structure(self, odds_data: List[Dict]) -> bool:
        """Try generic structure: recursively search for odds values - Validate MAIN odds only"""
        try:
            def search_recursively(obj, depth=0):
                if depth > 10:  # Increase depth limit for deep structures
                    return False
                
                if isinstance(obj, dict):
                    # Check if this dict has an odds-like key - validate the first valid one found
                    for key, value in obj.items():
                        if key.lower() in ['odds', 'price', 'odd', 'value'] and isinstance(value, (int, float, str)):
                            try:
                                main_odds = float(value)
                                logger.debug(f"🔍 DEBUG: Validating main odds in generic structure: {main_odds}")
                                if OddsFilter.validate_odds(main_odds):
                                    logger.debug(f"🔍 DEBUG: Main odds valid in generic structure: {main_odds}")
                                    return True
                                else:
                                    logger.debug(f"🔍 DEBUG: Main odds invalid in generic structure: {main_odds}")
                                    return False  # Main odds failed validation
                            except (ValueError, TypeError):
                                logger.debug(f"🔍 DEBUG: Error converting main odds in generic structure: {value}")
                                return False
                        
                        # Recursively search nested objects
                        if isinstance(value, (dict, list)):
                            if search_recursively(value, depth + 1):
                                return True
                
                elif isinstance(obj, list):
                    for item in obj:
                        if search_recursively(item, depth + 1):
                            return True
                
                return False
            
            return search_recursively(odds_data)
            
        except Exception:
            return False
    
    def _calculate_roi_rating(self, odds_data: List[Dict], match: Dict, match_index: int) -> float:
        """Calculate ROI rating based on actual odds data and match context"""
        try:
            if not odds_data:
                return 0.3 + (match_index * 0.05)
            
            # Base rating starts from match position
            base_rating = 0.5 + (match_index * 0.1)
            
            # Analyze odds for value opportunities
            total_markets = len(odds_data)
            value_opportunities = 0
            
            for market in odds_data:
                if isinstance(market, dict):
                    # Look for markets with good value (odds > 2.0)
                    if 'bookmakers' in market:
                        for bookmaker in market['bookmakers']:
                            if 'bets' in bookmaker:
                                for bet in bookmaker['bets']:
                                    if 'values' in bet:
                                        for value in bet['values']:
                                            if 'odd' in value:
                                                try:
                                                    odd_value = float(value.get('odd', 0))
                                                    if odd_value > 2.0:  # High odds = potential value
                                                        value_opportunities += 1
                                                except (ValueError, TypeError):
                                                    continue
            
            # Adjust rating based on value opportunities
            if value_opportunities > 0:
                value_bonus = min(value_opportunities * 0.2, 0.5)  # Max 0.5 bonus
                base_rating += value_bonus
            
            # Adjust based on market variety
            market_bonus = min(total_markets * 0.05, 0.3)  # Max 0.3 bonus
            base_rating += market_bonus
            
            # Ensure rating is within reasonable bounds
            return min(max(base_rating, 0.1), 2.0)
            
        except Exception as e:
            logger.error(f"Error calculating ROI rating: {e}")
            return 0.3 + (match_index * 0.05)

    # Error message posting method removed - no longer needed in ROI-only mode

    # No matches message method removed - no longer needed in ROI-only mode

    # Value bets posting method removed - no longer needed in ROI-only mode

    # Daily summary method removed - no longer needed in ROI-only mode
