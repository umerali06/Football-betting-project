#!/usr/bin/env python3
"""
Test script for API-Football integration
Run this to verify your API key and endpoints are working correctly
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

async def test_api_football():
    """Test API-Football endpoints"""
    client = ApiFootballClient()
    
    print("🔍 Testing API-Football Integration...")
    print("=" * 50)
    
    try:
        # Test 1: Get today's matches
        print("\n📅 Test 1: Getting today's matches...")
        matches = await client.get_today_matches()
        if matches:
            print(f"✅ Success! Found {len(matches)} matches")
            if len(matches) > 0:
                first_match = matches[0]
                print(f"   First match: {first_match.get('teams', {}).get('home', {}).get('name', 'Unknown')} vs {first_match.get('teams', {}).get('away', {}).get('name', 'Unknown')}")
                fixture_id = client.extract_fixture_id(first_match)
                print(f"   Fixture ID: {fixture_id}")
        else:
            print("❌ No matches found")
        
        # Test 2: Get live scores
        print("\n⚽ Test 2: Getting live scores...")
        live_matches = await client.get_live_scores()
        if live_matches:
            print(f"✅ Success! Found {len(live_matches)} live matches")
        else:
            print("ℹ️  No live matches currently (this is normal)")
        
        # Test 3: Test specific fixture if we have one
        if matches and len(matches) > 0:
            first_match = matches[0]
            fixture_id = client.extract_fixture_id(first_match)
            
            if fixture_id:
                print(f"\n🔍 Test 3: Testing fixture details for ID {fixture_id}...")
                
                # Get fixture details
                details = await client.get_fixture_details(fixture_id)
                if details:
                    print("✅ Fixture details retrieved successfully")
                else:
                    print("❌ Failed to get fixture details")
                
                # Get odds
                print(f"\n💰 Test 4: Testing odds for fixture {fixture_id}...")
                odds = await client.get_match_odds(fixture_id)
                if odds:
                    print(f"✅ Success! Found odds from {len(odds)} bookmakers")
                else:
                    print("ℹ️  No odds available (this might be normal for some fixtures)")
                
                # Get predictions
                print(f"\n🔮 Test 5: Testing predictions for fixture {fixture_id}...")
                predictions = await client.get_predictions(fixture_id)
                if predictions:
                    print("✅ Predictions retrieved successfully")
                else:
                    print("ℹ️  No predictions available (this might be normal for some fixtures)")
                
                # Get live odds
                print(f"\n📊 Test 6: Testing live odds for fixture {fixture_id}...")
                live_odds = await client.get_live_odds(fixture_id)
                if live_odds:
                    print(f"✅ Success! Found live odds from {len(live_odds)} bookmakers")
                else:
                    print("ℹ️  No live odds available (this might be normal for some fixtures)")
            else:
                print("❌ Could not extract fixture ID from first match")
        
        # Test 4: Test team form (if we have team IDs)
        if matches and len(matches) > 0:
            first_match = matches[0]
            teams = first_match.get('teams', {})
            home_team_id = teams.get('home', {}).get('id')
            away_team_id = teams.get('away', {}).get('id')
            
            if home_team_id:
                print(f"\n🏆 Test 7: Testing team form for team {home_team_id}...")
                form = await client.get_team_form(home_team_id, limit=3)
                if form:
                    print(f"✅ Success! Found {len(form)} recent matches")
                else:
                    print("ℹ️  No team form data available")
        
        print("\n" + "=" * 50)
        print("🎯 API-Football Integration Test Complete!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    # Check if API key is configured
    if not hasattr(config, 'API_FOOTBALL_API_KEY') or not config.API_FOOTBALL_API_KEY:
        print("❌ Error: API_FOOTBALL_API_KEY not configured in config.py")
        print("Please add your API-Football API key to config.py")
        sys.exit(1)
    
    print(f"🔑 Using API key: {config.API_FOOTBALL_API_KEY[:10]}...")
    print(f"🌍 Timezone: {getattr(config, 'API_FOOTBALL_TIMEZONE', 'Asia/Karachi')}")
    
    # Run the test
    asyncio.run(test_api_football())
