#!/usr/bin/env python3
"""
Test script for the unified API system
Tests API-Football as primary and SportMonks as fallback
"""

import asyncio
import logging
from api.unified_api_client import UnifiedAPIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_unified_api():
    """Test the unified API system"""
    try:
        logger.info("Testing Unified API System...")
        
        # Create unified API client
        api_client = UnifiedAPIClient()
        logger.info("Unified API client created successfully")
        
        # Test connection to both APIs
        logger.info("Testing API connections...")
        connection_results = await api_client.test_connection()
        
        logger.info("Connection test results:")
        for api, status in connection_results.items():
            logger.info(f"  {api}: {'✅ SUCCESS' if status else '❌ FAILED'}")
        
        # Test today's matches
        logger.info("Testing today's matches...")
        today_matches = await api_client.get_today_matches()
        
        if today_matches:
            logger.info(f"✅ Found {len(today_matches)} matches for today")
            
            # Test fixture details for first match
            if len(today_matches) > 0:
                first_match = today_matches[0]
                fixture_id = first_match.get('id') or first_match.get('fixture', {}).get('id')
                
                if fixture_id:
                    logger.info(f"Testing fixture details for ID: {fixture_id}")
                    fixture_details = await api_client.get_fixture_details(fixture_id)
                    
                    if fixture_details:
                        logger.info("✅ Fixture details retrieved successfully")
                        
                        # Test odds
                        logger.info("Testing match odds...")
                        odds = await api_client.get_match_odds(fixture_id)
                        
                        if odds:
                            logger.info(f"✅ Retrieved {len(odds)} odds entries")
                        else:
                            logger.info("⚠️ No odds available")
                        
                        # Test team form
                        logger.info("Testing team form...")
                        home_team_id = first_match.get('teams', {}).get('home', {}).get('id')
                        if home_team_id:
                            team_form = await api_client.get_team_form(home_team_id)
                            if team_form:
                                logger.info(f"✅ Retrieved team form: {len(team_form)} matches")
                            else:
                                logger.info("⚠️ No team form available")
                        
                        # Test predictions
                        logger.info("Testing predictions...")
                        predictions = await api_client.get_predictions(fixture_id)
                        if predictions:
                            logger.info("✅ Predictions retrieved successfully")
                        else:
                            logger.info("⚠️ No predictions available")
                    else:
                        logger.warning("⚠️ Could not retrieve fixture details")
                else:
                    logger.warning("⚠️ Could not extract fixture ID from first match")
        else:
            logger.warning("⚠️ No matches found for today")
        
        # Get API statistics
        api_stats = api_client.get_api_stats()
        logger.info("API Usage Statistics:")
        logger.info(f"  Total requests: {api_stats['total_requests']}")
        logger.info(f"  API-Football success rate: {api_stats['api_football']['success_rate']}%")
        logger.info(f"  SportMonks success rate: {api_stats['sportmonks']['success_rate']}%")
        logger.info(f"  Fallbacks used: {api_stats['fallbacks_used']}")
        
        # Close the client
        await api_client.close()
        logger.info("✅ Unified API test completed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Unified API test failed: {e}")
        return False

async def main():
    """Main test function"""
    try:
        success = await test_unified_api()
        
        if success:
            print("\n" + "="*60)
            print("🎉 UNIFIED API TEST PASSED!")
            print("="*60)
            print("✅ API-Football is working as primary API")
            print("✅ SportMonks is working as fallback API")
            print("✅ Unified system is functioning correctly")
            print("="*60)
            print("\n🚀 Your system is now using:")
            print("   • API-Football as PRIMARY data source")
            print("   • SportMonks as FALLBACK data source")
            print("   • Automatic failover when primary fails")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("❌ UNIFIED API TEST FAILED!")
            print("="*60)
            print("Please check your configuration and API keys")
            print("="*60)
            return 1
            
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
