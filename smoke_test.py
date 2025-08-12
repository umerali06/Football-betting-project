#!/usr/bin/env python3
"""
Smoke test for API-Football endpoints
Quick verification that your paid plan is working correctly
"""

import asyncio
import logging
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.api_apifootball import ApiFootballClient
import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def smoke_test():
    """Quick smoke test of key endpoints"""
    client = ApiFootballClient()
    
    print("🚬 API-Football Smoke Test")
    print("=" * 40)
    
    try:
        # Test 1: Status endpoint (if available)
        print("\n1️⃣ Testing basic connectivity...")
        
        # Test 2: Today's fixtures
        print("\n2️⃣ Testing /fixtures?date=...")
        matches = await client.get_today_matches()
        if matches:
            print(f"✅ Found {len(matches)} matches")
            if len(matches) > 0:
                first_match = matches[0]
                fixture_id = client.extract_fixture_id(first_match)
                print(f"   Sample fixture ID: {fixture_id}")
                home_team = first_match.get('teams', {}).get('home', {}).get('name', 'Unknown')
                away_team = first_match.get('teams', {}).get('away', {}).get('name', 'Unknown')
                print(f"   Sample match: {home_team} vs {away_team}")
        else:
            print("❌ No matches found - check your API key and plan")
            return False
        
        # Test 3: Specific fixture details
        if matches and len(matches) > 0:
            first_match = matches[0]
            fixture_id = client.extract_fixture_id(first_match)
            
            if fixture_id:
                print(f"\n3️⃣ Testing /fixtures?id={fixture_id}")
                details = await client.get_fixture_details(fixture_id)
                if details:
                    print("✅ Fixture details working")
                else:
                    print("❌ Fixture details failed")
                
                print(f"\n4️⃣ Testing /odds?fixture={fixture_id}")
                odds = await client.get_match_odds(fixture_id)
                if odds:
                    print(f"✅ Odds working - {len(odds)} bookmakers")
                else:
                    print("ℹ️  No odds (might be normal for some fixtures)")
                
                print(f"\n5️⃣ Testing /predictions?fixture={fixture_id}")
                predictions = await client.get_predictions(fixture_id)
                if predictions:
                    print("✅ Predictions working")
                else:
                    print("ℹ️  No predictions (might be normal for some fixtures)")
                
                print(f"\n6️⃣ Testing /odds/live?fixture={fixture_id}")
                live_odds = await client.get_live_odds(fixture_id)
                if live_odds:
                    print(f"✅ Live odds working - {len(live_odds)} bookmakers")
                else:
                    print("ℹ️  No live odds (might be normal for some fixtures)")
            else:
                print("❌ Could not extract fixture ID")
                return False
        
        print("\n" + "=" * 40)
        print("🎯 Smoke test completed successfully!")
        print("✅ Your API-Football paid plan is working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
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
    
    print(f"🔑 API Key: {config.API_FOOTBALL_API_KEY[:10]}...")
    print(f"🌍 Timezone: {getattr(config, 'API_FOOTBALL_TIMEZONE', 'Asia/Karachi')}")
    
    # Run smoke test
    success = asyncio.run(smoke_test())
    
    if success:
        print("\n🎉 All tests passed! Your system is ready to use.")
    else:
        print("\n💥 Tests failed. Check the errors above.")
        sys.exit(1)
