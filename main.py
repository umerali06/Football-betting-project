import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Import our modules
import config
from api.api_football import APIFootballClient
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
        self.api_client = APIFootballClient()
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
                logger.info("📭 No matches available at the moment")
                if not self.demo_mode:
                    await self.telegram_bot.post_no_matches_message()
                    logger.info("Posted 'no matches' message to Telegram")
                return
            
            logger.info(f"✅ Found {len(matches)} matches for today")
            
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
                logger.info(f"Analyzing match {i+1}/{len(demo_matches)}: {match['teams']['home']['name']} vs {match['teams']['away']['name']}")
                
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
                print(f"\n📊 Premium Analysis Summary:")
                print(f"Matches analyzed: {summary_stats['total_bets']}")
                print(f"Value bets found: {summary_stats['value_bets_found']}")
                if total_value_bets:
                    print(f"Average edge: {summary_stats['average_edge']:.3f}")
                    
                    # Get risk-managed recommendations
                    recommendations = self.risk_manager.get_bet_recommendations(total_value_bets)
                    
                    print(f"\n🎯 Premium Value Bets (Risk-Managed):")
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
                        print(f"💰 Performance Metrics:")
                        print(f"   Win Rate: {metrics.get('win_rate', 0):.1%}")
                        print(f"   Overall ROI: {metrics.get('overall_roi', 0):.1%}")
                        print(f"   Bankroll Growth: {metrics.get('bankroll_growth', 0):.1%}")
                        print(f"   Kelly Efficiency: {metrics.get('kelly_efficiency', 0):.1%}")
                        print()
                    else:
                        print(f"💰 Performance Metrics: No historical data available yet")
                        print()
                    
                    # Show risk alerts
                    alerts = self.risk_manager.get_risk_alerts()
                    if alerts:
                        print(f"⚠️ Risk Alerts:")
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
            fixture_id = match_data['fixture']['id']
            home_team_id = match_data['teams']['home']['id']
            away_team_id = match_data['teams']['away']['id']
            
            # Get team form data
            home_form = self.api_client.get_team_form(home_team_id, 10)
            away_form = self.api_client.get_team_form(away_team_id, 10)
            
            # Get match odds
            odds_data = self.api_client.get_match_odds(fixture_id)
            
            # Generate predictions
            predictions = await self.generate_predictions(home_team_id, away_team_id, home_form, away_form)
            
            # Analyze for value bets
            value_bets = []
            
            # Match result bets
            if 'match_result' in predictions and odds_data:
                match_odds = self.extract_match_odds(odds_data)
                value_bets.extend(self.value_analyzer.analyze_match_result_bets(predictions['match_result'], match_odds))
            
            # Goals bets
            if 'goals' in predictions and odds_data:
                goals_odds = self.extract_goals_odds(odds_data)
                value_bets.extend(self.value_analyzer.analyze_goals_bets(predictions['goals'], goals_odds))
            
            # Corners bets
            if 'corners' in predictions and odds_data:
                corners_odds = self.extract_corners_odds(odds_data)
                value_bets.extend(self.value_analyzer.analyze_corners_bets(predictions['corners'], corners_odds))
            
            # Add match info to value bets
            for bet in value_bets:
                bet['match_info'] = {
                    'fixture_id': fixture_id,
                    'home_team': match_data['teams']['home']['name'],
                    'away_team': match_data['teams']['away']['name'],
                    'match_time': match_data['fixture']['date']
                }
            
            return value_bets
            
        except Exception as e:
            logger.error(f"Error analyzing match {match_data.get('fixture', {}).get('id', 'unknown')}: {e}")
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
