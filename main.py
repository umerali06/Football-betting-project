import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import sys
import os
from typing import Dict, List, Optional, Tuple
import argparse

# Configure logging to handle UTF-8 properly on Windows
if sys.platform == "win32":
    # Force UTF-8 encoding for Windows
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    
    # Configure logging to use UTF-8
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('football_betting.log', encoding='utf-8')
        ]
    )
else:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger(__name__)

# Import our modules
import config
from api.unified_api_client import UnifiedAPIClient
from api.league_filter import LeagueFilter
from models.elo_model import EloModel
from models.xg_model import XGModel
from models.corners_model import CornersModel
from betting.value_bet_analyzer import ValueBetAnalyzer
from betting.risk_manager import AdvancedRiskManager
from models.ml_model import AdvancedMLModel
from telegram_bot import TelegramBetBot
from reports.report_generator import ReportGenerator

class FootballBettingSystem:
    """
    Main football betting system that combines all components
    """
    
    def __init__(self, demo_mode: bool = False):
        # Use UnifiedAPIClient which prioritizes API-Football and falls back to SportMonks
        self.api_client = UnifiedAPIClient()
        
        # Initialize league filter for England League 2 and up + Top European leagues
        self.league_filter = LeagueFilter()
        
        self.elo_model = EloModel()
        self.xg_model = XGModel()
        self.corners_model = CornersModel()
        self.value_analyzer = ValueBetAnalyzer()
        self.risk_manager = AdvancedRiskManager()
        self.ml_model = AdvancedMLModel()
        self.telegram_bot = TelegramBetBot()
        self.report_generator = ReportGenerator()
        self.demo_mode = demo_mode
        
        # Store betting data for reporting
        self.betting_data = []
        
        # Load ML models if available
        if config.ML_ENABLED:
            self.ml_model.load_models('models/ml_models.pkl')
    
    def _extract_team_names(self, match_data: Dict) -> tuple:
        """Extract home and away team names from API data - handles both API-Football and SportMonks formats"""
        logger.info(f"🔍 Extracting team names from match data with keys: {list(match_data.keys())}")
        
        # Check if this is API-Football format
        if 'teams' in match_data:
            # API-Football format
            teams = match_data.get('teams', {})
            logger.info(f"   Found 'teams' key: {teams}")
            
            # Check if teams has home and away keys
            if 'home' in teams and 'away' in teams:
                home_team = teams.get('home', {}).get('name', 'Unknown')
                away_team = teams.get('away', {}).get('name', 'Unknown')
                logger.info(f"   Extracted: {home_team} vs {away_team}")
                return home_team, away_team
            else:
                logger.warning(f"   ❌ Teams object missing 'home' or 'away' keys")
                logger.warning(f"   Teams object keys: {list(teams.keys())}")
        
        # Check if this is SportMonks format
        elif 'name' in match_data and ' vs ' in match_data.get('name', ''):
            # SportMonks format
            match_name = match_data.get('name', 'Unknown vs Unknown')
            logger.info(f"   Found 'name' key with ' vs ': {match_name}")
            if ' vs ' in match_name:
                parts = match_name.split(' vs ')
                if len(parts) == 2:
                    home_team, away_team = parts[0].strip(), parts[1].strip()
                    logger.info(f"   Extracted: {home_team} vs {away_team}")
                    return home_team, away_team
        
        # Check if this is SportMonks format with participants
        elif 'participants' in match_data:
            participants = match_data.get('participants', [])
            logger.info(f"   Found 'participants' key: {participants}")
            if len(participants) >= 2:
                home_team = participants[0].get('name', 'Unknown')
                away_team = participants[1].get('name', 'Unknown')
                logger.info(f"   Extracted: {home_team} vs {away_team}")
                return home_team, away_team
        
        # Check for other possible formats
        elif 'localTeam' in match_data and 'visitorTeam' in match_data:
            home_team = match_data.get('localTeam', {}).get('name', 'Unknown')
            away_team = match_data.get('visitorTeam', {}).get('name', 'Unknown')
            logger.info(f"   Found localTeam/visitorTeam: {home_team} vs {away_team}")
            return home_team, away_team
        
        logger.warning(f"   ❌ Could not extract team names, using defaults")
        logger.warning(f"   Full match_data for debugging: {match_data}")
        
        # Try to extract any team information available
        if 'teams' in match_data:
            teams = match_data['teams']
            if isinstance(teams, dict):
                # Try to get any team names available
                home_team = teams.get('home', {}).get('name', 'Unknown Home')
                away_team = teams.get('away', {}).get('name', 'Unknown Away')
                if home_team != 'Unknown Home' or away_team != 'Unknown Away':
                    return home_team, away_team
        
        # Final fallback
        return 'Home Team', 'Away Team'
    
    def _extract_fixture_id(self, match_data: Dict) -> Optional[int]:
        """Extract fixture ID from API data - handles both API-Football and SportMonks formats"""
        logger.info("🔍 DEBUG: _extract_fixture_id called!")
        logger.info(f"🔍 DEBUG: Match data keys: {list(match_data.keys())}")
        
        # Check if this is API-Football format
        if 'fixture' in match_data and 'id' in match_data['fixture']:
            fixture_id = match_data['fixture']['id']
            logger.info(f"🔍 DEBUG: Found fixture ID in 'fixture' key: {fixture_id}")
            return fixture_id
        
        # Check if this is SportMonks format
        if 'id' in match_data:
            fixture_id = match_data['id']
            logger.info(f"🔍 DEBUG: Found fixture ID in 'id' key: {fixture_id}")
            return fixture_id
        
        logger.info("🔍 DEBUG: Could not extract fixture ID")
        return None
        
    async def start(self):
        """Start the betting system"""
        logger.info("Starting Football Betting System...")
        
        if not self.demo_mode:
            # Start Telegram bot
            try:
                await self.telegram_bot.start()
                logger.info("Telegram bot initialized successfully")
                
                # Start polling in a separate task to avoid blocking
                asyncio.create_task(self.telegram_bot.start_polling())
                logger.info("Telegram bot polling started in background")
                logger.info("Send /start to your bot in Telegram to begin")
                
                # Wait a moment for bot to fully initialize
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Telegram bot failed to start: {e}")
                logger.info("This could be due to:")
                logger.info("1. Invalid bot token")
                logger.info("2. Network connectivity issues")
                logger.info("3. Bot not properly configured")
                logger.info("Running in demo mode without Telegram bot")
                self.demo_mode = True
        
        # Daily analysis completely disabled in ROI-only mode
        if getattr(self, 'roi_only_mode', False):
            logger.info("ROI-only mode: Daily analysis completely disabled")
            logger.info("Only morning ROI updates at 8am UK time will be sent")
        else:
            # Schedule daily analysis (only if not in ROI-only mode)
            schedule.every().day.at("09:00").do(self.daily_analysis)
            schedule.every().sunday.at("18:00").do(self.generate_weekly_report)
            logger.info("Daily analysis scheduled for 09:00")
            logger.info("Weekly reports scheduled for Sunday 18:00")
        
        logger.info("System started successfully!")
        
        # Initial daily analysis completely disabled in ROI-only mode
        if getattr(self, 'roi_only_mode', False):
            logger.info("ROI-only mode: Initial daily analysis completely disabled")
        else:
            await self.daily_analysis()
        
        if not self.demo_mode:
            # Keep the system running with bot
            if getattr(self, 'roi_only_mode', False):
                logger.info("System running in ROI-only mode. Press Ctrl+C to stop.")
                logger.info("Morning ROI updates will be sent at 8am UK time")
                while True:
                    await asyncio.sleep(60)  # Check every minute
            else:
                logger.info("System running with Telegram bot. Press Ctrl+C to stop.")
                while True:
                    schedule.run_pending()
                    await asyncio.sleep(60)  # Check every minute
        else:
            logger.info("Demo mode: System completed initial analysis")
    
    # Daily analysis method completely disabled in ROI-only mode
    async def daily_analysis(self):
        """Daily analysis disabled in ROI-only mode"""
        if getattr(self, 'roi_only_mode', False):
            logger.info("Daily analysis is completely disabled in ROI-only mode")
            return
        else:
            logger.info("Daily analysis method called but not implemented")
            return
    
    async def analyze_match(self, match_data: Dict) -> List[Dict]:
        """Analyze a single match for value bets"""
        try:
            logger.info("🔍 DEBUG: analyze_match method started!")
            logger.info(f"🔍 DEBUG: match_data keys: {list(match_data.keys())}")
            
            fixture_id = self._extract_fixture_id(match_data)
            logger.info(f"🔍 DEBUG: Extracted fixture_id: {fixture_id} (type: {type(fixture_id)})")
            
            if not fixture_id:
                logger.warning(f"Could not extract fixture_id from match data. Keys: {list(match_data.keys())}")
                # Try to generate a fallback fixture ID for demo purposes
                if self.demo_mode:
                    import hashlib
                    # Generate a hash-based fixture ID from match data
                    match_str = str(match_data.get('teams', {})) + str(match_data.get('league', {}))
                    fixture_id = int(hashlib.md5(match_str.encode()).hexdigest()[:8], 16)
                    logger.info(f"Generated fallback fixture ID for demo: {fixture_id}")
                else:
                    return []
            
            # Extract team names from match name
            match_name = match_data.get('name', 'Unknown vs Unknown')
            logger.info(f"🔍 About to call _extract_team_names for match_data with keys: {list(match_data.keys())}")
            home_team, away_team = self._extract_team_names(match_data)
            logger.info(f"🔍 After _extract_team_names call: {home_team} vs {away_team}")
            
            # Extract team IDs from fixture data if available
            home_team_id = None
            away_team_id = None
            
            # Check if this is API-Football format
            if 'teams' in match_data and 'fixture' in match_data:
                teams = match_data.get('teams', {})
                home_team_id = teams.get('home', {}).get('id')
                away_team_id = teams.get('away', {}).get('id')
            
            # Check if this is SportMonks format
            elif 'localTeam' in match_data or 'visitorTeam' in match_data:
                home_team_id = match_data.get('localTeam', {}).get('id') or match_data.get('localteam_id')
                away_team_id = match_data.get('visitorTeam', {}).get('id') or match_data.get('visitorteam_id')
            
            # If team IDs are not available, try to extract from participants
            if not home_team_id or not away_team_id:
                participants = match_data.get('participants', [])
                if len(participants) >= 2:
                    home_team_id = participants[0].get('id') if participants[0].get('meta', {}).get('location') == 'home' else participants[1].get('id')
                    away_team_id = participants[1].get('id') if participants[1].get('meta', {}).get('location') == 'away' else participants[0].get('id')
            
            # If still no team IDs, use placeholder IDs for demo purposes
            if not home_team_id or not away_team_id:
                # Ensure fixture_id is an integer for placeholder generation
                if fixture_id is None or not isinstance(fixture_id, int):
                    safe_fixture_id = 1000
                    logger.warning(f"fixture_id is None or invalid, using fallback: {safe_fixture_id}")
                else:
                    safe_fixture_id = fixture_id
                
                home_team_id = 1000 + safe_fixture_id  # Generate unique placeholder ID
                away_team_id = 2000 + safe_fixture_id  # Generate unique placeholder ID
                logger.warning(f"Using placeholder team IDs for fixture {fixture_id}")
                logger.info(f"🔍 Generated placeholder team IDs: Home={home_team_id}, Away={away_team_id}")
            
            # Final safety check - ensure team IDs are valid integers
            if not isinstance(home_team_id, int) or not isinstance(away_team_id, int):
                logger.error(f"Team IDs are still not valid integers: home_team_id={home_team_id} (type: {type(home_team_id)}), away_team_id={away_team_id} (type: {type(away_team_id)})")
                # Use fallback IDs
                home_team_id = 1000
                away_team_id = 2000
                logger.info(f"Using fallback team IDs: Home={home_team_id}, Away={away_team_id}")
            
            # Get match odds
            odds_data = await self.api_client.get_match_odds(fixture_id)
            
            if not odds_data:
                logger.warning(f"No odds data available for fixture {fixture_id}")
                return []
            

            
            # Get team form data (use empty lists if not available)
            try:
                home_form = await self.api_client.get_team_form(home_team_id, 5) or []
                away_form = await self.api_client.get_team_form(away_team_id, 5) or []
            except:
                home_form = []
                away_form = []
                logger.warning(f"Could not fetch team form for fixture {fixture_id}")
            
            # Generate predictions
            predictions = await self.generate_predictions(home_team_id, away_team_id, home_form, away_form)
            
            logger.info(f"🎯 Generated predictions for fixture {fixture_id}:")
            logger.info(f"   Match Result: {predictions.get('match_result', {})}")
            logger.info(f"   Goals: {predictions.get('goals', {})}")
            logger.info(f"   Corners: {predictions.get('corners', {})}")
            
            # Extract odds in the correct format
            match_odds = self.extract_match_odds(odds_data)
            goals_odds = self.extract_goals_odds(odds_data)
            corners_odds = self.extract_corners_odds(odds_data)
            
            logger.info(f"💰 Available odds:")
            logger.info(f"   Match: {match_odds}")
            logger.info(f"   Goals: {match_odds}")
            logger.info(f"   Corners: {corners_odds}")
            
            # Analyze for value bets
            value_bets = []
            
            # Match result analysis
            if match_odds and 'match_result' in predictions:
                logger.info(f"🔍 Analyzing match result bets...")
                match_result_bets = self.value_analyzer.analyze_match_result_bets(
                    predictions['match_result'], match_odds
                )
                logger.info(f"   Found {len(match_result_bets)} match result value bets")
                value_bets.extend(match_result_bets)
            
            # Goals analysis
            if goals_odds and 'goals' in predictions:
                logger.info(f"🔍 Analyzing goals bets...")
                goals_bets = self.value_analyzer.analyze_goals_bets(
                    predictions['goals'], goals_odds
                )
                logger.info(f"   Found {len(goals_bets)} goals value bets")
                value_bets.extend(goals_bets)
            
            # Corners analysis
            if corners_odds and 'corners' in predictions:
                logger.info(f"🔍 Analyzing corners bets...")
                corners_bets = self.value_analyzer.analyze_corners_bets(
                    predictions['corners'], corners_odds
                )
                logger.info(f"   Found {len(corners_bets)} corners value bets")
                value_bets.extend(corners_bets)
            
            if value_bets:
                logger.info(f"Match {fixture_id} ({home_team} vs {away_team}) - Found {len(value_bets)} value bets")
                # Sort by edge value
                value_bets = self.value_analyzer.sort_value_bets(value_bets)
            else:
                logger.info(f"Match {fixture_id} ({home_team} vs {away_team}) - No value bets found")
            
            return value_bets
            
        except Exception as e:
            logger.error(f"Error analyzing match {match_data.get('id', 'unknown')}: {e}")
            return []
    
    async def generate_predictions(self, home_team_id: int, away_team_id: int,
                                 home_form: List[Dict], away_form: List[Dict]) -> Dict:
        """Generate predictions using all models"""
        predictions = {}
        
        # Safety check - ensure team IDs are valid integers
        if not isinstance(home_team_id, int) or not isinstance(away_team_id, int):
            logger.error(f"Invalid team IDs in generate_predictions: home_team_id={home_team_id} (type: {type(home_team_id)}), away_team_id={away_team_id} (type: {type(away_team_id)})")
            # Return empty predictions to avoid errors
            return {
                'match_result': {'home_win': 0.33, 'draw': 0.34, 'away_win': 0.33},
                'goals': {'over_05': 0.5, 'over_15': 0.5, 'over_25': 0.5, 'under_05': 0.5, 'under_15': 0.5, 'under_25': 0.5, 'btts': 0.5, 'total_xg': 2.0, 'home_xg': 1.0, 'away_xg': 1.0},
                'corners': {'over_45': 0.5, 'over_55': 0.5, 'over_65': 0.5, 'over_75': 0.5, 'over_85': 0.5, 'over_95': 0.5, 'under_45': 0.5, 'under_55': 0.5, 'under_65': 0.5, 'under_75': 0.5, 'under_85': 0.5, 'under_95': 0.5, 'home_over_45': 0.5, 'away_over_45': 0.5, 'total_corners': 10.0, 'home_corners': 5.0, 'away_corners': 5.0}
            }
        
        # Elo predictions
        home_win_prob, draw_prob, away_win_prob = self.elo_model.predict_match_result(home_team_id, away_team_id)
        predictions['match_result'] = {
            'home_win': home_win_prob,
            'draw': draw_prob,
            'away_win': away_win_prob
        }
        
        # xG predictions
        home_stats = self.xg_model.calculate_team_xg(home_team_id, home_form)
        away_stats = self.xg_model.calculate_team_xg(away_team_id, away_form)
        
        home_xg, away_xg = self.xg_model.predict_match_xg(home_team_id, away_team_id, home_stats, away_stats)
        goals_predictions = self.xg_model.predict_goals_probabilities(home_xg, away_xg)
        predictions['goals'] = goals_predictions
        
        # Corners predictions
        home_corner_stats = self.corners_model.calculate_team_corners(home_team_id, home_form)
        away_corner_stats = self.corners_model.calculate_team_corners(away_team_id, away_form)
        
        home_corners, away_corners = self.corners_model.predict_match_corners(home_team_id, away_team_id, home_corner_stats, away_corner_stats)
        corners_predictions = self.corners_model.predict_corners_probabilities(home_corners, away_corners)
        predictions['corners'] = corners_predictions
        
        return predictions
    
    def extract_match_odds(self, odds_data: List[Dict]) -> Dict:
        """Extract match result odds from API data - Updated for SportMonks format"""
        match_odds = {}
        
        logger.info(f"🔍 Processing {len(odds_data)} odds records for match result...")
        
        for odds_record in odds_data:
            # Check if this is a match result market
            market_desc = odds_record.get('market_description', '').lower()
            label = odds_record.get('label', '')
            odds_value = odds_record.get('dp3') or odds_record.get('value')
            
            # Look for fulltime result markets
            if 'fulltime result' in market_desc:
                if odds_value:
                    try:
                        odds_float = float(odds_value)
                        if label.lower() == 'home':
                            match_odds['home_win'] = odds_float
                            logger.info(f"      ✅ Home win odds: {odds_float}")
                        elif label.lower() == 'draw':
                            match_odds['draw'] = odds_float
                            logger.info(f"      ✅ Draw odds: {odds_float}")
                        elif label.lower() == 'away':
                            match_odds['away_win'] = odds_float
                            logger.info(f"      ✅ Away win odds: {odds_float}")
                    except (ValueError, TypeError):
                        logger.warning(f"      ❌ Invalid odds value: {odds_value}")
                        continue
        
        logger.info(f"📈 Extracted match odds: {match_odds}")
        return match_odds
    
    def extract_goals_odds(self, odds_data: List[Dict]) -> Dict:
        """Extract goals-related odds from API data - Updated for SportMonks format"""
        goals_odds = {}
        
        logger.info(f"🔍 Processing {len(odds_data)} odds records for goals markets...")
        
        for odds_record in odds_data:
            market_desc = odds_record.get('market_description', '').lower()
            label = odds_record.get('label', '').lower()
            odds_value = odds_record.get('dp3') or odds_record.get('value')
            
            if not odds_value:
                continue
                
            try:
                odds_float = float(odds_value)
                
                # Both teams to score
                if 'both teams to score' in market_desc or 'btts' in market_desc:
                    if 'yes' in label:
                        goals_odds['btts_yes'] = odds_float
                        logger.info(f"      ✅ BTTS Yes odds: {odds_float}")
                    elif 'no' in label:
                        goals_odds['btts_no'] = odds_float
                        logger.info(f"      ✅ BTTS No odds: {odds_float}")
                
                # Over/Under goals
                elif 'goals over/under' in market_desc:
                    if 'over' in label:
                        goals_odds['over_goals'] = odds_float
                        logger.info(f"      ✅ Over goals odds: {odds_float}")
                    elif 'under' in label:
                        goals_odds['under_goals'] = odds_float
                        logger.info(f"      ✅ Under goals odds: {odds_float}")
                
                # Total goals
                elif 'total goals' in market_desc:
                    if 'over' in label:
                        goals_odds['over_total'] = odds_float
                        logger.info(f"      ✅ Over total odds: {odds_float}")
                    elif 'under' in label:
                        goals_odds['under_total'] = odds_float
                        logger.info(f"      ✅ Under total odds: {odds_float}")
                        
            except (ValueError, TypeError):
                logger.warning(f"      ❌ Invalid odds value: {odds_value}")
                continue
        
        logger.info(f"📈 Extracted goals odds: {goals_odds}")
        return goals_odds
    
    def extract_corners_odds(self, odds_data: List[Dict]) -> Dict:
        """Extract corners-related odds from API data - Updated for SportMonks format"""
        corners_odds = {}
        
        logger.info(f"🔍 Processing {len(odds_data)} odds records for corners markets...")
        
        for odds_record in odds_data:
            market_desc = odds_record.get('market_description', '').lower()
            label = odds_record.get('label', '').lower()
            odds_value = odds_record.get('dp3') or odds_record.get('value')
            
            if not odds_value:
                continue
                
            try:
                odds_float = float(odds_value)
                
                # Total corners
                if 'total corners' in market_desc:
                    if 'over' in label:
                        corners_odds['over_corners'] = odds_float
                        logger.info(f"      ✅ Over corners odds: {odds_float}")
                    elif 'under' in label:
                        corners_odds['under_corners'] = odds_float
                        logger.info(f"      ✅ Under corners odds: {odds_float}")
                
                # Asian total corners
                elif 'asian total corners' in market_desc:
                    if 'over' in label:
                        corners_odds['asian_over_corners'] = odds_float
                        logger.info(f"      ✅ Asian Over corners odds: {odds_float}")
                    elif 'under' in label:
                        corners_odds['asian_under_corners'] = odds_float
                        logger.info(f"      ✅ Asian Under corners odds: {odds_float}")
                        
            except (ValueError, TypeError):
                logger.warning(f"      ❌ Invalid odds value: {odds_value}")
                continue
        
        logger.info(f"📈 Extracted corners odds: {corners_odds}")
        return corners_odds
    
    def generate_weekly_report(self):
        """Generate weekly ROI report"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            # Filter betting data for the week
            weekly_data = [
                bet for bet in self.betting_data
                if start_date <= datetime.fromisoformat(bet['date']) <= end_date
            ]
            
            # Generate report
            report_path = self.report_generator.generate_weekly_report(
                weekly_data, start_date, end_date
            )
            
            logger.info(f"Weekly report generated: {report_path}")
            
        except Exception as e:
            logger.error(f"Error generating weekly report: {e}")
    
    def add_betting_record(self, bet_record: Dict):
        """Add a betting record to the system"""
        self.betting_data.append(bet_record)
    
    async def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self.api_client, 'cleanup'):
                await self.api_client.cleanup()
            logger.info("API clients cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

async def main():
    """Main function to run the betting system"""
    import sys
    
    # Check if demo mode is requested
    demo_mode = '--demo' in sys.argv
    
    # Check if ROI-only mode is requested
    roi_only_mode = '--roi-only' in sys.argv
    
    if demo_mode:
        print("🚀 Starting Football Betting System in DEMO MODE")
        print("This mode will analyze matches without requiring Telegram bot setup")
        print()
    
    if roi_only_mode:
        print("💰 Starting Football Betting System in ROI-ONLY MODE")
        print("This mode will only post daily summaries at 8am UK time, not after every command")
        print()
    
    betting_system = FootballBettingSystem(demo_mode=demo_mode)
    
    # Set ROI-only mode flag
    if roi_only_mode:
        betting_system.roi_only_mode = True
    
    try:
        await betting_system.start()
    except KeyboardInterrupt:
        logger.info("Shutting down betting system...")
        if not demo_mode:
            betting_system.telegram_bot.stop()
    except Exception as e:
        logger.error(f"System error: {e}")
        if not demo_mode:
            await betting_system.telegram_bot.post_error_message(f"System error: {str(e)}")
    finally:
        # Always cleanup
        await betting_system.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
