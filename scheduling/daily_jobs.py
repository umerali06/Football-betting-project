import asyncio
import logging
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Robust import handling with fallbacks
try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    APSCHEDULER_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("APScheduler imported successfully")
except ImportError as e:
    APSCHEDULER_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.error(f"APScheduler import failed: {e}")
    logger.warning("Falling back to basic time-based scheduling")

try:
    import pytz
    PYTZ_AVAILABLE = True
except ImportError:
    PYTZ_AVAILABLE = False
    logger.warning("pytz not available, using basic timezone handling")

# Local imports with error handling
try:
    from utils.time import now_london, get_next_8am_london
    TIME_UTILS_AVAILABLE = True
except ImportError as e:
    TIME_UTILS_AVAILABLE = False
    logger.error(f"Time utils import failed: {e}")

try:
    from filters.competition_filter import CompetitionFilter
    COMPETITION_FILTER_AVAILABLE = True
except ImportError as e:
    COMPETITION_FILTER_AVAILABLE = False
    logger.error(f"Competition filter import failed: {e}")

try:
    from utils.odds_filter import OddsFilter
    ODDS_FILTER_AVAILABLE = True
except ImportError as e:
    ODDS_FILTER_AVAILABLE = False
    logger.error(f"Odds filter import failed: {e}")

try:
    import config
    CONFIG_AVAILABLE = True
except ImportError as e:
    CONFIG_AVAILABLE = False
    logger.error(f"Config import failed: {e}")

