import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from utils.time import now_london, get_next_8am_london
from filters.competition_filter import CompetitionFilter
import config

logger = logging.getLogger(__name__)

class DailyJobsScheduler:
    """Scheduler for daily automated jobs"""
    
    def __init__(self, telegram_bot=None):
        self.scheduler = AsyncIOScheduler()
        self.telegram_bot = telegram_bot
        self.competition_filter = CompetitionFilter()
        self.is_running = False
        
    async def start(self):
        """Start the scheduler"""
        try:
            # Add daily digest job at 8:00 AM UK time
            self.scheduler.add_job(
                self.job_morning_digest,
                trigger=CronTrigger(hour=8, minute=0, timezone='Europe/London'),
                id='morning_digest',
                name='Daily Morning Digest',
                replace_existing=True
            )
            
            # Start the scheduler
            self.scheduler.start()
            self.is_running = True
            
            next_run = get_next_8am_london()
            logger.info(f"Daily jobs scheduler started successfully")
            logger.info(f"Next morning digest scheduled for: {next_run.strftime('%Y-%m-%d %H:%M')} UK time")
            
        except Exception as e:
            logger.error(f"Failed to start daily jobs scheduler: {e}")
            raise
    
    async def stop(self):
        """Stop the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("Daily jobs scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    async def job_morning_digest(self):
        """Daily morning digest job - runs at 8:00 AM UK time"""
        try:
            logger.info("Starting daily morning digest job...")
            
            # Get current UK time
            now_uk = now_london()
            logger.info(f"Current UK time: {now_uk.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Force fresh fetch of today's future fixtures
            fixtures = await self._fetch_todays_fixtures(bypass_cache=True)
            
            if not fixtures:
                message = "📅 Today (UK) – No upcoming fixtures for configured competitions."
                logger.info("No fixtures found for today")
            else:
                # Run ROI/value-bet analysis
                value_bets = await self._analyze_value_bets(fixtures)
                
                # Format message
                message = self._format_morning_digest(fixtures, value_bets, now_uk)
                logger.info(f"Generated morning digest with {len(fixtures)} fixtures and {len(value_bets)} value bets")
            
            # Send via Telegram bot
            if self.telegram_bot:
                await self._send_telegram_message(message)
            else:
                logger.warning("Telegram bot not available, cannot send morning digest")
            
            logger.info("Daily morning digest job completed successfully")
            
        except Exception as e:
            logger.error(f"Error in morning digest job: {e}")
            # Try to send error notification
            if self.telegram_bot:
                try:
                    error_msg = f"❌ Error in morning digest job: {str(e)}"
                    await self._send_telegram_message(error_msg)
                except Exception as send_error:
                    logger.error(f"Failed to send error notification: {send_error}")
    
    async def _fetch_todays_fixtures(self, bypass_cache: bool = False) -> List[Dict]:
        """Fetch today's fixtures with optional cache bypass"""
        try:
            from api.unified_api_client import UnifiedAPIClient
            
            # Initialize API client
            api_client = UnifiedAPIClient()
            
            # Get today's date range in UK time
            now_uk = now_london()
            start_dt = now_uk.replace(hour=0, minute=0, second=0, microsecond=0)
            end_dt = now_uk.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Add future cutoff minutes from config
            from config.leagues import future_cutoff_minutes
            start_dt = start_dt + timedelta(minutes=future_cutoff_minutes)
            
            logger.info(f"Fetching fixtures from {start_dt.strftime('%H:%M')} to {end_dt.strftime('%H:%M')} UK time")
            
            # Get fixtures using unified client
            fixtures = await api_client.get_fixtures(start_dt, end_dt)
            
            # Filter by allowed competitions
            fixtures = self.competition_filter.filter_fixtures(fixtures)
            
            logger.info(f"Found {len(fixtures)} fixtures for today")
            return fixtures
            
        except Exception as e:
            logger.error(f"Failed to fetch today's fixtures: {e}")
            return []
    
    async def _analyze_value_bets(self, fixtures: List[Dict]) -> List[Dict]:
        """Analyze fixtures for value bets"""
        try:
            from betting.value_bet_analyzer import ValueBetAnalyzer
            from models.elo_model import EloModel
            from models.xg_model import XGModel
            from models.corners_model import CornersModel
            
            value_bets = []
            value_analyzer = ValueBetAnalyzer()
            
            # Initialize models
            elo_model = EloModel()
            xg_model = XGModel()
            corners_model = CornersModel()
            
            for fixture in fixtures:
                try:
                    # Extract fixture ID and team information
                    fixture_id = self._extract_fixture_id(fixture)
                    home_team_id = self._extract_team_id(fixture, 'home')
                    away_team_id = self._extract_team_id(fixture, 'away')
                    
                    if not all([fixture_id, home_team_id, away_team_id]):
                        continue
                    
                    # Generate predictions
                    predictions = await self._generate_predictions(
                        home_team_id, away_team_id, elo_model, xg_model, corners_model
                    )
                    
                    # Get odds data
                    odds_data = await self._get_odds_data(fixture_id)
                    
                    if odds_data and predictions:
                        # Analyze for value bets
                        fixture_value_bets = self._analyze_fixture_value_bets(
                            fixture, predictions, odds_data, value_analyzer
                        )
                        value_bets.extend(fixture_value_bets)
                
                except Exception as e:
                    logger.debug(f"Failed to analyze fixture {fixture.get('id', 'unknown')}: {e}")
                    continue
            
            # Sort by edge value (descending)
            value_bets.sort(key=lambda x: x.get('edge', 0), reverse=True)
            
            logger.info(f"Found {len(value_bets)} value bets")
            return value_bets
            
        except Exception as e:
            logger.error(f"Failed to analyze value bets: {e}")
            return []
    
    def _extract_fixture_id(self, fixture: Dict) -> Optional[int]:
        """Extract fixture ID from fixture data"""
        try:
            # Try different possible keys
            possible_keys = ['id', 'fixture.id', 'fixture_id']
            
            for key in possible_keys:
                if '.' in key:
                    parts = key.split('.')
                    value = fixture
                    for part in parts:
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        else:
                            value = None
                            break
                else:
                    value = fixture.get(key)
                
                if value and isinstance(value, int):
                    return value
            
            return None
        except Exception as e:
            logger.debug(f"Failed to extract fixture ID: {e}")
            return None
    
    def _extract_team_id(self, fixture: Dict, team_type: str) -> Optional[int]:
        """Extract team ID from fixture data"""
        try:
            # Try different possible keys
            possible_keys = [
                f'teams.{team_type}.id',
                f'{team_type}Team.id',
                f'{team_type}_team_id'
            ]
            
            for key in possible_keys:
                if '.' in key:
                    parts = key.split('.')
                    value = fixture
                    for part in parts:
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        else:
                            value = None
                            break
                else:
                    value = fixture.get(key)
                
                if value and isinstance(value, int):
                    return value
            
            return None
        except Exception as e:
            logger.debug(f"Failed to extract {team_type} team ID: {e}")
            return None
    
    async def _generate_predictions(self, home_team_id: int, away_team_id: int,
                                  elo_model, xg_model, corners_model) -> Optional[Dict]:
        """Generate predictions for a fixture"""
        try:
            # ELO predictions
            home_win_prob, draw_prob, away_win_prob = elo_model.predict_match_result(home_team_id, away_team_id)
            
            # xG predictions (simplified)
            home_xg, away_xg = 1.5, 1.2  # Default values
            
            # Corners predictions (simplified)
            home_corners, away_corners = 5.5, 4.8  # Default values
            
            predictions = {
                'match_result': {
                    'home_win': home_win_prob,
                    'draw': draw_prob,
                    'away_win': away_win_prob
                },
                'goals': {
                    'home_xg': home_xg,
                    'away_xg': away_xg,
                    'total_xg': home_xg + away_xg
                },
                'corners': {
                    'home_corners': home_corners,
                    'away_corners': away_corners,
                    'total_corners': home_corners + away_corners
                }
            }
            
            return predictions
            
        except Exception as e:
            logger.debug(f"Failed to generate predictions: {e}")
            return None
    
    async def _get_odds_data(self, fixture_id: int) -> Optional[Dict]:
        """Get odds data for a fixture"""
        try:
            from api.unified_api_client import UnifiedAPIClient
            
            api_client = UnifiedAPIClient()
            odds_data = await api_client.get_match_odds(fixture_id)
            
            return odds_data
            
        except Exception as e:
            logger.debug(f"Failed to get odds data: {e}")
            return None
    
    def _analyze_fixture_value_bets(self, fixture: Dict, predictions: Dict, 
                                   odds_data: Dict, value_analyzer) -> List[Dict]:
        """Analyze a single fixture for value bets"""
        value_bets = []
        
        try:
            # Extract team names
            home_team = self._extract_team_name(fixture, 'home')
            away_team = self._extract_team_name(fixture, 'away')
            competition = self._extract_competition_name(fixture)
            
            # Analyze match result bets
            if 'match_result' in predictions and odds_data:
                match_odds = self._extract_match_odds(odds_data)
                
                for outcome, prob in predictions['match_result'].items():
                    if outcome in match_odds:
                        odds = match_odds[outcome]
                        edge = value_analyzer.calculate_value_edge(prob, odds)
                        
                        if edge >= config.VALUE_BET_THRESHOLD:
                            value_bet = {
                                'fixture_id': self._extract_fixture_id(fixture),
                                'home_team': home_team,
                                'away_team': away_team,
                                'competition': competition,
                                'market': 'match_result',
                                'selection': outcome,
                                'odds': odds,
                                'model_probability': prob,
                                'edge': edge,
                                'stake_units': self._calculate_stake_units(edge)
                            }
                            value_bets.append(value_bet)
            
            return value_bets
            
        except Exception as e:
            logger.debug(f"Failed to analyze fixture value bets: {e}")
            return []
    
    def _extract_team_name(self, fixture: Dict, team_type: str) -> str:
        """Extract team name from fixture data"""
        try:
            # Try different possible keys
            possible_keys = [
                f'teams.{team_type}.name',
                f'{team_type}Team.name',
                f'{team_type}_team_name'
            ]
            
            for key in possible_keys:
                if '.' in key:
                    parts = key.split('.')
                    value = fixture
                    for part in parts:
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        else:
                            value = None
                            break
                    
                    if value:
                        return str(value)
                else:
                    value = fixture.get(key)
                    if value:
                        return str(value)
            
            return f"Unknown {team_type.title()} Team"
        except Exception as e:
            logger.debug(f"Failed to extract {team_type} team name: {e}")
            return f"Unknown {team_type.title()} Team"
    
    def _extract_competition_name(self, fixture: Dict) -> str:
        """Extract competition name from fixture data"""
        try:
            # Try different possible keys
            possible_keys = [
                'league.name', 'competition.name', 'tournament.name'
            ]
            
            for key in possible_keys:
                if '.' in key:
                    parts = key.split('.')
                    value = fixture
                    for part in parts:
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        else:
                            value = None
                            break
                    
                    if value:
                        return str(value)
                else:
                    value = fixture.get(key)
                    if value:
                        return str(value)
            
            return "Unknown Competition"
        except Exception as e:
            logger.debug(f"Failed to extract competition name: {e}")
            return "Unknown Competition"
    
    def _extract_match_odds(self, odds_data: Dict) -> Dict:
        """Extract match result odds from odds data"""
        match_odds = {}
        
        try:
            # Handle different odds data formats
            if isinstance(odds_data, list):
                for odds_record in odds_data:
                    market_desc = odds_record.get('market_description', '').lower()
                    label = odds_record.get('label', '').lower()
                    odds_value = odds_record.get('dp3') or odds_record.get('value')
                    
                    if 'fulltime result' in market_desc and odds_value:
                        try:
                            odds = float(odds_value)
                            if label == 'home':
                                match_odds['home_win'] = odds
                            elif label == 'draw':
                                match_odds['draw'] = odds
                            elif label == 'away':
                                match_odds['away_win'] = odds
                        except (ValueError, TypeError):
                            continue
            
            return match_odds
            
        except Exception as e:
            logger.debug(f"Failed to extract match odds: {e}")
            return {}
    
    def _calculate_stake_units(self, edge: float) -> float:
        """Calculate stake units based on edge value"""
        if edge >= 0.15:
            return 3.0  # 1st place - highest confidence
        elif edge >= 0.10:
            return 2.0  # 2nd place - high confidence
        elif edge >= 0.08:
            return 1.0  # 3rd place - medium confidence
        elif edge >= 0.05:
            return 0.5  # 4th & 5th - lower confidence
        else:
            return 0.0  # No bet
    
    def _format_morning_digest(self, fixtures: List[Dict], value_bets: List[Dict], 
                              now_uk: datetime) -> str:
        """Format the morning digest message"""
        try:
            from utils.time import format_london_time
            
            # Header
            message = f"📅 Today ({now_uk.strftime('%d/%m')}) – Upcoming Fixtures\n\n"
            
            # Group fixtures by competition type
            uefa_fixtures = [f for f in fixtures if f.get('display_group') == 'UEFA']
            domestic_fixtures = [f for f in fixtures if f.get('display_group') == 'Domestic']
            
            # UEFA fixtures
            if uefa_fixtures:
                message += "🏆 UEFA Competitions:\n"
                for fixture in uefa_fixtures[:10]:  # Limit to first 10
                    kickoff = self._extract_kickoff_time(fixture)
                    if kickoff:
                        time_str = format_london_time(kickoff)
                        home_team = self._extract_team_name(fixture, 'home')
                        away_team = self._extract_team_name(fixture, 'away')
                        competition = self._extract_competition_name(fixture)
                        message += f"• {time_str} – {home_team} vs {away_team} ({competition})\n"
                message += "\n"
            
            # Domestic fixtures
            if domestic_fixtures:
                message += "🏠 Domestic Leagues:\n"
                for fixture in domestic_fixtures[:10]:  # Limit to first 10
                    kickoff = self._extract_kickoff_time(fixture)
                    if kickoff:
                        time_str = format_london_time(kickoff)
                        home_team = self._extract_team_name(fixture, 'home')
                        away_team = self._extract_team_name(fixture, 'away')
                        competition = self._extract_competition_name(fixture)
                        message += f"• {time_str} – {home_team} vs {away_team} ({competition})\n"
                message += "\n"
            
            # Value bets section
            if value_bets:
                message += "🎯 Value Bets:\n"
                for bet in value_bets[:5]:  # Top 5 value bets
                    home_team = bet.get('home_team', 'Unknown')
                    away_team = bet.get('away_team', 'Unknown')
                    selection = bet.get('selection', 'Unknown')
                    odds = bet.get('odds', 0)
                    edge = bet.get('edge', 0)
                    stake_units = bet.get('stake_units', 0)
                    
                    edge_percent = edge * 100
                    message += f"• {selection} | {home_team} vs {away_team} @ {odds:.2f} | Edge +{edge_percent:.1f}% | Stake {stake_units}u\n"
            else:
                message += "🎯 No value bets found for today's fixtures.\n"
            
            # Footer
            message += f"\n⏰ Next update: Tomorrow at 08:00 UK time"
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to format morning digest: {e}")
            return "❌ Error formatting morning digest"
    
    def _extract_kickoff_time(self, fixture: Dict) -> Optional[datetime]:
        """Extract kickoff time from fixture data"""
        try:
            from utils.time import to_utc
            
            # Try different possible keys
            possible_keys = [
                'fixture.date', 'date', 'kickoff', 'start_time', 'time'
            ]
            
            for key in possible_keys:
                if '.' in key:
                    parts = key.split('.')
                    value = fixture
                    for part in parts:
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        else:
                            value = None
                            break
                else:
                    value = fixture.get(key)
                
                if value:
                    if isinstance(value, str):
                        try:
                            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                            return to_utc(dt)
                        except ValueError:
                            continue
                    elif isinstance(value, datetime):
                        return to_utc(value)
            
            return None
        except Exception as e:
            logger.debug(f"Failed to extract kickoff time: {e}")
            return None
    
    async def _send_telegram_message(self, message: str):
        """Send message via Telegram bot"""
        try:
            if not self.telegram_bot:
                logger.warning("Telegram bot not available")
                return
            
            # Check message length and chunk if necessary
            if len(message) > 4096:
                # Split into chunks
                chunks = [message[i:i+4096] for i in range(0, len(message), 4096)]
                for i, chunk in enumerate(chunks):
                    await self.telegram_bot.send_message(chunk)
                    if i < len(chunks) - 1:  # Not the last chunk
                        await asyncio.sleep(1)  # Small delay between chunks
            else:
                await self.telegram_bot.send_message(message)
            
            logger.info("Morning digest sent via Telegram successfully")
            
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
    
    def get_next_run_time(self) -> datetime:
        """Get the next scheduled run time"""
        try:
            if self.scheduler.running:
                job = self.scheduler.get_job('morning_digest')
                if job:
                    return job.next_run_time
            return get_next_8am_london()
        except Exception as e:
            logger.error(f"Failed to get next run time: {e}")
            return get_next_8am_london()
    
    def get_status(self) -> Dict:
        """Get scheduler status"""
        return {
            'is_running': self.is_running,
            'next_run': self.get_next_run_time().strftime('%Y-%m-%d %H:%M:%S') if self.is_running else 'Not scheduled',
            'jobs_count': len(self.scheduler.get_jobs()) if self.scheduler.running else 0
        }
