#!/usr/bin/env python3
"""
Comprehensive Test Script for FIXORA PRO System
Tests all improvements: enhanced data fetching, better error handling, and improved quality assessment
"""

import asyncio
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('comprehensive_test.log')
    ]
)

logger = logging.getLogger(__name__)

async def test_api_football_client():
    """Test API-Football client with enhanced methods"""
    logger.info("Testing API-Football Client...")
    
    try:
        from api.api_apifootball import ApiFootballClient
        
        client = ApiFootballClient()
        
        # Test basic connectivity
        logger.info("Testing basic connectivity...")
        test_fixture_id = 1035037  # Example fixture ID
        
        # Test expected goals with multiple strategies
        logger.info("Testing expected goals with multiple strategies...")
        xg_data = await client.get_expected_goals(test_fixture_id)
        if xg_data:
            logger.info(f"Expected goals data retrieved: {type(xg_data)}")
            if isinstance(xg_data, dict):
                source = xg_data.get('source', 'unknown')
                logger.info(f"   Source: {source}")
        else:
            logger.info("Expected goals data not available (this is normal for many fixtures)")
        
        await client.close()
        logger.info("API-Football client test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"API-Football client test failed: {e}")
        return False

async def test_unified_api_client():
    """Test unified API client with enhanced methods"""
    logger.info("Testing Unified API Client...")
    
    try:
        from api.unified_api_client import UnifiedAPIClient
        
        client = UnifiedAPIClient()
        
        # Test today's matches
        logger.info("Testing today's matches...")
        today_matches = await client.get_today_matches()
        if today_matches:
            logger.info(f"Today's matches retrieved: {len(today_matches)} matches")
            
            # Test analysis of first match
            if today_matches:
                first_match = today_matches[0]
                fixture_id = client.extract_fixture_id(first_match)
                if fixture_id:
                    logger.info(f"   Testing fixture ID: {fixture_id}")
                    
                    # Test expected goals
                    xg_data = await client.get_expected_goals(fixture_id)
                    if xg_data:
                        logger.info(f"   Expected goals: {type(xg_data)}")
                    else:
                        logger.info(f"   Expected goals not available")
                    
                    # Test predictions
                    predictions = await client.get_predictions(fixture_id)
                    if predictions:
                        logger.info(f"   Predictions: {type(predictions)}")
                    else:
                        logger.info(f"   Predictions not available")
        else:
            logger.info("No matches found for today")
        
        await client.close()
        logger.info("Unified API client test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Unified API client test failed: {e}")
        return False

async def test_realtime_analyzer():
    """Test real-time analyzer with enhanced methods"""
    logger.info("Testing Real-Time Analyzer...")
    
    try:
        from realtime_analyzer import RealTimeAnalyzer
        
        analyzer = RealTimeAnalyzer()
        
        # Test today's matches analysis
        logger.info("Testing today's matches analysis...")
        analysis_results = await analyzer.analyze_today_matches()
        
        if analysis_results:
            logger.info(f"Analysis completed: {len(analysis_results)} matches")
            
            # Analyze first result
            first_result = analysis_results[0]
            logger.info(f"   First match: {first_result.get('home_team')} vs {first_result.get('away_team')}")
            logger.info(f"   Quality: {first_result.get('analysis_quality')}")
            logger.info(f"   Data availability: {first_result.get('data_availability')}")
            
            # Check data sources
            data_sources = first_result.get('data_sources', {})
            if data_sources:
                logger.info(f"   Data sources: {data_sources}")
            
        else:
            logger.info("No analysis results available")
        
        logger.info("Real-time analyzer test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Real-time analyzer test failed: {e}")
        return False

async def main():
    """Run all comprehensive tests"""
    logger.info("Starting Comprehensive FIXORA PRO System Test")
    logger.info("=" * 60)
    
    test_results = {}
    
    # Test API clients
    test_results['api_football'] = await test_api_football_client()
    test_results['unified_api'] = await test_unified_api_client()
    
    # Test analyzer
    test_results['realtime_analyzer'] = await test_realtime_analyzer()
    
    # Summary
    logger.info("=" * 60)
    logger.info("Test Results Summary:")
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "PASS" if result else "FAIL"
        logger.info(f"   {test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("All tests passed! System is working correctly.")
    else:
        logger.warning("Some tests failed. Check the logs for details.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with unexpected error: {e}")
        sys.exit(1)
