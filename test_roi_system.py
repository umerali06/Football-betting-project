#!/usr/bin/env python3
"""
Test script for FIXORA PRO ROI System
Tests ROI tracking, league filtering, and report generation
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
        logging.FileHandler('roi_test.log')
    ]
)

logger = logging.getLogger(__name__)

async def test_roi_tracker():
    """Test ROI tracker functionality"""
    logger.info("Testing ROI Tracker...")
    
    try:
        from betting.roi_tracker import ROITracker
        
        tracker = ROITracker()
        
        # Test recording a bet
        bet_data = {
            'fixture_id': 12345,
            'league_id': 39,  # Premier League
            'league_name': 'England - Premier League',
            'home_team': 'Manchester United',
            'away_team': 'Liverpool',
            'market_type': 'match_result',
            'selection': 'home_win',
            'odds': 2.5,
            'stake': 100.0,
            'bet_date': '2024-01-15',
            'match_date': '2024-01-15'
        }
        
        success = tracker.record_bet(bet_data)
        if success:
            logger.info("✅ Bet recorded successfully")
        else:
            logger.error("❌ Failed to record bet")
            return False
        
        # Test updating bet result
        success = tracker.update_bet_result(12345, 'win', 250.0)
        if success:
            logger.info("✅ Bet result updated successfully")
        else:
            logger.error("❌ Failed to update bet result")
            return False
        
        # Test getting performance data
        overall = tracker.get_overall_performance()
        market_perf = tracker.get_market_performance()
        league_perf = tracker.get_league_performance()
        
        logger.info(f"Overall performance: {overall}")
        logger.info(f"Market performance: {market_perf}")
        logger.info(f"League performance: {league_perf}")
        
        logger.info("✅ ROI Tracker test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ ROI Tracker test failed: {e}")
        return False

async def test_league_filter():
    """Test league filter functionality"""
    logger.info("Testing League Filter...")
    
    try:
        from api.league_filter import LeagueFilter
        
        filter_service = LeagueFilter()
        
        # Test league filtering
        test_matches = [
            {
                'id': 1,
                'league': {'id': 39},  # Premier League
                'home_team': 'Arsenal',
                'away_team': 'Chelsea',
                'date': '2024-01-15'
            },
            {
                'id': 2,
                'league': {'id': 140},  # La Liga
                'home_team': 'Barcelona',
                'away_team': 'Real Madrid',
                'date': '2024-01-15'
            },
            {
                'id': 3,
                'league': {'id': 999},  # Unknown league
                'home_team': 'Team A',
                'away_team': 'Team B',
                'date': '2024-01-15'
            }
        ]
        
        filtered_matches = filter_service.filter_matches_by_league(test_matches)
        summary = filter_service.get_filtered_matches_summary(test_matches)
        
        logger.info(f"Filtered matches: {len(filtered_matches)}")
        logger.info(f"Filtering summary: {summary}")
        
        if len(filtered_matches) == 2:  # Should filter out unknown league
            logger.info("✅ League filtering working correctly")
        else:
            logger.error(f"❌ League filtering failed: expected 2, got {len(filtered_matches)}")
            return False
        
        logger.info("✅ League Filter test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ League Filter test failed: {e}")
        return False

async def test_roi_system():
    """Test comprehensive ROI system"""
    logger.info("Testing Comprehensive ROI System...")
    
    try:
        from betting.roi_system import ROISystem
        
        roi_system = ROISystem()
        
        # Test getting ROI summary
        roi_summary = await roi_system.get_roi_summary()
        logger.info(f"ROI summary: {roi_summary}")
        
        # Test getting filtered matches
        matches = await roi_system.get_filtered_matches(days_ahead=1)
        logger.info(f"Filtered matches: {len(matches)}")
        
        logger.info("✅ ROI System test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ ROI System test failed: {e}")
        return False

async def main():
    """Run all ROI system tests"""
    logger.info("Starting FIXORA PRO ROI System Tests")
    logger.info("=" * 60)
    
    test_results = {}
    
    # Test individual components
    test_results['roi_tracker'] = await test_roi_tracker()
    test_results['league_filter'] = await test_league_filter()
    test_results['roi_system'] = await test_roi_system()
    
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
        logger.info("✅ All tests passed! ROI system is working correctly.")
    else:
        logger.warning("⚠️ Some tests failed. Check the logs for details.")
    
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
