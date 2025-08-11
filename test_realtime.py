import asyncio
import logging
from realtime_analyzer import RealTimeAnalyzer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_realtime_analyzer():
    """Test the real-time analyzer functionality"""
    logger.info("🧪 Testing Real-Time Analyzer...")
    
    try:
        # Initialize analyzer
        analyzer = RealTimeAnalyzer()
        logger.info("✅ RealTimeAnalyzer initialized successfully")
        
        # Test live matches analysis
        logger.info("🔍 Testing live matches analysis...")
        live_results = await analyzer.analyze_live_matches()
        logger.info(f"📊 Live analysis results: {len(live_results)} matches")
        
        # Test today's matches analysis
        logger.info("🔍 Testing today's matches analysis...")
        today_results = await analyzer.analyze_today_matches()
        logger.info(f"📊 Today's analysis results: {len(today_results)} matches")
        
        # Test Telegram summary generation
        if today_results or live_results:
            logger.info("📱 Testing Telegram summary generation...")
            all_results = live_results + today_results
            summary = await analyzer.get_telegram_summary(all_results)
            logger.info("✅ Telegram summary generated successfully")
            logger.info(f"📝 Summary length: {len(summary)} characters")
            
            # Print first 500 characters of summary
            print("\n" + "="*50)
            print("TELEGRAM SUMMARY PREVIEW:")
            print("="*50)
            print(summary[:500] + "..." if len(summary) > 500 else summary)
            print("="*50)
        
        # Close analyzer
        await analyzer.close()
        logger.info("✅ Test completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise

async def main():
    """Main test function"""
    try:
        await test_realtime_analyzer()
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