class DailyJobsScheduler:
    """Robust scheduler for daily automated jobs with fallback mechanisms"""
    
    def __init__(self, telegram_bot=None):
        self.telegram_bot = telegram_bot
        self.is_running = False
        self.fallback_mode = False
        
        # Initialize components with availability checks
        if COMPETITION_FILTER_AVAILABLE:
            try:
                self.competition_filter = CompetitionFilter()
            except Exception as e:
                logger.error(f"Failed to initialize CompetitionFilter: {e}")
                self.competition_filter = None
        else:
            self.competition_filter = None
            
        if ODDS_FILTER_AVAILABLE:
            try:
                self.odds_filter = OddsFilter()
            except Exception as e:
                logger.error(f"Failed to initialize OddsFilter: {e}")
                self.odds_filter = None
        else:
            self.odds_filter = None
        
        # Initialize scheduler based on availability
        if APSCHEDULER_AVAILABLE:
            try:
                self.scheduler = AsyncIOScheduler()
                self.fallback_mode = False
                logger.info("Using APScheduler for job scheduling")
            except Exception as e:
                logger.error(f"Failed to initialize APScheduler: {e}")
                self.scheduler = None
                self.fallback_mode = True
        else:
            self.scheduler = None
            self.fallback_mode = True
            logger.warning("Running in fallback mode without APScheduler")
        
        # Fallback scheduling variables
        self.last_check = None
        self.next_8am = None
        
    async def start(self):
        """Start the scheduler with robust error handling"""
        try:
            if self.fallback_mode:
                await self._start_fallback_scheduler()
            else:
                await self._start_apscheduler()
                
            self.is_running = True
            logger.info("Daily jobs scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start primary scheduler: {e}")
            logger.info("Attempting to start fallback scheduler...")
            
            try:
                self.fallback_mode = True
                await self._start_fallback_scheduler()
                self.is_running = True
                logger.info("Fallback scheduler started successfully")
            except Exception as fallback_error:
                logger.error(f"Failed to start fallback scheduler: {fallback_error}")
                raise
    
    async def _start_apscheduler(self):
        """Start APScheduler-based scheduling"""
        if not self.scheduler:
            raise RuntimeError("APScheduler not available")
            
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
            logger.info("APScheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start APScheduler: {e}")
            raise
    
    async def _start_fallback_scheduler(self):
        """Start fallback time-based scheduling"""
        try:
            # Calculate next 8am UK time
            if TIME_UTILS_AVAILABLE:
                self.next_8am = get_next_8am_london()
            else:
                # Basic fallback calculation
                now = datetime.now()
                if now.hour >= 8:
                    # Next 8am is tomorrow
                    self.next_8am = now.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
                else:
                    # Next 8am is today
                    self.next_8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
            
            self.last_check = datetime.now()
            logger.info(f"Fallback scheduler started - next run at: {self.next_8am.strftime('%Y-%m-%d %H:%M')}")
            
        except Exception as e:
            logger.error(f"Failed to start fallback scheduler: {e}")
            raise
    
    async def check_and_run_fallback(self):
        """Check if it's time to run the morning digest (fallback mode)"""
        if not self.fallback_mode or not self.is_running:
            return
            
        try:
            now = datetime.now()
            
            # Check if we've passed 8am
            if self.next_8am and now >= self.next_8am:
                logger.info("Fallback scheduler: Time to run morning digest")
                await self.job_morning_digest()
                
                # Calculate next 8am
                if TIME_UTILS_AVAILABLE:
                    self.next_8am = get_next_8am_london()
                else:
                    self.next_8am = now.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
                
                logger.info(f"Next fallback run scheduled for: {self.next_8am.strftime('%Y-%m-%d %H:%M')}")
                
        except Exception as e:
            logger.error(f"Error in fallback scheduler check: {e}")
    
    async def stop(self):
        """Stop the scheduler"""
        try:
            if self.scheduler and self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("APScheduler stopped")
            
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
            
            # CRITICAL: Final odds filtering to ensure no bets with odds < 1.8 slip through
            value_bets = OddsFilter.filter_value_bets(value_bets)
            
            # Sort by edge value (descending)
            value_bets.sort(key=lambda x: x.get('edge', 0), reverse=True)
            
            logger.info(f"Found {len(value_bets)} value bets after odds filtering")
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
                        
                        # CRITICAL: Filter by minimum odds requirement (≥1.8)
                        if not OddsFilter.validate_odds(odds):
                            logger.debug(f"Excluding bet with invalid odds {odds} for {outcome}")
                            continue
                        
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
                            logger.info(f"Added value bet: {outcome} @ {odds:.2f} (edge: {edge:.3f})")
                        else:
                            logger.debug(f"Bet {outcome} @ {odds:.2f} failed edge threshold: {edge:.3f} < {config.VALUE_BET_THRESHOLD}")
                    else:
                        logger.debug(f"No odds available for {outcome}")
            
            return value_bets
            
        except Exception as e:
            logger.debug(f"Failed to analyze fixture value bets: {e}")
            return []
    
    def _extract_team_name(self, fixture: Dict, team_type: str) -> str:
        """Extract team name from fixture data"""
        try:
            if team_type == 'home':
                # Try different possible keys for home team
                for key in ['home_team', 'localTeam', 'home']:
                    if key in fixture:
                        team_data = fixture[key]
                        if isinstance(team_data, dict):
                            return team_data.get('name', 'Unknown')
                        elif isinstance(team_data, str):
                            return team_data
                
                # Try teams structure
                if 'teams' in fixture and 'home' in fixture['teams']:
                    return fixture['teams']['home'].get('name', 'Unknown')
                    
            elif team_type == 'away':
                # Try different possible keys for away team
                for key in ['away_team', 'visitorTeam', 'away']:
                    if key in fixture:
                        team_data = fixture[key]
                        if isinstance(team_data, dict):
                            return team_data.get('name', 'Unknown')
                        elif isinstance(team_data, str):
                            return team_data
                
                # Try teams structure
                if 'teams' in fixture and 'away' in fixture['teams']:
                    return fixture['teams']['away'].get('name', 'Unknown')
            
            return 'Unknown'
            
        except Exception as e:
            logger.debug(f"Failed to extract {team_type} team name: {e}")
            return 'Unknown'
    
    def _extract_competition_name(self, fixture: Dict) -> str:
        """Extract competition name from fixture data"""
        try:
            # Try different possible keys for competition
            for key in ['league', 'competition', 'tournament']:
                if key in fixture:
                    comp_data = fixture[key]
                    if isinstance(comp_data, dict):
                        return comp_data.get('name', 'Unknown')
                    elif isinstance(comp_data, str):
                        return comp_data
            
            return 'Unknown'
            
        except Exception as e:
            logger.debug(f"Failed to extract competition name: {e}")
            return 'Unknown'
    
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
            
            # Log odds validation summary
            if match_odds:
                OddsFilter.log_odds_validation_summary(match_odds, "Match Result")
            
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
            # Try different possible keys for kickoff time
            if 'fixture' in fixture and 'date' in fixture['fixture']:
                date_str = fixture['fixture']['date']
                if TIME_UTILS_AVAILABLE:
                    from utils.time import parse_datetime
                    return parse_datetime(date_str)
                else:
                    # Basic fallback parsing
                    try:
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        pass
            
            # Try other common keys
            for key in ['kickoff', 'start_time', 'match_time', 'scheduled']:
                if key in fixture:
                    date_str = fixture[key]
                    try:
                        if TIME_UTILS_AVAILABLE:
                            from utils.time import parse_datetime
                            return parse_datetime(date_str)
                        else:
                            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        continue
            
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
    
    def get_next_run_time(self):
        """Get the next scheduled run time"""
        try:
            if self.fallback_mode and self.next_8am:
                return self.next_8am
            elif self.scheduler and self.scheduler.running:
                # Get next run from APScheduler
                jobs = self.scheduler.get_jobs()
                for job in jobs:
                    if job.name == 'Daily Morning Digest':
                        return job.next_run_time
            return None
        except Exception as e:
            logger.error(f"Error getting next run time: {e}")
            return None
    
    def get_status(self) -> Dict:
        """Get scheduler status information"""
        try:
            status = {
                'is_running': self.is_running,
                'fallback_mode': self.fallback_mode,
                'apscheduler_available': APSCHEDULER_AVAILABLE,
                'time_utils_available': TIME_UTILS_AVAILABLE,
                'competition_filter_available': COMPETITION_FILTER_AVAILABLE,
                'odds_filter_available': ODDS_FILTER_AVAILABLE,
                'config_available': CONFIG_AVAILABLE
            }
            
            if self.fallback_mode:
                status['next_run'] = self.next_8am.isoformat() if self.next_8am else None
            else:
                status['next_run'] = self.get_next_run_time().isoformat() if self.get_next_run_time() else None
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting scheduler status: {e}")
            return {'error': str(e)}
