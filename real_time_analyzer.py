#!/usr/bin/env python3
"""
Real-Time Football Betting Analyzer
Fetches live data from Sportmonks API and provides real-time analysis
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

from api.sportmonks_client import SportmonksClient
from betting.value_bet_analyzer import ValueBetAnalyzer
from betting.risk_manager import AdvancedRiskManager
from bot_interface.telegram_bot import TelegramBetBot
import config

class RealTimeAnalyzer:
    """
    Real-time football betting analyzer using live Sportmonks data
    """
    
    def __init__(self):
        self.sportmonks = SportmonksClient()
        self.value_analyzer = ValueBetAnalyzer()
        self.risk_manager = AdvancedRiskManager()
        self.telegram_bot = TelegramBetBot()
        
        # Cache for market IDs to avoid repeated API calls
        self.market_cache = {}
        self.last_update = None
        
        print("🚀 Real-Time Analyzer initialized")
    
    async def start_real_time_monitoring(self):
        """Start continuous real-time monitoring"""
        print("\n🔴 LIVE: Starting real-time football betting monitor")
        print("=" * 60)
        
        try:
            # Initialize Telegram bot
            await self.telegram_bot.start()
            print("✅ Telegram bot ready for live updates")
        except Exception as e:
            print(f"⚠️ Telegram bot failed to start: {e}")
            print("📱 Continuing in console-only mode")
        
        # Load market cache
        await self.load_market_cache()
        
        # Start monitoring loop
        while True:
            try:
                await self.perform_real_time_scan()
                print(f"\n⏰ Next scan in 5 minutes...")
                await asyncio.sleep(300)  # Scan every 5 minutes
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping real-time monitoring...")
                break
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                print("🔄 Continuing in 30 seconds...")
                await asyncio.sleep(30)
    
    async def perform_real_time_scan(self):
        """Perform a complete real-time analysis scan"""
        scan_time = datetime.now().strftime("%H:%M:%S")
        print(f"\n🔍 LIVE SCAN at {scan_time}")
        print("-" * 40)
        
        # Step 1: Get today's live fixtures
        live_fixtures = await self.get_live_fixtures()
        if not live_fixtures:
            print("📭 No live fixtures found")
            return
        
        # Step 2: Analyze each fixture for opportunities
        total_opportunities = 0
        high_value_bets = []
        
        for fixture in live_fixtures[:10]:  # Limit to 10 fixtures for performance
            opportunities = await self.analyze_fixture_real_time(fixture)
            if opportunities:
                total_opportunities += len(opportunities)
                high_value_bets.extend(opportunities)
        
        # Step 3: Generate and send real-time summary
        if high_value_bets:
            await self.send_real_time_summary(high_value_bets, scan_time)
        
        print(f"✅ Scan complete: {total_opportunities} opportunities found")
    
    async def get_live_fixtures(self) -> List[Dict]:
        """Get live fixtures with real-time data"""
        print("📡 Fetching live fixtures...")
        
        # Get today's fixtures
        today_fixtures = self.sportmonks.get_today_matches()
        
        if not today_fixtures:
            # Try tomorrow's early fixtures
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            tomorrow_fixtures = self.sportmonks.get_fixtures_by_date(tomorrow)
            today_fixtures.extend(tomorrow_fixtures[:5])  # Add first 5 tomorrow fixtures
        
        # Filter for live and upcoming fixtures
        live_fixtures = []
        for fixture in today_fixtures:
            status = fixture['fixture']['status']['short']
            if status in ['NS', '1H', '2H', 'HT', 'LIVE']:  # Not started, live, or halftime
                live_fixtures.append(fixture)
        
        print(f"🎮 Found {len(live_fixtures)} live/upcoming fixtures")
        return live_fixtures
    
    async def analyze_fixture_real_time(self, fixture: Dict) -> List[Dict]:
        """Analyze a single fixture for real-time betting opportunities"""
        fixture_id = fixture['fixture']['id']
        home_team = fixture['teams']['home']['name']
        away_team = fixture['teams']['away']['name']
        
        print(f"\n⚽ Analyzing: {home_team} vs {away_team}")
        
        opportunities = []
        
        try:
            # Get real-time odds
            odds_data = self.sportmonks.get_match_odds(fixture_id)
            
            # Get xG data if available
            xg_data = self.sportmonks.get_fixture_xg_data(fixture_id)
            
            # Get live statistics
            stats = self.sportmonks.get_fixture_statistics(fixture_id)
            
            # Get SportMonks predictions
            predictions = self.sportmonks.get_sportmonks_predictions(fixture_id)
            
            # Get SportMonks value bets
            value_bets = self.sportmonks.get_value_bets(fixture_id)
            
            # Analyze for opportunities
            if odds_data:
                fixture_opportunities = await self.find_value_opportunities(
                    fixture, odds_data, xg_data, stats, predictions, value_bets
                )
                opportunities.extend(fixture_opportunities)
            
            if opportunities:
                print(f"💎 Found {len(opportunities)} opportunities")
            else:
                print("📊 No significant opportunities")
                
        except Exception as e:
            print(f"❌ Error analyzing fixture {fixture_id}: {e}")
        
        return opportunities
    
    async def find_value_opportunities(self, fixture: Dict, odds_data: List[Dict], 
                                     xg_data: Dict, stats: Dict, predictions: Dict, 
                                     value_bets: List[Dict]) -> List[Dict]:
        """Find value betting opportunities from real-time data"""
        opportunities = []
        
        # Use SportMonks value bets if available
        if value_bets:
            for vb in value_bets:
                opportunity = {
                    'type': 'sportmonks_value_bet',
                    'fixture': fixture,
                    'market': vb.get('market', 'Unknown'),
                    'selection': vb.get('selection', 'Unknown'),
                    'odds': vb.get('odds', 0),
                    'probability': vb.get('probability', 0),
                    'edge': vb.get('edge', 0),
                    'confidence': vb.get('confidence', 0.8),
                    'source': 'SportMonks AI',
                    'timestamp': datetime.now().isoformat()
                }
                opportunities.append(opportunity)
        
        # Analyze xG opportunities
        if xg_data and odds_data:
            xg_opportunities = self.analyze_xg_opportunities(fixture, xg_data, odds_data)
            opportunities.extend(xg_opportunities)
        
        # Analyze statistical opportunities
        if stats and odds_data:
            stat_opportunities = self.analyze_statistical_opportunities(fixture, stats, odds_data)
            opportunities.extend(stat_opportunities)
        
        # Use SportMonks predictions for additional insights
        if predictions:
            pred_opportunities = self.analyze_prediction_opportunities(fixture, predictions, odds_data)
            opportunities.extend(pred_opportunities)
        
        return opportunities
    
    def analyze_xg_opportunities(self, fixture: Dict, xg_data: Dict, odds_data: List[Dict]) -> List[Dict]:
        """Analyze xG-based opportunities"""
        opportunities = []
        
        home_xg = xg_data.get('home_xg', 0)
        away_xg = xg_data.get('away_xg', 0)
        total_xg = home_xg + away_xg
        
        # Over/Under goals analysis
        if total_xg > 0:
            # Simple xG model: if total xG suggests over 2.5, look for over bets
            if total_xg >= 2.8:  # High xG total
                for odd in odds_data:
                    market_name = odd.get('market', {}).get('name', '').lower()
                    if 'over' in market_name and '2.5' in market_name:
                        odds_value = odd.get('odds', {}).get('value', 0)
                        if odds_value > 1.5:  # Reasonable odds
                            # Calculate implied probability vs xG probability
                            implied_prob = 1 / odds_value if odds_value > 0 else 0
                            xg_prob = min(0.9, total_xg / 3.5)  # Simplified xG to probability
                            
                            if xg_prob > implied_prob + 0.05:  # 5% edge minimum
                                opportunities.append({
                                    'type': 'xg_over_under',
                                    'fixture': fixture,
                                    'market': 'Over 2.5 Goals',
                                    'selection': 'Over 2.5',
                                    'odds': odds_value,
                                    'xg_total': total_xg,
                                    'xg_probability': xg_prob,
                                    'implied_probability': implied_prob,
                                    'edge': xg_prob - implied_prob,
                                    'confidence': 0.7,
                                    'source': 'xG Analysis',
                                    'timestamp': datetime.now().isoformat()
                                })
        
        return opportunities
    
    def analyze_statistical_opportunities(self, fixture: Dict, stats: Dict, odds_data: List[Dict]) -> List[Dict]:
        """Analyze statistics-based opportunities"""
        opportunities = []
        
        home_stats = stats.get('home', {})
        away_stats = stats.get('away', {})
        
        # Corner analysis
        home_corners = home_stats.get('corners', 0)
        away_corners = away_stats.get('corners', 0)
        total_corners = home_corners + away_corners
        
        if total_corners > 8:  # High corner count
            for odd in odds_data:
                market_name = odd.get('market', {}).get('name', '').lower()
                if 'corner' in market_name and 'over' in market_name:
                    odds_value = odd.get('odds', {}).get('value', 0)
                    if 1.5 <= odds_value <= 3.0:  # Reasonable odds range
                        opportunities.append({
                            'type': 'corners_analysis',
                            'fixture': fixture,
                            'market': 'Total Corners',
                            'selection': 'Over',
                            'odds': odds_value,
                            'current_corners': total_corners,
                            'edge': 0.06,  # Estimated edge
                            'confidence': 0.6,
                            'source': 'Live Stats',
                            'timestamp': datetime.now().isoformat()
                        })
        
        return opportunities
    
    def analyze_prediction_opportunities(self, fixture: Dict, predictions: Dict, odds_data: List[Dict]) -> List[Dict]:
        """Analyze SportMonks prediction-based opportunities"""
        opportunities = []
        
        # Extract prediction probabilities
        win_probs = predictions.get('probabilities', {})
        if win_probs:
            home_prob = win_probs.get('home', 0)
            draw_prob = win_probs.get('draw', 0)
            away_prob = win_probs.get('away', 0)
            
            # Compare with market odds
            for odd in odds_data:
                market_name = odd.get('market', {}).get('name', '').lower()
                if 'match winner' in market_name or 'result' in market_name:
                    odds_value = odd.get('odds', {}).get('value', 0)
                    label = odd.get('odds', {}).get('label', '').lower()
                    
                    implied_prob = 1 / odds_value if odds_value > 0 else 0
                    
                    if 'home' in label and home_prob > implied_prob + 0.08:
                        opportunities.append({
                            'type': 'prediction_match_result',
                            'fixture': fixture,
                            'market': 'Match Result',
                            'selection': 'Home Win',
                            'odds': odds_value,
                            'ai_probability': home_prob,
                            'implied_probability': implied_prob,
                            'edge': home_prob - implied_prob,
                            'confidence': 0.75,
                            'source': 'SportMonks AI',
                            'timestamp': datetime.now().isoformat()
                        })
        
        return opportunities
    
    async def send_real_time_summary(self, opportunities: List[Dict], scan_time: str):
        """Send real-time summary to Telegram"""
        print(f"\n📱 Sending live update to Telegram...")
        
        # Sort opportunities by edge/confidence
        sorted_opportunities = sorted(opportunities, 
                                    key=lambda x: x.get('edge', 0) * x.get('confidence', 0.5), 
                                    reverse=True)
        
        # Create summary message
        message = f"🔴 LIVE BETTING ALERT - {scan_time}\n\n"
        message += f"💎 {len(opportunities)} Value Opportunities Found\n\n"
        
        # Add top opportunities
        for i, opp in enumerate(sorted_opportunities[:5], 1):
            fixture = opp['fixture']
            home_team = fixture['teams']['home']['name']
            away_team = fixture['teams']['away']['name']
            
            message += f"{i}. {home_team} vs {away_team}\n"
            message += f"   🎯 {opp['market']} - {opp.get('selection', 'N/A')}\n"
            message += f"   💰 Odds: {opp.get('odds', 'N/A')}\n"
            message += f"   📈 Edge: {opp.get('edge', 0):.1%}\n"
            message += f"   🤖 Source: {opp.get('source', 'Analysis')}\n"
            
            if opp.get('xg_total'):
                message += f"   ⚽ xG: {opp['xg_total']:.1f}\n"
            
            message += "\n"
        
        # Add summary stats
        avg_edge = sum(opp.get('edge', 0) for opp in opportunities) / len(opportunities) if opportunities else 0
        message += f"📊 Average Edge: {avg_edge:.1%}\n"
        message += f"⏰ Next update in 5 minutes\n"
        message += f"🤖 Live analysis powered by SportMonks API"
        
        # Send to Telegram
        try:
            await self.telegram_bot.post_value_bets(opportunities)
            print("✅ Live update sent to Telegram")
        except Exception as e:
            print(f"❌ Failed to send Telegram update: {e}")
        
        # Also print to console
        print("\n" + "="*50)
        print("🔥 LIVE OPPORTUNITIES SUMMARY")
        print("="*50)
        print(message)
        print("="*50)
    
    async def load_market_cache(self):
        """Load and cache market IDs for faster lookups"""
        print("🏪 Loading betting markets cache...")
        
        try:
            markets = self.sportmonks.get_markets_list()
            for market in markets:
                name = market.get('name', '').lower()
                self.market_cache[name] = market.get('id')
            
            print(f"✅ Cached {len(self.market_cache)} markets")
            
            # Cache important market searches
            important_markets = ['btts', 'corners', 'match winner', 'over under']
            for market_name in important_markets:
                results = self.sportmonks.search_market_by_name(market_name)
                print(f"🔍 Found {len(results)} results for '{market_name}'")
                
        except Exception as e:
            print(f"⚠️ Failed to load market cache: {e}")
    
    def get_market_id(self, market_name: str) -> Optional[int]:
        """Get market ID from cache"""
        return self.market_cache.get(market_name.lower())

async def main():
    """Main function to run real-time analyzer"""
    print("🚀 Starting Real-Time Football Betting Analyzer")
    print("Using live data from SportMonks API")
    print("=" * 60)
    
    analyzer = RealTimeAnalyzer()
    
    try:
        await analyzer.start_real_time_monitoring()
    except KeyboardInterrupt:
        print("\n👋 Real-time analyzer stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")

if __name__ == "__main__":
    asyncio.run(main())