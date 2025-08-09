import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import config
from api.api_football import APIFootballClient
from models.elo_model import EloModel
from models.xg_model import XGModel
from models.corners_model import CornersModel
from betting.value_bet_analyzer import ValueBetAnalyzer
from betting.risk_manager import AdvancedRiskManager
from bot_interface.telegram_bot import TelegramBetBot

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('realtime_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealTimeBettingMonitor:
    """
    Real-time betting monitor that continuously checks for new matches
    and updates the bot dynamically with live data
    """
    
    def __init__(self):
        self.api_client = APIFootballClient()
        self.elo_model = EloModel()
        self.xg_model = XGModel()
        self.corners_model = CornersModel()
        self.value_analyzer = ValueBetAnalyzer()
        self.risk_manager = AdvancedRiskManager()
        self.telegram_bot = TelegramBetBot()
        
        # Track analyzed matches to avoid duplicates
        self.analyzed_matches = set()
        self.last_check_time = None
        self.check_interval = 300  # Check every 5 minutes
        self.is_running = False
        
    async def start(self):
        """Start the real-time monitoring system"""
        logger.info("🚀 Starting Real-Time Betting Monitor...")
        
        try:
            # Start Telegram bot
            await self.telegram_bot.start()
            logger.info("✅ Telegram bot started successfully")
            logger.info("💬 Send /setchat to your bot in Telegram to set up notifications")
            
            # Send startup message
            await self.telegram_bot.post_startup_message()
            
            self.is_running = True
            
            # Start continuous monitoring
            await self.monitor_loop()
            
        except Exception as e:
            logger.error(f"❌ Failed to start real-time monitor: {e}")
            await self.telegram_bot.post_error_message(f"Real-time monitor failed to start: {str(e)}")
    
    async def monitor_loop(self):
        """Main monitoring loop that runs continuously"""
        logger.info("🔄 Starting real-time monitoring loop...")
        
        while self.is_running:
            try:
                current_time = datetime.now()
                logger.info(f"⏰ Checking for new matches at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Check for new matches
                await self.check_for_new_matches()
                
                # Wait for next check
                logger.info(f"⏳ Waiting {self.check_interval} seconds until next check...")
                await asyncio.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Real-time monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await self.telegram_bot.post_error_message(f"Monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def check_for_new_matches(self):
        """Check for new matches and analyze them"""
        try:
            # Get current matches
            matches = self.api_client.get_today_matches(days_ahead=3)
            
            if not matches:
                logger.info("📭 No matches available at the moment")
                await self.telegram_bot.post_no_matches_message()
                return
            
            logger.info(f"✅ Found {len(matches)} matches to analyze")
            
            # Filter for new matches only
            new_matches = []
            for match in matches:
                fixture_id = match['fixture']['id']
                if fixture_id not in self.analyzed_matches:
                    new_matches.append(match)
                    self.analyzed_matches.add(fixture_id)
            
            if not new_matches:
                logger.info("📋 No new matches to analyze")
                return
            
            logger.info(f"🆕 Found {len(new_matches)} new matches to analyze")
            
            # Analyze new matches
            total_value_bets = []
            for i, match in enumerate(new_matches):
                logger.info(f"🔍 Analyzing new match {i+1}/{len(new_matches)}: {match['teams']['home']['name']} vs {match['teams']['away']['name']}")
                
                value_bets = await self.analyze_match(match)
                if value_bets:
                    total_value_bets.extend(value_bets)
                    logger.info(f"💎 Found {len(value_bets)} value bets for this match")
            
            # Post value bets if found
            if total_value_bets:
                await self.telegram_bot.post_value_bets(total_value_bets)
                logger.info(f"📤 Posted {len(total_value_bets)} value bets to Telegram")
                
                # Post real-time summary
                await self.post_realtime_summary(len(new_matches), len(total_value_bets))
            else:
                logger.info("📭 No value bets found in new matches")
                
        except Exception as e:
            logger.error(f"❌ Error checking for new matches: {e}")
            await self.telegram_bot.post_error_message(f"Error checking matches: {str(e)}")
    
    async def analyze_match(self, match_data: Dict) -> List[Dict]:
        """Analyze a single match for value bets"""
        try:
            fixture_id = match_data['fixture']['id']
            home_team_id = match_data['teams']['home']['id']
            away_team_id = match_data['teams']['away']['id']
            
            logger.info(f"🔍 Getting real-time data for fixture {fixture_id}")
            
            # Get real-time team form data
            home_form = self.api_client.get_team_form(home_team_id, 10)
            away_form = self.api_client.get_team_form(away_team_id, 10)
            
            # Get real-time match odds
            odds_data = self.api_client.get_match_odds(fixture_id)
            
            if not odds_data:
                logger.info(f"📭 No odds available for fixture {fixture_id}")
                return []
            
            # Generate predictions using real-time data
            predictions = await self.generate_predictions(home_team_id, away_team_id, home_form, away_form)
            
            # Analyze for value bets
            value_bets = []
            
            # Match result bets
            if 'match_result' in predictions:
                match_odds = self.extract_match_odds(odds_data)
                if match_odds:
                    value_bets.extend(self.value_analyzer.analyze_match_result_bets(predictions['match_result'], match_odds))
            
            # Goals bets
            if 'goals' in predictions:
                goals_odds = self.extract_goals_odds(odds_data)
                if goals_odds:
                    value_bets.extend(self.value_analyzer.analyze_goals_bets(predictions['goals'], goals_odds))
            
            # Corners bets
            if 'corners' in predictions:
                corners_odds = self.extract_corners_odds(odds_data)
                if corners_odds:
                    value_bets.extend(self.value_analyzer.analyze_corners_bets(predictions['corners'], corners_odds))
            
            # Add match info to value bets
            for bet in value_bets:
                bet['match_info'] = {
                    'fixture_id': fixture_id,
                    'home_team': match_data['teams']['home']['name'],
                    'away_team': match_data['teams']['away']['name'],
                    'match_time': match_data['fixture']['date'],
                    'league': match_data.get('league', {}).get('name', 'Unknown League')
                }
            
            return value_bets
            
        except Exception as e:
            logger.error(f"❌ Error analyzing match {match_data.get('fixture', {}).get('id', 'unknown')}: {e}")
            return []
    
    async def generate_predictions(self, home_team_id: int, away_team_id: int,
                                 home_form: List[Dict], away_form: List[Dict]) -> Dict:
        """Generate predictions using all models with real-time data"""
        predictions = {}
        
        try:
            # Elo predictions
            home_win_prob, draw_prob, away_win_prob = self.elo_model.predict_match_result(home_team_id, away_team_id)
            predictions['match_result'] = {
                'home_win': home_win_prob,
                'draw': draw_prob,
                'away_win': away_win_prob
            }
            
            # xG predictions (only if we have form data)
            if home_form and away_form:
                home_stats = self.xg_model.calculate_team_xg(home_team_id, home_form)
                away_stats = self.xg_model.calculate_team_xg(away_team_id, away_form)
                
                home_xg, away_xg = self.xg_model.predict_match_xg(home_team_id, away_team_id, home_stats, away_stats)
                goals_predictions = self.xg_model.predict_goals_probabilities(home_xg, away_xg)
                predictions['goals'] = goals_predictions
            
            # Corners predictions (only if we have form data)
            if home_form and away_form:
                home_corner_stats = self.corners_model.calculate_team_corners(home_team_id, home_form)
                away_corner_stats = self.corners_model.calculate_team_corners(away_team_id, away_form)
                
                home_corners, away_corners = self.corners_model.predict_match_corners(home_team_id, away_team_id, home_corner_stats, away_corner_stats)
                corners_predictions = self.corners_model.predict_corners_probabilities(home_corners, away_corners)
                predictions['corners'] = corners_predictions
            
        except Exception as e:
            logger.error(f"❌ Error generating predictions: {e}")
        
        return predictions
    
    def extract_match_odds(self, odds_data: List[Dict]) -> Dict:
        """Extract match result odds from API data"""
        match_odds = {}
        
        for bookmaker in odds_data:
            if 'bookmakers' in bookmaker:
                for bm in bookmaker['bookmakers']:
                    if bm['name'] in config.BOOKMAKERS:
                        for market in bm['bets']:
                            if market['name'] == 'Match Winner':
                                for outcome in market['values']:
                                    if outcome['value'] == 'Home':
                                        match_odds['home_win'] = float(outcome['odd'])
                                    elif outcome['value'] == 'Draw':
                                        match_odds['draw'] = float(outcome['odd'])
                                    elif outcome['value'] == 'Away':
                                        match_odds['away_win'] = float(outcome['odd'])
        
        return match_odds
    
    def extract_goals_odds(self, odds_data: List[Dict]) -> Dict:
        """Extract goals-related odds from API data"""
        goals_odds = {}
        
        for bookmaker in odds_data:
            if 'bookmakers' in bookmaker:
                for bm in bookmaker['bookmakers']:
                    if bm['name'] in config.BOOKMAKERS:
                        for market in bm['bets']:
                            if market['name'] == 'Both Teams Score':
                                for outcome in market['values']:
                                    if outcome['value'] == 'Yes':
                                        goals_odds['btts_yes'] = float(outcome['odd'])
                            
                            elif market['name'] == 'Total Goals':
                                for outcome in market['values']:
                                    if 'Over' in outcome['value']:
                                        goals_odds[f"over_{outcome['value'].split()[-1]}"] = float(outcome['odd'])
                                    elif 'Under' in outcome['value']:
                                        goals_odds[f"under_{outcome['value'].split()[-1]}"] = float(outcome['odd'])
        
        return goals_odds
    
    def extract_corners_odds(self, odds_data: List[Dict]) -> Dict:
        """Extract corners odds from API data"""
        corners_odds = {}
        
        for bookmaker in odds_data:
            if 'bookmakers' in bookmaker:
                for bm in bookmaker['bookmakers']:
                    if bm['name'] in config.BOOKMAKERS:
                        for market in bm['bets']:
                            if market['name'] == 'Total Corners':
                                for outcome in market['values']:
                                    if 'Over' in outcome['value']:
                                        corners_odds[f"over_{outcome['value'].split()[-1]}"] = float(outcome['odd'])
                                    elif 'Under' in outcome['value']:
                                        corners_odds[f"under_{outcome['value'].split()[-1]}"] = float(outcome['odd'])
        
        return corners_odds
    
    async def post_realtime_summary(self, matches_analyzed: int, value_bets_found: int):
        """Post real-time summary to Telegram"""
        try:
            message = f"""
🔄 Real-Time Update

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔍 Matches Analyzed: {matches_analyzed}
💎 Value Bets Found: {value_bets_found}

✅ System is running and monitoring for new matches
🔄 Next check in {self.check_interval} seconds
            """
            
            await self.telegram_bot.bot.send_message(
                chat_id=self.telegram_bot.chat_id, 
                text=message
            )
            
        except Exception as e:
            logger.error(f"❌ Error posting real-time summary: {e}")
    
    def stop(self):
        """Stop the real-time monitor"""
        self.is_running = False
        logger.info("🛑 Real-time monitor stopped")

async def main():
    """Main function to run the real-time betting monitor"""
    print("🚀 Starting Real-Time Football Betting Monitor")
    print("This system will continuously monitor for new matches and post value bets in real-time")
    print("=" * 60)
    
    monitor = RealTimeBettingMonitor()
    
    try:
        await monitor.start()
    except KeyboardInterrupt:
        print("\n🛑 Stopping real-time monitor...")
        monitor.stop()
    except Exception as e:
        logger.error(f"❌ System error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
