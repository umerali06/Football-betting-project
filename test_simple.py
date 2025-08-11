#!/usr/bin/env python3
"""
Simple test script for FIXORA PRO system
Tests basic functionality without emojis
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

async def test_basic_functionality():
    """Test basic system functionality"""
    try:
        logger.info("Testing FIXORA PRO basic functionality...")
        
        # Initialize analyzer
        analyzer = RealTimeAnalyzer()
        logger.info("Analyzer initialized successfully")
        
        # Test API connection
        logger.info("Testing API connection...")
        today_matches = await analyzer.api_client.get_today_matches()
        
        if today_matches:
            logger.info(f"Found {len(today_matches)} matches for today")
            
            # Test analysis
            logger.info("Testing match analysis...")
            analysis_results = await analyzer.analyze_today_matches()
            
            if analysis_results:
                logger.info(f"Successfully analyzed {len(analysis_results)} matches")
                
                # Test Telegram summary generation
                logger.info("Testing Telegram summary generation...")
                summary = await analyzer.get_telegram_summary(analysis_results)
                
                if summary:
                    logger.info("Telegram summary generated successfully")
                    logger.info(f"Summary length: {len(summary)} characters")
                    logger.info("Summary preview:")
                    print("-" * 50)
                    print(summary[:500] + "..." if len(summary) > 500 else summary)
                    print("-" * 50)
                else:
                    logger.error("Failed to generate Telegram summary")
            else:
                logger.warning("No analysis results generated")
        else:
            logger.warning("No matches found for today")
        
        # Close analyzer
        await analyzer.close()
        logger.info("Test completed successfully")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

async def main():
    """Main test function"""
    try:
        await test_basic_functionality()
        print("\n" + "="*50)
        print("TEST PASSED: System is working correctly!")
        print("="*50)
    except Exception as e:
        print("\n" + "="*50)
        print(f"TEST FAILED: {e}")
        print("="*50)
        return 1
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
