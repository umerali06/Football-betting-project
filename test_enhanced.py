#!/usr/bin/env python3
"""
Enhanced FIXORA PRO Real-Time Analyzer Test Script
Tests the system with graceful fallbacks for both free and subscription plans
"""

import asyncio
import logging
from realtime_analyzer import RealTimeAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_enhanced_analyzer():
    """Test the enhanced realtime analyzer"""
    analyzer = None
    
    try:
        logger.info("🚀 Testing Enhanced FIXORA PRO Real-Time Analyzer...")
        
        # Initialize analyzer
        analyzer = RealTimeAnalyzer()
        logger.info("✅ Analyzer initialized successfully")
        
        # Test system info
        system_info = analyzer.get_system_info()
        logger.info(f"📊 System Info: {system_info['name']} v{system_info['version']}")
        logger.info(f"🔧 Features: {', '.join(system_info['features'].keys())}")
        
        # Test live matches analysis
        logger.info("🔍 Testing live matches analysis...")
        live_results = await analyzer.analyze_live_matches()
        logger.info(f"📊 Live analysis results: {len(live_results)} matches")
        
        # Test today's matches analysis
        logger.info("🔍 Testing today's matches analysis...")
        today_results = await analyzer.analyze_today_matches()
        logger.info(f"📊 Today's analysis results: {len(today_results)} matches")
        
        # Generate Telegram summary
        if today_results or live_results:
            all_results = live_results + today_results
            logger.info("📱 Generating Telegram summary...")
            summary = await analyzer.get_telegram_summary(all_results)
            logger.info("✅ Telegram summary generated successfully")
            
            # Show preview (first 500 characters)
            preview = summary[:500] + "..." if len(summary) > 500 else summary
            logger.info(f"📋 Summary Preview:\n{preview}")
        else:
            logger.warning("⚠️ No results to generate summary")
        
        # Test individual match analysis
        if today_results:
            logger.info("🔍 Testing individual match analysis...")
            sample_match = today_results[0]
            logger.info(f"📊 Sample match: {sample_match.get('home_team', 'Unknown')} vs {sample_match.get('away_team', 'Unknown')}")
            logger.info(f"🔧 Analysis quality: {sample_match.get('analysis_quality', 'Unknown')}")
            logger.info(f"📈 Data availability: {sample_match.get('data_availability', {})}")
        
        logger.info("✅ Enhanced analyzer test completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise
    finally:
        if analyzer:
            await analyzer.close()
            logger.info("✅ Analyzer closed")

async def main():
    """Main test function"""
    try:
        await test_enhanced_analyzer()
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
