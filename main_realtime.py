#!/usr/bin/env python3
"""
FIXORA PRO Real-Time Football Betting System
Enhanced version with real-time analysis (Telegram bot runs separately)
"""

import asyncio
import logging
import signal
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import schedule

from realtime_analyzer import RealTimeAnalyzer
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('fixora_pro.log')
    ]
)

logger = logging.getLogger(__name__)

class RealTimeBettingSystem:
    """Enhanced real-time football betting analysis system"""
    
    def __init__(self):
        self.analyzer = RealTimeAnalyzer()
        # Remove Telegram bot - it runs separately to avoid conflicts
        self.is_running = False
        self.analysis_stats = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'start_time': None,
            'last_analysis': None
        }
        
    async def start(self):
        """Start the real-time system"""
        try:
            logger.info("Starting FIXORA PRO Real-Time Football Betting System...")
            logger.info("Note: Telegram bot runs separately to avoid conflicts")
            
            # Schedule analysis tasks
            self.schedule_analysis()
            logger.info("Analysis tasks scheduled")
            
            # Run initial analysis
            await self.run_initial_analysis()
            
            logger.info("Real-time system started successfully")
            logger.info("To use the Telegram bot, run: python bot_interface/telegram_bot.py")
            
        except Exception as e:
            logger.error(f"Failed to start system: {e}")
            raise
    
    def schedule_analysis(self):
        """Schedule periodic analysis tasks"""
        # Live analysis every 5 minutes with sync wrapper
        schedule.every(5).minutes.do(self._run_live_analysis_sync)
        
        # Daily analysis at 9 AM with sync wrapper
        schedule.every().day.at("09:00").do(self._run_daily_analysis_sync)
        
        # System status every hour with sync wrapper
        schedule.every().hour.do(self._send_system_status_sync)
    
    def _run_live_analysis_sync(self):
        """Sync wrapper for run_live_analysis to avoid coroutine warning"""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.run_live_analysis())
        except Exception as e:
            logger.error("Error in live analysis scheduler: %s", e)
        finally:
            if loop and not loop.is_closed():
                loop.close()
    
    def _run_daily_analysis_sync(self):
        """Sync wrapper for run_daily_analysis to avoid coroutine warning"""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.run_daily_analysis())
        except Exception as e:
            logger.error("Error in daily analysis scheduler: %s", e)
        finally:
            if loop and not loop.is_closed():
                loop.close()
    
    def _send_system_status_sync(self):
        """Sync wrapper for send_system_status to avoid coroutine warning"""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.send_system_status())
        except Exception as e:
            logger.error("Error in system status scheduler: %s", e)
        finally:
            if loop and not loop.is_closed():
                loop.close()
    
    async def run_initial_analysis(self):
        """Run initial analysis on startup"""
        try:
            logger.info("Running initial analysis...")
            
            # Analyze today's matches
            today_results = await self.analyzer.analyze_today_matches()
            
            if today_results:
                # Generate summary (but don't send automatically - bot is interactive now)
                summary = await self.analyzer.get_telegram_summary(today_results)
                logger.info(f"Analysis summary generated: {len(summary)} characters")
                
                logger.info(f"Initial analysis completed: {len(today_results)} matches analyzed")
                logger.info("Bot is now interactive - users can send commands to get analysis")
            else:
                logger.info("No matches found for initial analysis")
                
        except Exception as e:
            logger.error(f"Initial analysis failed: {e}")
            await self._run_fallback_analysis()
    
    async def run_live_analysis(self):
        """Run live match analysis"""
        try:
            logger.info("Running live match analysis...")
            
            results = await self.analyzer.analyze_live_matches()
            
            if results:
                # Update stats
                self.analysis_stats['total_analyses'] += 1
                self.analysis_stats['successful_analyses'] += 1
                self.analysis_stats['last_analysis'] = datetime.now()
                
                # Generate summary (bot is interactive now)
                summary = await self.analyzer.get_telegram_summary(results)
                logger.info(f"Live analysis summary generated: {len(summary)} characters")
                
                logger.info(f"Live analysis completed: {len(results)} matches")
                logger.info("Users can use /live command to see live matches")
            else:
                logger.info("No live matches found")
                
        except Exception as e:
            logger.error(f"Live analysis failed: {e}")
            self.analysis_stats['failed_analyses'] += 1
            await self._run_fallback_analysis()
    
    async def run_daily_analysis(self):
        """Run daily match analysis"""
        try:
            logger.info("Running daily match analysis...")
            
            results = await self.analyzer.analyze_today_matches()
            
            if results:
                # Update stats
                self.analysis_stats['total_analyses'] += 1
                self.analysis_stats['successful_analyses'] += 1
                self.analysis_stats['last_analysis'] = datetime.now()
                
                # Generate summary (bot is interactive now)
                summary = await self.analyzer.get_telegram_summary(results)
                logger.info(f"Daily analysis summary generated: {len(summary)} characters")
                
                logger.info(f"Daily analysis completed: {len(results)} matches")
                logger.info("Users can use /analyze command to see today's analysis")
            else:
                logger.info("No matches found for daily analysis")
                
        except Exception as e:
            logger.error(f"Daily analysis failed: {e}")
            self.analysis_stats['failed_analyses'] += 1
            await self._run_fallback_analysis()
    
    async def _run_fallback_analysis(self):
        """Run fallback analysis when main analysis fails"""
        try:
            logger.info("Running fallback analysis...")
            
            # Try to get basic fixture data
            basic_data = await self._get_basic_fixture_data()
            
            if basic_data:
                # Log status (bot is interactive now)
                logger.info("System Status: Basic analysis running due to API limitations")
                logger.info("Users can check status with /status command")
                
        except Exception as e:
            logger.error(f"Fallback analysis failed: {e}")
    
    async def _get_basic_fixture_data(self):
        """Get basic fixture data as fallback"""
        try:
            # This would be a simplified data fetch
            return True
        except Exception:
            return False
    
    async def send_system_status(self):
        """Log system status (bot is interactive now)"""
        try:
            status = self.get_system_status()
            logger.info("System status updated:")
            logger.info(status)
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
    
    def get_system_status(self):
        """Get current system status"""
        uptime = self._get_uptime()
        features_status = self._get_features_status()
        
        status = f"""
System Status Report
===================
Uptime: {uptime}
Total Analyses: {self.analysis_stats['total_analyses']}
Successful: {self.analysis_stats['successful_analyses']}
Failed: {self.analysis_stats['failed_analyses']}
Last Analysis: {self._format_last_analysis()}

{features_status}
        """
        return status.strip()
    
    def _get_uptime(self):
        """Get system uptime"""
        if not self.analysis_stats['start_time']:
            return "Not started"
        
        uptime = datetime.now() - self.analysis_stats['start_time']
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"
    
    def _get_features_status(self):
        """Get features availability status"""
        return """
Feature Status:
- Live Analysis: Active
- Daily Analysis: Scheduled
- Telegram Integration: Runs Separately
- API Client: Connected
        """
    
    def _format_last_analysis(self):
        """Format last analysis time"""
        if not self.analysis_stats['last_analysis']:
            return "Never"
        return self.analysis_stats['last_analysis'].strftime("%H:%M:%S")
    
    async def shutdown(self):
        """Shutdown the system gracefully"""
        try:
            logger.info("Shutting down FIXORA PRO system...")
            
            # Close analyzer
            await self.analyzer.close()
            
            logger.info("System shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    async def run(self):
        """Main run loop"""
        try:
            self.is_running = True
            self.analysis_stats['start_time'] = datetime.now()
            
            logger.info("FIXORA PRO system is running. Press Ctrl+C to stop.")
            
            while self.is_running:
                schedule.run_pending()
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"System error: {e}")
        finally:
            await self.shutdown()

async def main():
    """Main entry point"""
    system = RealTimeBettingSystem()
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        system.is_running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await system.start()
        await system.run()
    except Exception as e:
        logger.error(f"System failed to start: {e}")
        await system.shutdown()
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("System stopped by user")
    except Exception as e:
        logger.error(f"System error: {e}")
        sys.exit(1)
