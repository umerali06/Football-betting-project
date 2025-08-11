#!/usr/bin/env python3
"""
Real-Time Sportmonks Endpoints Test
Tests all real-time endpoints with live data validation
"""

import asyncio
import time
from datetime import datetime, timedelta
from api.sportmonks_client import SportmonksClient
import json

class RealTimeEndpointTester:
    """Test all real-time Sportmonks endpoints"""
    
    def __init__(self):
        self.client = SportmonksClient()
        self.test_results = {}
        
    async def run_comprehensive_test(self):
        """Run comprehensive test of all real-time endpoints"""
        print("🚀 COMPREHENSIVE REAL-TIME ENDPOINT TEST")
        print("=" * 60)
        print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test all endpoints
        await self.test_today_fixtures()
        await self.test_fixtures_by_date()
        await self.test_odds_endpoints()
        await self.test_team_form()
        await self.test_xg_data()
        await self.test_statistics()
        await self.test_markets()
        await self.test_predictions()
        
        # Show final summary
        self.show_test_summary()
    
    async def test_today_fixtures(self):
        """Test today's fixtures endpoint"""
        print("📅 Testing Today's Fixtures")
        print("-" * 30)
        
        try:
            fixtures = self.client.get_today_matches()
            
            if fixtures:
                print(f"✅ SUCCESS: Found {len(fixtures)} fixtures")
                
                # Show first fixture details
                first_fixture = fixtures[0]
                print(f"📋 Sample Fixture:")
                print(f"   ID: {first_fixture['fixture']['id']}")
                print(f"   Teams: {first_fixture['teams']['home']['name']} vs {first_fixture['teams']['away']['name']}")
                print(f"   Status: {first_fixture['fixture']['status']['short']}")
                print(f"   Date: {first_fixture['fixture']['date']}")
                
                if first_fixture.get('league'):
                    print(f"   League: {first_fixture['league']['name']}")
                
                self.test_results['today_fixtures'] = 'PASS'
                return fixtures[0]['fixture']['id']  # Return fixture ID for further tests
            else:
                print("⚠️ No fixtures found for today - trying tomorrow")
                tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                tomorrow_fixtures = self.client.get_fixtures_by_date(tomorrow)
                
                if tomorrow_fixtures:
                    print(f"✅ Found {len(tomorrow_fixtures)} fixtures for tomorrow")
                    self.test_results['today_fixtures'] = 'PASS'
                    return tomorrow_fixtures[0]['fixture']['id']
                else:
                    print("❌ No fixtures found")
                    self.test_results['today_fixtures'] = 'FAIL'
                    return None
                    
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.test_results['today_fixtures'] = 'ERROR'
            return None
    
    async def test_fixtures_by_date(self):
        """Test fixtures by specific date"""
        print("\n📅 Testing Fixtures by Date")
        print("-" * 30)
        
        try:
            # Test with tomorrow's date
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            fixtures = self.client.get_fixtures_by_date(tomorrow)
            
            print(f"✅ Found {len(fixtures)} fixtures for {tomorrow}")
            self.test_results['fixtures_by_date'] = 'PASS'
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.test_results['fixtures_by_date'] = 'ERROR'
    
    async def test_odds_endpoints(self):
        """Test odds-related endpoints"""
        print("\n💰 Testing Odds Endpoints")
        print("-" * 30)
        
        # Get a fixture ID first
        fixtures = self.client.get_today_matches()
        if not fixtures:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            fixtures = self.client.get_fixtures_by_date(tomorrow)
        
        if fixtures:
            fixture_id = fixtures[0]['fixture']['id']
            print(f"🎯 Testing with fixture ID: {fixture_id}")
            
            # Test match odds
            try:
                odds = self.client.get_match_odds(fixture_id)
                print(f"📊 Match Odds: Found {len(odds)} odds entries")
                
                if odds:
                    sample_odd = odds[0]
                    print(f"   Sample: {sample_odd.get('bookmaker', {}).get('name', 'Unknown')} - {sample_odd.get('market', {}).get('name', 'Unknown')}")
                    print(f"   Value: {sample_odd.get('odds', {}).get('value', 'N/A')}")
                
                self.test_results['match_odds'] = 'PASS'
                
            except Exception as e:
                print(f"❌ Match Odds Error: {e}")
                self.test_results['match_odds'] = 'ERROR'
            
            # Test latest odds updates
            try:
                latest_odds = self.client.get_latest_odds_updates()
                print(f"🔄 Latest Odds Updates: Found {len(latest_odds)} updates")
                self.test_results['latest_odds'] = 'PASS'
                
            except Exception as e:
                print(f"❌ Latest Odds Error: {e}")
                self.test_results['latest_odds'] = 'ERROR'
        else:
            print("❌ No fixtures available for odds testing")
            self.test_results['match_odds'] = 'SKIP'
            self.test_results['latest_odds'] = 'SKIP'
    
    async def test_team_form(self):
        """Test team form endpoint"""
        print("\n📈 Testing Team Form")
        print("-" * 30)
        
        # Get a team ID from fixtures
        fixtures = self.client.get_today_matches()
        if not fixtures:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            fixtures = self.client.get_fixtures_by_date(tomorrow)
        
        if fixtures:
            team_id = fixtures[0]['teams']['home']['id']
            team_name = fixtures[0]['teams']['home']['name']
            
            print(f"🏆 Testing with team: {team_name} (ID: {team_id})")
            
            try:
                form = self.client.get_team_form(team_id, 5)
                print(f"✅ Found form data: {len(form)} recent matches")
                
                if form:
                    recent_match = form[0]
                    print(f"   Most recent: {recent_match.get('teams', {}).get('home', {}).get('name', 'Unknown')} vs {recent_match.get('teams', {}).get('away', {}).get('name', 'Unknown')}")
                    print(f"   Score: {recent_match.get('goals', {}).get('home', 'N/A')}-{recent_match.get('goals', {}).get('away', 'N/A')}")
                
                self.test_results['team_form'] = 'PASS'
                
            except Exception as e:
                print(f"❌ ERROR: {e}")
                self.test_results['team_form'] = 'ERROR'
        else:
            print("❌ No fixtures available for team form testing")
            self.test_results['team_form'] = 'SKIP'
    
    async def test_xg_data(self):
        """Test xG data endpoint"""
        print("\n⚽ Testing xG Data")
        print("-" * 30)
        
        fixtures = self.client.get_today_matches()
        if not fixtures:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            fixtures = self.client.get_fixtures_by_date(tomorrow)
        
        if fixtures:
            fixture_id = fixtures[0]['fixture']['id']
            
            try:
                xg_data = self.client.get_fixture_xg_data(fixture_id)
                
                if xg_data:
                    print(f"✅ xG Data Available:")
                    print(f"   Home xG: {xg_data.get('home_xg', 'N/A')}")
                    print(f"   Away xG: {xg_data.get('away_xg', 'N/A')}")
                    print(f"   Total xG: {xg_data.get('total_xg', 'N/A')}")
                    self.test_results['xg_data'] = 'PASS'
                else:
                    print("⚠️ No xG data available for this fixture")
                    self.test_results['xg_data'] = 'NO_DATA'
                    
            except Exception as e:
                print(f"❌ ERROR: {e}")
                self.test_results['xg_data'] = 'ERROR'
        else:
            print("❌ No fixtures available for xG testing")
            self.test_results['xg_data'] = 'SKIP'
    
    async def test_statistics(self):
        """Test statistics endpoint"""
        print("\n📊 Testing Match Statistics")
        print("-" * 30)
        
        fixtures = self.client.get_today_matches()
        if not fixtures:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            fixtures = self.client.get_fixtures_by_date(tomorrow)
        
        if fixtures:
            fixture_id = fixtures[0]['fixture']['id']
            
            try:
                stats = self.client.get_fixture_statistics(fixture_id)
                
                if stats:
                    home_stats = stats.get('home', {})
                    away_stats = stats.get('away', {})
                    
                    print(f"✅ Statistics Available:")
                    print(f"   Home team stats: {len(home_stats)} categories")
                    print(f"   Away team stats: {len(away_stats)} categories")
                    
                    # Show some sample stats
                    if home_stats:
                        sample_stats = list(home_stats.items())[:3]
                        print(f"   Sample stats: {sample_stats}")
                    
                    self.test_results['statistics'] = 'PASS'
                else:
                    print("⚠️ No statistics available for this fixture")
                    self.test_results['statistics'] = 'NO_DATA'
                    
            except Exception as e:
                print(f"❌ ERROR: {e}")
                self.test_results['statistics'] = 'ERROR'
        else:
            print("❌ No fixtures available for statistics testing")
            self.test_results['statistics'] = 'SKIP'
    
    async def test_markets(self):
        """Test markets endpoints"""
        print("\n🏪 Testing Betting Markets")
        print("-" * 30)
        
        try:
            # Test markets list
            markets = self.client.get_markets_list()
            print(f"📊 Available Markets: {len(markets)}")
            
            if markets:
                # Show first few markets
                for i, market in enumerate(markets[:5], 1):
                    print(f"   {i}. {market.get('name', 'Unknown')} (ID: {market.get('id', 'N/A')})")
            
            self.test_results['markets_list'] = 'PASS'
            
        except Exception as e:
            print(f"❌ Markets List Error: {e}")
            self.test_results['markets_list'] = 'ERROR'
        
        try:
            # Test market search
            search_terms = ['btts', 'match winner', 'corners']
            for term in search_terms:
                results = self.client.search_market_by_name(term)
                print(f"🔍 Search '{term}': {len(results)} results")
            
            self.test_results['market_search'] = 'PASS'
            
        except Exception as e:
            print(f"❌ Market Search Error: {e}")
            self.test_results['market_search'] = 'ERROR'
    
    async def test_predictions(self):
        """Test predictions endpoints"""
        print("\n🤖 Testing AI Predictions")
        print("-" * 30)
        
        fixtures = self.client.get_today_matches()
        if not fixtures:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            fixtures = self.client.get_fixtures_by_date(tomorrow)
        
        if fixtures:
            fixture_id = fixtures[0]['fixture']['id']
            
            # Test predictions
            try:
                predictions = self.client.get_sportmonks_predictions(fixture_id)
                
                if predictions:
                    print(f"✅ AI Predictions Available")
                    print(f"   Data keys: {list(predictions.keys())}")
                    
                    if 'probabilities' in predictions:
                        probs = predictions['probabilities']
                        print(f"   Win Probabilities: Home={probs.get('home', 'N/A')}, Draw={probs.get('draw', 'N/A')}, Away={probs.get('away', 'N/A')}")
                    
                    self.test_results['predictions'] = 'PASS'
                else:
                    print("⚠️ No predictions available for this fixture")
                    self.test_results['predictions'] = 'NO_DATA'
                    
            except Exception as e:
                print(f"❌ Predictions Error: {e}")
                self.test_results['predictions'] = 'ERROR'
            
            # Test value bets
            try:
                value_bets = self.client.get_value_bets(fixture_id)
                
                if value_bets:
                    print(f"✅ Value Bets Available: {len(value_bets)} recommendations")
                    
                    # Show first value bet
                    if value_bets:
                        vb = value_bets[0]
                        print(f"   Sample: {vb.get('market', 'Unknown')} - {vb.get('selection', 'Unknown')}")
                        print(f"   Edge: {vb.get('edge', 'N/A')}, Odds: {vb.get('odds', 'N/A')}")
                    
                    self.test_results['value_bets'] = 'PASS'
                else:
                    print("⚠️ No value bets available for this fixture")
                    self.test_results['value_bets'] = 'NO_DATA'
                    
            except Exception as e:
                print(f"❌ Value Bets Error: {e}")
                self.test_results['value_bets'] = 'ERROR'
        else:
            print("❌ No fixtures available for predictions testing")
            self.test_results['predictions'] = 'SKIP'
            self.test_results['value_bets'] = 'SKIP'
    
    def show_test_summary(self):
        """Show comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result == 'PASS')
        failed_tests = sum(1 for result in self.test_results.values() if result in ['FAIL', 'ERROR'])
        skipped_tests = sum(1 for result in self.test_results.values() if result in ['SKIP', 'NO_DATA'])
        
        print(f"📊 Test Results: {passed_tests}/{total_tests} passed")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Skipped/No Data: {skipped_tests}")
        print()
        
        # Detailed results
        print("📋 Detailed Results:")
        for endpoint, result in self.test_results.items():
            status_emoji = {
                'PASS': '✅',
                'FAIL': '❌', 
                'ERROR': '💥',
                'SKIP': '⏭️',
                'NO_DATA': '📭'
            }.get(result, '❓')
            
            print(f"   {status_emoji} {endpoint.replace('_', ' ').title()}: {result}")
        
        print("\n" + "=" * 60)
        
        # Recommendations
        if passed_tests >= total_tests * 0.7:  # 70% pass rate
            print("🎉 EXCELLENT: Real-time integration is working well!")
            print("💡 Ready for live betting analysis")
        elif passed_tests >= total_tests * 0.5:  # 50% pass rate
            print("⚠️ PARTIAL: Some endpoints working, may have subscription limitations")
            print("💡 Consider upgrading SportMonks plan for full access")
        else:
            print("❌ ISSUES: Multiple endpoint failures detected")
            print("💡 Check API key and subscription status")
        
        print(f"\n🔗 Test API endpoints at: https://my.sportmonks.com/api/tester")
        print(f"⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

async def main():
    """Run comprehensive real-time endpoint test"""
    tester = RealTimeEndpointTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())