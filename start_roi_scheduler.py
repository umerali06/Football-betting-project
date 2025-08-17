#!/usr/bin/env python3
"""
ROI Scheduler for FIXORA PRO
Automatically sends ROI updates every morning at 8am UK time
"""

import asyncio
import logging
import schedule
import time
from datetime import datetime, timezone, timedelta
import pytz
from telegram_bot import TelegramBetBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('roi_scheduler.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class ROIScheduler:
    """Scheduler for automatic ROI updates"""
    
    def __init__(self):
        self.bot = TelegramBetBot()
        self.is_running = False
        self.uk_timezone = pytz.timezone('Europe/London')
    
    async def start(self):
        """Start the ROI scheduler"""
        try:
            logger.info("🚀 Starting ROI Scheduler...")
            
            # Initialize the bot
            await self.bot.start()
            
            if not self.bot.is_running:
                logger.error("❌ Failed to initialize bot")
                return False
            
            logger.info("✅ Bot initialized successfully")
            
            # Schedule morning ROI updates at 8am UK time
            # Note: schedule library doesn't support timezone, so we'll use local time
            # UK time is typically UTC+0 (GMT) or UTC+1 (BST) depending on daylight saving
            schedule.every().day.at("08:00").do(self.send_morning_updates)
            
            # Also schedule a test update in 1 minute for testing
            schedule.every(1).minutes.do(self.send_test_update)
            
            self.is_running = True
            logger.info("✅ ROI Scheduler started successfully")
            logger.info("🕗 Morning updates scheduled for 8am daily (adjust for your local timezone)")
            logger.info("Note: If you're not in UK timezone, adjust the time in the schedule.every().day.at() call")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start ROI scheduler: {e}")
            return False
    
    async def send_morning_updates(self):
        """Send morning ROI updates to all active users"""
        try:
            logger.info("🌅 Sending morning ROI updates...")
            
            if not self.bot.user_sessions:
                logger.info("📝 No active users to send updates to")
                return
            
            success_count = 0
            total_users = len(self.bot.user_sessions)
            
            for chat_id in self.bot.user_sessions.keys():
                try:
                    success = await self.bot.send_morning_roi_update(chat_id)
                    if success:
                        success_count += 1
                        logger.info(f"✅ Morning update sent to chat {chat_id}")
                    else:
                        logger.warning(f"⚠️ Failed to send morning update to chat {chat_id}")
                except Exception as e:
                    logger.error(f"❌ Error sending morning update to chat {chat_id}: {e}")
            
            logger.info(f"🌅 Morning updates completed: {success_count}/{total_users} users")
            
        except Exception as e:
            logger.error(f"❌ Error in send_morning_updates: {e}")
    
    async def send_test_update(self):
        """Send a test update (for testing purposes)"""
        try:
            logger.info("🧪 Sending test update...")
            
            if not self.bot.user_sessions:
                logger.info("📝 No active users for test update")
                return
            
            # Send test message to first user
            first_chat_id = list(self.bot.user_sessions.keys())[0]
            test_message = """
🧪 **Test Update**

This is a test message from the ROI Scheduler.
Morning updates will be sent daily at 8am UK time.

💰 **Commands Available**:
• /analyze_roi - Analyze ROI opportunities
• /report - Generate performance report
• /status - Check bot status

🕗 **Next Update**: Tomorrow at 8am UK time
"""
            
            await self.bot.send_message_to_user(first_chat_id, test_message)
            logger.info(f"✅ Test update sent to chat {first_chat_id}")
            
        except Exception as e:
            logger.error(f"❌ Error in send_test_update: {e}")
    
    async def run_scheduler(self):
        """Run the scheduler loop"""
        try:
            logger.info("🔄 Starting scheduler loop...")
            
            while self.is_running:
                # Run pending scheduled tasks
                schedule.run_pending()
                
                # Wait for 1 minute before next check
                await asyncio.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("⏹️ Scheduler interrupted by user")
        except Exception as e:
            logger.error(f"❌ Error in scheduler loop: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the scheduler"""
        try:
            logger.info("🛑 Stopping ROI Scheduler...")
            self.is_running = False
            
            if self.bot:
                await self.bot.stop()
            
            logger.info("✅ ROI Scheduler stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping scheduler: {e}")

async def main():
    """Main function"""
    try:
        scheduler = ROIScheduler()
        
        # Start the scheduler
        if await scheduler.start():
            logger.info("🎉 ROI Scheduler is now running!")
            logger.info("📋 Available Commands:")
            logger.info("• /analyze_roi - Analyze ROI opportunities")
            logger.info("• /report - Generate performance report")
            logger.info("• /status - Check bot status")
            logger.info("🕗 Morning updates: Daily at 8am UK time")
            
            # Run the scheduler
            await scheduler.run_scheduler()
        else:
            logger.error("❌ Failed to start ROI Scheduler")
            
    except Exception as e:
        logger.error(f"❌ Main function error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Program interrupted by user")
    except Exception as e:
        logger.error(f"❌ Program error: {e}")
