#!/usr/bin/env python3
"""
Demo Real-Time Football Betting System
Simulates live betting analysis with mock data to demonstrate functionality
"""

import asyncio
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from bot_interface.telegram_bot import TelegramBetBot
import config

class DemoRealTimeSystem:
    """
    Demo system showing real-time football betting analysis
    Uses simulated data to demonstrate live capabilities
    """
    
    def __init__(self):
        self.telegram_bot = TelegramBetBot()
        self.demo_fixtures = self.generate_demo_fixtures()
        self.scan_count = 0
        
        print("🎭 Demo Real-Time System initialized")
        print("📊 This demonstrates how the live system would work with real data")
    
    async def start_demo_monitoring(self):
        """Start demo real-time monitoring"""
        print("\n🔴 DEMO: Real-Time Football Betting Monitor")
        print("=" * 60)
        print("📱 Simulating live data from SportMonks API")
        print("🎯 Demonstrating real-time betting opportunities")
        print()
        
        try:
            # Initialize Telegram bot
            await self.telegram_bot.start()
            print("✅ Telegram bot ready for demo updates")
        except Exception as e:
            print(f"⚠️ Telegram bot demo mode (no real messages): {e}")
        
        # Start demo monitoring loop
        for scan_num in range(5):  # Run 5 demo scans
            try:
                await self.perform_demo_scan(scan_num + 1)
                if scan_num < 4:  # Don't wait after last scan
                    print(f"\n⏰ Next demo scan in 30 seconds...")
                    await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping demo monitoring...")
                break
            except Exception as e:
                print(f"❌ Demo error: {e}")
        
        print("\n🎉 Demo completed! This shows how the real system works with live data.")
    
    async def perform_demo_scan(self, scan_number: int):
        """Perform a demo real-time analysis scan"""
        scan_time = datetime.now().strftime("%H:%M:%S")
        print(f"\n🔍 DEMO SCAN #{scan_number} at {scan_time}")
        print("-" * 40)
        
        # Simulate getting live fixtures
        live_fixtures = self.get_demo_live_fixtures()
        print(f"📡 Simulated API call: Found {len(live_fixtures)} live fixtures")
        
        # Analyze each fixture for opportunities
        all_opportunities = []
        
        for i, fixture in enumerate(live_fixtures, 1):
            print(f"\n⚽ Analyzing fixture {i}: {fixture['teams']['home']['name']} vs {fixture['teams']['away']['name']}")
            
            # Simulate real-time data fetching
            await self.simulate_api_calls(fixture['fixture']['id'])
            
            # Generate demo opportunities
            opportunities = self.generate_demo_opportunities(fixture)
            if opportunities:
                all_opportunities.extend(opportunities)
                print(f"💎 Found {len(opportunities)} value opportunities")
            else:
                print("📊 No significant opportunities")
        
        # Generate and send demo summary
        if all_opportunities:
            await self.send_demo_summary(all_opportunities, scan_time, scan_number)
        else:
            print("📭 No betting opportunities in this scan")
        
        print(f"✅ Demo scan #{scan_number} complete: {len(all_opportunities)} total opportunities")
    
    def get_demo_live_fixtures(self) -> List[Dict]:
        """Get demo live fixtures"""
        # Simulate different scenarios each scan
        num_fixtures = random.randint(3, 6)
        return random.sample(self.demo_fixtures, min(num_fixtures, len(self.demo_fixtures)))
    
    async def simulate_api_calls(self, fixture_id: int):
        """Simulate real API calls with timing"""
        api_calls = [
            "📊 Fetching live odds...",
            "⚽ Getting xG data...", 
            "📈 Retrieving live statistics...",
            "🤖 Getting AI predictions...",
            "💎 Checking value bets..."
        ]
        
        for call in api_calls:
            print(f"   {call}")
            await asyncio.sleep(0.5)  # Simulate API response time
    
    def generate_demo_opportunities(self, fixture: Dict) -> List[Dict]:
        """Generate realistic demo betting opportunities"""
        opportunities = []
        
        # Simulate different types of opportunities
        opportunity_types = [
            self.create_value_bet_opportunity,
            self.create_xg_opportunity,
            self.create_live_stats_opportunity,
            self.create_ai_prediction_opportunity
        ]
        
        # Generate 0-3 opportunities per fixture
        num_opportunities = random.randint(0, 3)
        
        for _ in range(num_opportunities):
            opp_type = random.choice(opportunity_types)
            opportunity = opp_type(fixture)
            if opportunity:
                opportunities.append(opportunity)
        
        return opportunities
    
    def create_value_bet_opportunity(self, fixture: Dict) -> Optional[Dict]:
        """Create a SportMonks value bet opportunity"""
        markets = ["Match Result", "Over 2.5 Goals", "Both Teams Score", "Total Corners"]
        market = random.choice(markets)
        
        # Generate realistic values
        odds = round(random.uniform(1.6, 4.5), 2)
        edge = round(random.uniform(0.05, 0.15), 3)
        confidence = round(random.uniform(0.65, 0.85), 2)
        
        selections = {
            "Match Result": ["Home Win", "Draw", "Away Win"],
            "Over 2.5 Goals": ["Over 2.5", "Under 2.5"],
            "Both Teams Score": ["Yes", "No"],
            "Total Corners": ["Over 9.5", "Under 9.5"]
        }
        
        return {
            'type': 'sportmonks_value_bet',
            'fixture': fixture,
            'market': market,
            'selection': random.choice(selections[market]),
            'odds': odds,
            'edge': edge,
            'confidence': confidence,
            'source': 'SportMonks AI',
            'timestamp': datetime.now().isoformat(),
            'expected_roi': round(edge * 100, 1)
        }
    
    def create_xg_opportunity(self, fixture: Dict) -> Optional[Dict]:
        """Create an xG-based opportunity"""
        home_xg = round(random.uniform(0.8, 2.5), 1)
        away_xg = round(random.uniform(0.8, 2.5), 1)
        total_xg = home_xg + away_xg
        
        if total_xg >= 2.3:  # High xG scenario
            odds = round(random.uniform(1.7, 2.8), 2)
            
            return {
                'type': 'xg_analysis',
                'fixture': fixture,
                'market': 'Over 2.5 Goals',
                'selection': 'Over 2.5',
                'odds': odds,
                'xg_total': total_xg,
                'home_xg': home_xg,
                'away_xg': away_xg,
                'edge': round(random.uniform(0.06, 0.12), 3),
                'confidence': 0.72,
                'source': 'xG Model',
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def create_live_stats_opportunity(self, fixture: Dict) -> Optional[Dict]:
        """Create a live statistics opportunity"""
        corner_stats = {
            'home_corners': random.randint(2, 8),
            'away_corners': random.randint(2, 8),
            'minutes_played': random.randint(15, 75)
        }
        
        total_corners = corner_stats['home_corners'] + corner_stats['away_corners']
        
        if total_corners >= 6 and corner_stats['minutes_played'] < 60:
            return {
                'type': 'live_statistics',
                'fixture': fixture,
                'market': 'Total Corners',
                'selection': 'Over 10.5',
                'odds': round(random.uniform(1.8, 3.2), 2),
                'current_corners': total_corners,
                'minutes_played': corner_stats['minutes_played'],
                'edge': round(random.uniform(0.04, 0.09), 3),
                'confidence': 0.68,
                'source': 'Live Stats',
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def create_ai_prediction_opportunity(self, fixture: Dict) -> Optional[Dict]:
        """Create an AI prediction opportunity"""
        predictions = {
            'home_win': round(random.uniform(0.2, 0.6), 2),
            'draw': round(random.uniform(0.15, 0.35), 2),
            'away_win': round(random.uniform(0.2, 0.6), 2)
        }
        
        # Normalize probabilities
        total = sum(predictions.values())
        predictions = {k: round(v/total, 2) for k, v in predictions.items()}
        
        # Find strongest prediction
        strongest = max(predictions.items(), key=lambda x: x[1])
        
        if strongest[1] >= 0.45:  # Strong prediction
            odds = round(random.uniform(1.9, 3.5), 2)
            implied_prob = 1 / odds
            
            if predictions[strongest[0]] > implied_prob + 0.08:
                return {
                    'type': 'ai_prediction',
                    'fixture': fixture,
                    'market': 'Match Result',
                    'selection': strongest[0].replace('_', ' ').title(),
                    'odds': odds,
                    'ai_probability': predictions[strongest[0]],
                    'implied_probability': round(implied_prob, 2),
                    'edge': round(predictions[strongest[0]] - implied_prob, 3),
                    'confidence': 0.75,
                    'source': 'AI Predictions',
                    'timestamp': datetime.now().isoformat()
                }
        
        return None
    
    async def send_demo_summary(self, opportunities: List[Dict], scan_time: str, scan_number: int):
        """Send demo summary"""
        print(f"\n📱 Demo: Sending live update summary...")
        
        # Sort by edge * confidence
        sorted_opportunities = sorted(opportunities, 
                                    key=lambda x: x.get('edge', 0) * x.get('confidence', 0.5), 
                                    reverse=True)
        
        # Create demo message
        message = f"🔴 DEMO LIVE ALERT #{scan_number} - {scan_time}\n\n"
        message += f"💎 {len(opportunities)} Value Opportunities Found\n\n"
        
        # Add top opportunities
        for i, opp in enumerate(sorted_opportunities[:4], 1):
            fixture = opp['fixture']
            home_team = fixture['teams']['home']['name']
            away_team = fixture['teams']['away']['name']
            
            message += f"{i}. {home_team} vs {away_team}\n"
            message += f"   🎯 {opp['market']} - {opp.get('selection', 'N/A')}\n"
            message += f"   💰 Odds: {opp.get('odds', 'N/A')}\n"
            message += f"   📈 Edge: {opp.get('edge', 0):.1%}\n"
            message += f"   🤖 Source: {opp.get('source', 'Analysis')}\n"
            
            # Add specific data based on type
            if opp.get('xg_total'):
                message += f"   ⚽ Total xG: {opp['xg_total']}\n"
            elif opp.get('current_corners'):
                message += f"   🔄 Current corners: {opp['current_corners']}\n"
            elif opp.get('ai_probability'):
                message += f"   🧠 AI confidence: {opp['ai_probability']:.1%}\n"
            
            message += "\n"
        
        # Add summary stats
        avg_edge = sum(opp.get('edge', 0) for opp in opportunities) / len(opportunities)
        total_potential_roi = sum(opp.get('expected_roi', 0) for opp in opportunities if opp.get('expected_roi'))
        
        message += f"📊 Average Edge: {avg_edge:.1%}\n"
        message += f"💰 Potential ROI: {total_potential_roi:.1f}%\n"
        message += f"🎭 DEMO: Real system would send to Telegram\n"
        message += f"🔄 Next scan in 30 seconds"
        
        # Display demo summary
        print("\n" + "="*60)
        print("🔥 DEMO LIVE OPPORTUNITIES SUMMARY")
        print("="*60)
        print(message)
        print("="*60)
        
        # Simulate some betting recommendations
        self.show_demo_recommendations(sorted_opportunities[:3])
    
    def show_demo_recommendations(self, top_opportunities: List[Dict]):
        """Show demo betting recommendations"""
        if not top_opportunities:
            return
        
        print("\n🎯 DEMO BETTING RECOMMENDATIONS")
        print("-" * 40)
        
        for i, opp in enumerate(top_opportunities, 1):
            print(f"\n{i}. RECOMMENDED BET:")
            print(f"   Match: {opp['fixture']['teams']['home']['name']} vs {opp['fixture']['teams']['away']['name']}")
            print(f"   Market: {opp['market']}")
            print(f"   Selection: {opp['selection']}")
            print(f"   Odds: {opp['odds']}")
            print(f"   Edge: {opp['edge']:.1%}")
            print(f"   Risk Level: {'Low' if opp['confidence'] > 0.75 else 'Medium' if opp['confidence'] > 0.65 else 'High'}")
            
            # Kelly Criterion demo
            kelly_percentage = opp['edge'] / (opp['odds'] - 1) if opp['odds'] > 1 else 0
            recommended_stake = min(kelly_percentage * 100, 5)  # Max 5%
            
            print(f"   Kelly %: {kelly_percentage:.1%}")
            print(f"   Recommended Stake: {recommended_stake:.1f}% of bankroll")
            print(f"   Data Source: {opp['source']}")
    
    def generate_demo_fixtures(self) -> List[Dict]:
        """Generate realistic demo fixtures"""
        teams = [
            ("Manchester City", "Liverpool"), ("Arsenal", "Chelsea"),
            ("Barcelona", "Real Madrid"), ("Bayern Munich", "Borussia Dortmund"),
            ("PSG", "Marseille"), ("Juventus", "AC Milan"),
            ("Inter Milan", "Napoli"), ("Atletico Madrid", "Sevilla"),
            ("Ajax", "PSV"), ("Porto", "Benfica")
        ]
        
        fixtures = []
        for i, (home, away) in enumerate(teams):
            fixture = {
                'fixture': {
                    'id': 1000000 + i,
                    'date': (datetime.now() + timedelta(hours=random.randint(1, 24))).isoformat(),
                    'status': {
                        'short': random.choice(['NS', '1H', 'HT', '2H']),
                        'long': 'In Progress'
                    }
                },
                'teams': {
                    'home': {'id': 100 + i*2, 'name': home},
                    'away': {'id': 101 + i*2, 'name': away}
                },
                'league': {
                    'name': random.choice(['Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1'])
                }
            }
            fixtures.append(fixture)
        
        return fixtures

async def main():
    """Run the demo real-time system"""
    print("🎭 Starting Demo Real-Time Football Betting System")
    print("=" * 60)
    print("📊 This demonstrates live betting analysis capabilities")
    print("🔄 Using simulated data to show real-time functionality")
    print("💡 In production, this would use live SportMonks API data")
    print()
    
    demo_system = DemoRealTimeSystem()
    
    try:
        await demo_system.start_demo_monitoring()
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    
    print("\n🎉 Demo Complete!")
    print("💡 This shows exactly how the real system works with live data")
    print("🚀 Ready to deploy with real SportMonks API when subscription upgraded")

if __name__ == "__main__":
    asyncio.run(main())