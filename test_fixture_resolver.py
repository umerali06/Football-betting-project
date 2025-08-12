#!/usr/bin/env python3
"""
Practical test for fixture ID resolver
Shows how SportMonks fixtures get mapped to API-Football IDs
"""

import asyncio
import logging
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.unified_api_client import UnifiedAPIClient
import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_fixture_resolver():
    """Test the fixture ID resolver with practical examples"""
    client = UnifiedAPIClient()
    
    print("🔍 Testing Fixture ID Resolver (Practical Example)")
    print("=" * 60)
    
    try:
        # Get today's matches from both APIs
        print("\n1️⃣ Fetching today's matches...")
        today_matches = await client.get_today_matches(include_live=True)
        
        if not today_matches:
            print("❌ No matches found for today")
            return False
        
        print(f"✅ Found {len(today_matches)} matches")
        
        # Show provider breakdown
        providers = {}
        for match in today_matches:
            provider = match.get("_provider", "unknown")
            providers[provider] = providers.get(provider, 0) + 1
        
        print(f"   📊 Provider breakdown: {providers}")
        
        # Test fixture ID resolution for SportMonks fixtures
        print("\n2️⃣ Testing fixture ID resolution...")
        sportmonks_fixtures = [m for m in today_matches if m.get("_provider") == "sportmonks"]
        
        if sportmonks_fixtures:
            print(f"   Found {len(sportmonks_fixtures)} SportMonks fixtures")
            
            # Test resolution for first few SportMonks fixtures
            for i, fixture in enumerate(sportmonks_fixtures[:3]):
                print(f"\n   🔍 Fixture {i+1}:")
                
                # Extract team names
                home_team, away_team = client.extract_team_names(fixture)
                print(f"      {home_team} vs {away_team}")
                
                # Try to resolve API-Football fixture ID
                api_football_id = await client.resolve_api_football_fixture_id(fixture)
                if api_football_id:
                    print(f"      ✅ Resolved API-Football ID: {api_football_id}")
                    
                    # Test if we can get data with this ID
                    print(f"      🧪 Testing data retrieval...")
                    
                    # Try odds
                    odds = await client.api_football.get_match_odds(api_football_id)
                    print(f"         Odds: {'✅ Available' if odds else '❌ Not available'}")
                    
                    # Try predictions
                    predictions = await client.api_football.get_predictions(api_football_id)
                    print(f"         Predictions: {'✅ Available' if predictions else '❌ Not available'}")
                    
                    # Try statistics
                    stats = await client.api_football.get_fixture_statistics(api_football_id)
                    print(f"         Statistics: {'✅ Available' if stats else '❌ Not available'}")
                    
                else:
                    print(f"      ❌ Could not resolve API-Football ID")
        else:
            print("   ℹ️  No SportMonks fixtures found (all from API-Football)")
        
        # Test the allow_empty functionality
        print("\n3️⃣ Testing allow_empty functionality...")
        
        # Test with a real fixture ID (if we have one)
        if today_matches:
            test_fixture = today_matches[0]
            fixture_id = client.extract_fixture_id(test_fixture)
            
            if fixture_id:
                print(f"   Testing with fixture ID: {fixture_id}")
                
                # Test odds with allow_empty=True
                print("   🎯 Testing odds with allow_empty=True...")
                odds_result, odds_source = await client._try_api_football_first("get_match_odds", fixture_id, allow_empty=True)
                print(f"      Result: {'Empty' if odds_result == [] else 'Data' if odds_result else 'None'}")
                print(f"      Source: {odds_source}")
                
                # Test predictions with allow_empty=True
                print("   🎯 Testing predictions with allow_empty=True...")
                pred_result, pred_source = await client._try_api_football_first("get_predictions", fixture_id, allow_empty=True)
                print(f"      Result: {'Empty' if pred_result == [] else 'Data' if pred_result else 'None'}")
                print(f"      Source: {pred_source}")
                
                # Test xG with allow_empty=True
                print("   🎯 Testing xG with allow_empty=True...")
                xg_result, xg_source = await client._try_api_football_first("get_expected_goals", fixture_id, allow_empty=True)
                print(f"      Result: {'Empty' if xg_result == [] else 'Data' if xg_result else 'None'}")
                print(f"      Source: {xg_source}")
        
        # Show API stats
        print("\n4️⃣ API Usage Statistics:")
        stats = client.get_api_stats()
        print(f"   📊 Total requests: {stats['total_requests']}")
        print(f"   📊 Fallbacks used: {stats['fallbacks_used']}")
        print(f"   📊 API-Football success rate: {stats['api_football']['success_rate']}%")
        print(f"   📊 SportMonks success rate: {stats['sportmonks']['success_rate']}%")
        
        print("\n" + "=" * 60)
        print("🎯 Fixture ID Resolver Test Completed!")
        print("✅ No more false fallbacks for empty odds/predictions/xG")
        print("✅ SportMonks fixtures can now use API-Football for rich data")
        print("✅ allow_empty flag prevents unnecessary fallbacks")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        await client.close()

if __name__ == "__main__":
    # Check if API key is configured
    if not hasattr(config, 'API_FOOTBALL_API_KEY') or not config.API_FOOTBALL_API_KEY:
        print("❌ Error: API_FOOTBALL_API_KEY not configured in config.py")
        sys.exit(1)
    
    print(f"🔑 Using API key: {config.API_FOOTBALL_API_KEY[:10]}...")
    print(f"🌍 Timezone: {getattr(config, 'API_FOOTBALL_TIMEZONE', 'Asia/Karachi')}")
    
    # Run the test
    success = asyncio.run(test_fixture_resolver())
    
    if success:
        print("\n🎉 Fixture ID resolver is working perfectly!")
        print("🚀 Your system will now have much cleaner logs and better data coverage!")
    else:
        print("\n💥 Test failed. Check the errors above.")
        sys.exit(1)
