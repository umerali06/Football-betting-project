import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Import our modules
import config
from api.api_sportmonks import SportMonksClient
from models.elo_model import EloModel
from models.xg_model import XGModel
from models.corners_model import CornersModel
from betting.value_bet_analyzer import ValueBetAnalyzer
from betting.risk_manager import AdvancedRiskManager
from models.ml_model import AdvancedMLModel
from bot_interface.telegram_bot import TelegramBetBot
from reports.report_generator import ReportGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('betting_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FootballBettingSystem:
    """
    Main football betting system that combines all components
    """
    
    def __init__(self, demo_mode: bool = False):
        self.api_client = SportMonksClient()
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
    
    def _extract_team_names(self, match_name: str) -> tuple:
        """Extract home and away team names from SportMonks match name format"""
        if ' vs ' in match_name:
            parts = match_name.split(' vs ')
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
        return 'Home Team', 'Away Team'
        
    async def start(self):
        """Start the betting system"""
        logger.info("Starting Football Betting System...")
        
        if not self.demo_mode:
            # Start Telegram bot
            try:
                await self.telegram_bot.start()
                logger.info("Telegram bot started successfully")
                logger.info("Send /setchat to your bot in Telegram to set up notifications")
            except Exception as e:
                logger.error(f"Telegram bot failed to start: {e}")
                logger.info("This could be due to:")
                logger.info("1. Invalid bot token")
                logger.info("2. Network connectivity issues")
                logger.info("3. Bot not properly configured")
                logger.info("Running in demo mode without Telegram bot")
                self.demo_mode = True
        
        # Schedule daily analysis
        schedule.every().day.at("09:00").do(self.daily_analysis)
        schedule.every().sunday.at("18:00").do(self.generate_weekly_report)
        
        logger.info("System started successfully!")
        logger.info("Daily analysis scheduled for 09:00")
        logger.info("Weekly reports scheduled for Sunday 18:00")
        
        # Run initial analysis
        await self.daily_analysis()
        
        if not self.demo_mode:
            # Keep the system running
            while True:
                schedule.run_pending()
                await asyncio.sleep(60)  # Check every minute
        else:
            logger.info("Demo mode: System completed initial analysis")
    
    async def daily_analysis(self):
        """Perform daily betting analysis"""
        logger.info("Starting daily betting analysis...")
        
        try:
            # Get today's matches - REAL TIME ONLY
            matches = self.api_client.get_today_matches()
            
            if not matches:
                logger.info("No matches available at the moment")
                if not self.demo_mode:
                    await self.telegram_bot.post_no_matches_message()
                    logger.info("Posted 'no matches' message to Telegram")
                return
            
            logger.info(f"Found {len(matches)} matches for today")
            
            total_value_bets = []
            summary_stats = {
                'total_bets': 0,
                'value_bets_found': 0,
                'average_edge': 0.0,
                'total_roi': 0.0
            }
            
            # Analyze first few matches for demo
            demo_matches = matches[:3] if self.demo_mode else matches
            
            for i, match in enumerate(demo_matches):
                # Extract team names from SportMonks API response
                match_name = match.get('name', 'Unknown vs Unknown')
                home_team, away_team = self._extract_team_names(match_name)
                
                logger.info(f"Analyzing match {i+1}/{len(demo_matches)}: {home_team} vs {away_team}")
                
                value_bets = await self.analyze_match(match)
                if value_bets:
                    total_value_bets.extend(value_bets)
                    summary_stats['value_bets_found'] += len(value_bets)
                    logger.info(f"Found {len(value_bets)} value bets for this match")
                
                summary_stats['total_bets'] += 1
            
            # Calculate average edge
            if total_value_bets:
                avg_edge = sum(bet['edge'] for bet in total_value_bets) / len(total_value_bets)
                summary_stats['average_edge'] = avg_edge
            
            # Post value bets to Telegram (if not in demo mode)
            if total_value_bets and not self.demo_mode:
                await self.telegram_bot.post_value_bets(total_value_bets)
                logger.info(f"Posted {len(total_value_bets)} value bets to Telegram")
            elif not self.demo_mode:
                # Post "no matches" message to Telegram
                await self.telegram_bot.post_no_matches_message()
                logger.info("Posted 'no matches' message to Telegram")
            
            # Post daily summary (if not in demo mode)
            if not self.demo_mode:
                await self.telegram_bot.post_daily_summary(summary_stats)
            
            logger.info(f"Daily analysis completed. Found {len(total_value_bets)} value bets")
            
            # Print summary in demo mode
            if self.demo_mode:
                print(f"\nPremium Analysis Summary:")
                print(f"Matches analyzed: {summary_stats['total_bets']}")
                print(f"Value bets found: {summary_stats['value_bets_found']}")
                if total_value_bets:
                    print(f"Average edge: {summary_stats['average_edge']:.3f}")
                    
                    # Get risk-managed recommendations
                    recommendations = self.risk_manager.get_bet_recommendations(total_value_bets)
                    
                    print(f"\nPremium Value Bets (Risk-Managed):")
                    for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
                        print(f"{i}. {rec['match_info']['home_team']} vs {rec['match_info']['away_team']}")
                        print(f"   Market: {rec['market']} | Selection: {rec['selection']}")
                        print(f"   Odds: {rec['odds']} | Edge: {rec['edge']:.3f}")
                        print(f"   Confidence: {rec.get('confidence', 0.7):.2f}")
                        print(f"   Kelly %: {rec['kelly_percentage']:.3f}")
                        print(f"   Recommended Stake: £{rec['recommended_stake']:.2f}")
                        print(f"   Risk Score: {rec['risk_score']:.4f}")
                        print()
                    
                    # Show performance metrics
                    metrics = self.risk_manager.get_performance_metrics()
                    if metrics and metrics.get('total_bets', 0) > 0:
                        print(f"Performance Metrics:")
                        print(f"   Win Rate: {metrics.get('win_rate', 0):.1%}")
                        print(f"   Overall ROI: {metrics.get('overall_roi', 0):.1%}")
                        print(f"   Bankroll Growth: {metrics.get('bankroll_growth', 0):.1%}")
                        print(f"   Kelly Efficiency: {metrics.get('kelly_efficiency', 0):.1%}")
                        print()
                    else:
                        print(f"Performance Metrics: No historical data available yet")
                        print()
                    
                    # Show risk alerts
                    alerts = self.risk_manager.get_risk_alerts()
                    if alerts:
                        print(f"Risk Alerts:")
                        for alert in alerts:
                            print(f"   • {alert}")
                        print()
            
        except Exception as e:
            logger.error(f"Error in daily analysis: {e}")
            if not self.demo_mode:
                await self.telegram_bot.post_error_message(f"Daily analysis failed: {str(e)}")
    
    async def analyze_match(self, match_data: Dict) -> List[Dict]:
        """Analyze a single match for value bets"""
        try:
            fixture_id = match_data['id']
            
            # Extract team names from match name
            match_name = match_data.get('name', 'Unknown vs Unknown')
            home_team, away_team = self._extract_team_names(match_name)
            
            # Extract team IDs from fixture data if available
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
                home_team_id = 1000 + fixture_id  # Generate unique placeholder ID
                away_team_id = 2000 + fixture_id  # Generate unique placeholder ID
                logger.warning(f"Using placeholder team IDs for fixture {fixture_id}")
            
            # Get match odds
            odds_data = self.api_client.get_match_odds(fixture_id)
            
            if not odds_data:
                logger.warning(f"No odds data available for fixture {fixture_id}")
                return []
            
            # Get team form data (use empty lists if not available)
            try:
                home_form = self.api_client.get_team_form(home_team_id, 5) or []
                away_form = self.api_client.get_team_form(away_team_id, 5) or []
            except:
                home_form = []
                away_form = []
                logger.warning(f"Could not fetch team form for fixture {fixture_id}")
            
            # Generate predictions
            predictions = await self.generate_predictions(home_team_id, away_team_id, home_form, away_form)
            
            print(f"🎯 Generated predictions for fixture {fixture_id}:")
            print(f"   Match Result: {predictions.get('match_result', {})}")
            print(f"   Goals: {predictions.get('goals', {})}")
            print(f"   Corners: {predictions.get('corners', {})}")
            
            # Extract odds in the correct format
            match_odds = self.extract_match_odds(odds_data)
            goals_odds = self.extract_goals_odds(odds_data)
            corners_odds = self.extract_corners_odds(odds_data)
            
            print(f"💰 Available odds:")
            print(f"   Match: {match_odds}")
            print(f"   Goals: {goals_odds}")
            print(f"   Corners: {corners_odds}")
            
            # Analyze for value bets
            value_bets = []
            
            # Match result analysis
            if match_odds and 'match_result' in predictions:
                print(f"🔍 Analyzing match result bets...")
                match_result_bets = self.value_analyzer.analyze_match_result_bets(
                    predictions['match_result'], match_odds
                )
                print(f"   Found {len(match_result_bets)} match result value bets")
                value_bets.extend(match_result_bets)
            
            # Goals analysis
            if goals_odds and 'goals' in predictions:
                print(f"🔍 Analyzing goals bets...")
                goals_bets = self.value_analyzer.analyze_goals_bets(
                    predictions['goals'], goals_odds
                )
                print(f"   Found {len(goals_bets)} goals value bets")
                value_bets.extend(goals_bets)
            
            # Corners analysis
            if corners_odds and 'corners' in predictions:
                print(f"🔍 Analyzing corners bets...")
                corners_bets = self.value_analyzer.analyze_corners_bets(
                    predictions['corners'], corners_odds
                )
                print(f"   Found {len(corners_bets)} corners value bets")
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
        
        print(f"🔍 Processing {len(odds_data)} odds records for match result...")
        
        for odds_record in odds_data:
            # Check if this is a match result market
            market_desc = odds_record.get('market_description', '').lower()
            if 'fulltime result' in market_desc or 'match winner' in market_desc:
                # Extract the outcome value and odds
                outcome_value = odds_record.get('value', '')
                odds_value = odds_record.get('dp3') or odds_record.get('value')
                
                print(f"   📊 Market: {market_desc}, Outcome: {outcome_value}, Odds: {odds_value}")
                
                if odds_value and outcome_value:
                    try:
                        odds_float = float(odds_value)
                        if outcome_value == '1' or outcome_value == 'home':
                            match_odds['home_win'] = odds_float
                            print(f"      ✅ Home win odds: {odds_float}")
                        elif outcome_value == 'X' or outcome_value == 'draw':
                            match_odds['draw'] = odds_float
                            print(f"      ✅ Draw odds: {odds_float}")
                        elif outcome_value == '2' or outcome_value == 'away':
                            match_odds['away_win'] = odds_float
                            print(f"      ✅ Away win odds: {odds_float}")
                    except (ValueError, TypeError):
                        print(f"      ❌ Invalid odds value: {odds_value}")
                        continue
        
        print(f"📈 Extracted match odds: {match_odds}")
        return match_odds
    
    def extract_goals_odds(self, odds_data: List[Dict]) -> Dict:
        """Extract goals-related odds from API data - Updated for SportMonks format"""
        goals_odds = {}
        
        print(f"🔍 Processing {len(odds_data)} odds records for goals markets...")
        
        for odds_record in odds_data:
            market_desc = odds_record.get('market_description', '').lower()
            outcome_value = odds_record.get('value', '')
            odds_value = odds_record.get('dp3') or odds_record.get('value')
            
            if not odds_value or not outcome_value:
                continue
                
            try:
                odds_float = float(odds_value)
                
                # Both teams to score
                if 'both teams to score' in market_desc or 'btts' in market_desc:
                    if 'yes' in outcome_value.lower():
                        goals_odds['btts_yes'] = odds_float
                        print(f"      ✅ BTTS Yes odds: {odds_float}")
                    elif 'no' in outcome_value.lower():
                        goals_odds['btts_no'] = odds_float
                        print(f"      ✅ BTTS No odds: {odds_float}")
                
                # Over/Under goals
                elif 'over' in market_desc or 'under' in market_desc:
                    if 'over' in outcome_value.lower():
                        goals_odds['over_goals'] = odds_float
                        print(f"      ✅ Over goals odds: {odds_float}")
                    elif 'under' in outcome_value.lower():
                        goals_odds['under_goals'] = odds_float
                        print(f"      ✅ Under goals odds: {odds_float}")
                
                # Total goals
                elif 'total goals' in market_desc:
                    if 'over' in outcome_value.lower():
                        goals_odds['over_total'] = odds_float
                        print(f"      ✅ Over total odds: {odds_float}")
                    elif 'under' in outcome_value.lower():
                        goals_odds['under_total'] = odds_float
                        print(f"      ✅ Under total odds: {odds_float}")
                        
            except (ValueError, TypeError):
                print(f"      ❌ Invalid odds value: {odds_value}")
                continue
        
        print(f"📈 Extracted goals odds: {goals_odds}")
        return goals_odds
    
    def extract_corners_odds(self, odds_data: List[Dict]) -> Dict:
        """Extract corners-related odds from API data - Updated for SportMonks format"""
        corners_odds = {}
        
        print(f"🔍 Processing {len(odds_data)} odds records for corners markets...")
        
        for odds_record in odds_data:
            market_desc = odds_record.get('market_description', '').lower()
            outcome_value = odds_record.get('value', '')
            odds_value = odds_record.get('dp3') or odds_record.get('value')
            
            if not odds_value or not outcome_value:
                continue
                
            try:
                odds_float = float(odds_value)
                
                # Total corners
                if 'corners' in market_desc:
                    if 'over' in outcome_value.lower():
                        corners_odds['over_corners'] = odds_float
                        print(f"      ✅ Over corners odds: {odds_float}")
                    elif 'under' in outcome_value.lower():
                        corners_odds['under_corners'] = odds_float
                        print(f"      ✅ Under corners odds: {odds_float}")
                
                # Team corners
                elif 'team corners' in market_desc:
                    if 'home' in outcome_value.lower():
                        corners_odds['home_corners'] = odds_float
                        print(f"      ✅ Home corners odds: {odds_float}")
                    elif 'away' in outcome_value.lower():
                        corners_odds['away_corners'] = odds_float
                        print(f"      ✅ Away corners odds: {odds_float}")
                        
            except (ValueError, TypeError):
                print(f"      ❌ Invalid odds value: {odds_value}")
                continue
        
        print(f"📈 Extracted corners odds: {corners_odds}")
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

async def main():
    """Main function to run the betting system"""
    import sys
    
    # Check if demo mode is requested
    demo_mode = '--demo' in sys.argv
    
    if demo_mode:
        print("🚀 Starting Football Betting System in DEMO MODE")
        print("This mode will analyze matches without requiring Telegram bot setup")
        print()
    
    betting_system = FootballBettingSystem(demo_mode=demo_mode)
    
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

if __name__ == "__main__":
    asyncio.run(main())
