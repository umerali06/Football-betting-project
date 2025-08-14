import requests
import time
from typing import Dict, List, Optional, Tuple
import config
import logging
from datetime import datetime, timedelta
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class SportMonksClient:
    def __init__(self):
        self.base_url = config.SPORTMONKS_BASE_URL
        self.api_token = config.SPORTMONKS_API_KEY
        self.session = None
        self.last_request_time = 0
        self.rate_limit_delay = 0.1

    async def _init_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'User-Agent': 'FIXORA-PRO-Betting-System/1.0'}
            )

    async def _make_async_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make an asynchronous API request with rate limiting"""
        await self._init_session()
        
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        
        try:
            # Add API token to params
            if params is None:
                params = {}
            params['api_token'] = self.api_token
            
            url = f"{self.base_url}/{endpoint}"
            logger.debug(f"Making request to: {url}")
            
            async with self.session.get(url, params=params) as response:
                self.last_request_time = time.time()
                
                if response.status == 200:
                    data = await response.json()
                    return data
                elif response.status == 403:
                    error_data = await response.json()
                    logger.error(f"API access denied: {error_data.get('message', 'Unknown error')}")
                    return None
                elif response.status == 404:
                    error_data = await response.json()
                    logger.error(f"API request failed: {response.status} - {error_data}")
                    return None
                else:
                    error_data = await response.text()
                    logger.error(f"API request failed: {response.status} - {error_data}")
                return None
                
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None
    
    async def get_today_matches(self, include_live: bool = True) -> List[Dict]:
        """Get today's matches using the correct v3 date endpoint"""
        from datetime import datetime
        
        # Get today's date in YYYY-MM-DD format
        today = datetime.now().strftime('%Y-%m-%d')
        
        params = {
            'include': 'scores;participants;league;venue'
        }
        
        data = await self._make_async_request(f'fixtures/date/{today}', params)
        if not data or 'data' not in data:
            logger.warning("No data returned for today's matches")
            return []
        
        fixtures = data['data']
        logger.info(f"Found {len(fixtures)} fixtures for today")
        return fixtures

    async def get_live_scores(self) -> List[Dict]:
        """Get live matches using the correct v3 endpoint"""
        params = {
            'include': 'scores;participants;league;venue'
        }
        
        data = await self._make_async_request('livescores/inplay', params)
        if not data or 'data' not in data:
            logger.warning("No data returned for live scores")
            return []
        
        live_matches = data['data']
        logger.info(f"Retrieved {len(live_matches)} live matches")
        return live_matches

    async def get_fixture_details(self, fixture_id: int) -> Optional[Dict]:
        """Get detailed fixture information using correct v3 includes"""
        params = {
            'include': 'scores;participants;league;season;venue;statistics'
        }
        
        data = await self._make_async_request(f'fixtures/{fixture_id}', params)
        if not data or 'data' not in data:
            logger.warning(f"No data returned for fixture {fixture_id}")
            return None
        
        logger.info(f"Retrieved detailed data for fixture {fixture_id}")
        return data['data']

    async def get_match_odds(self, fixture_id: int) -> List[Dict]:
        """Get match odds using correct v3 endpoint and includes"""
        params = {
            'include': 'bookmaker;market'
        }
        
        data = await self._make_async_request(f'odds/pre-match/fixtures/{fixture_id}', params)
        
        if not data or 'data' not in data:
            logger.warning(f"No odds available for fixture {fixture_id}")
            return []
        
        odds = data['data']
        logger.info(f"Retrieved {len(odds)} odds for fixture {fixture_id}")
        return odds

    async def get_team_form(self, team_id: int, limit: int = 5) -> List[Dict]:
        """Get team form using documented v3 approach with date ranges"""
        try:
            from datetime import datetime, timedelta
            
            # Calculate date range for last 120 days (to get enough finished fixtures)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=120)
            
            # Format dates as YYYY-MM-DD
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            params = {
                'include': 'scores;participants'
            }
            
            # Use the documented v3 endpoint for fixtures between dates
            data = await self._make_async_request(f'fixtures/between/{start_str}/{end_str}/{team_id}', params)
            if data and 'data' in data:
                all_fixtures = data['data']
                
                # Filter for finished fixtures and take the latest ones
                finished_fixtures = []
                for fixture in all_fixtures:
                    if 'scores' in fixture and fixture['scores']:
                        for score in fixture['scores']:
                            if score.get('description') == 'FULL_TIME':
                                finished_fixtures.append(fixture)
                                break
                
                # Sort by date and take the latest limit
                if finished_fixtures:
                    # Sort by starting_at date (most recent first)
                    finished_fixtures.sort(key=lambda x: x.get('starting_at', ''), reverse=True)
                    latest_fixtures = finished_fixtures[:limit]
                    
                    logger.info(f"Retrieved {len(latest_fixtures)} recent finished fixtures for team {team_id}")
                    return latest_fixtures
            
            logger.warning(f"No recent fixtures available for team {team_id}")
            return []
    
        except Exception as e:
            logger.debug(f"Team form API failed for team {team_id}: {e}")
            return []
    
    async def get_expected_goals(self, fixture_id: int) -> Optional[Dict]:
        """Get expected goals data with multiple fallback strategies"""
        try:
            # Strategy 1: Try to get xG using the xGFixture include (cleanest method)
            params = {
                'include': 'xGFixture'
            }
            
            data = await self._make_async_request(f'fixtures/{fixture_id}', params)
            if not data or 'data' not in data:
                logger.debug(f"xGFixture include not accessible for fixture {fixture_id}")
                # Don't return None yet - try alternative strategies
            else:
                fixture_data = data['data']
                if 'xGFixture' in fixture_data and fixture_data['xGFixture']:
                    xg_data = fixture_data['xGFixture']
                    logger.info(f"Retrieved xG data via xGFixture for fixture {fixture_id}")
                    return xg_data
            
            # Strategy 2: Try to get statistics which might contain xG-like data
            try:
                stats_params = {
                    'include': 'statistics;statistics.type'
                }
                stats_data = await self._make_async_request(f'fixtures/{fixture_id}', stats_params)
                if stats_data and 'data' in stats_data:
                    fixture_data = stats_data['data']
                    if 'statistics' in fixture_data and fixture_data['statistics']:
                        logger.debug(f"Retrieved statistics data for fixture {fixture_id} (can be used for xG-like analysis)")
                        return {"statistics": fixture_data['statistics'], "source": "statistics"}
            except Exception as e:
                logger.debug(f"Statistics fallback failed for fixture {fixture_id}: {e}")
            
            # Strategy 3: Try to get team form data which can be used for xG estimation
            try:
                # Get home and away team IDs from the fixture
                fixture_info = await self._make_async_request(f'fixtures/{fixture_id}', {'include': 'participants'})
                if fixture_info and 'data' in fixture_info:
                    fixture_data = fixture_info['data']
                    if 'participants' in fixture_data:
                        participants = fixture_data['participants']
                        home_team_id = None
                        away_team_id = None
                        
                        for participant in participants:
                            if participant.get('meta', {}).get('location') == 'home':
                                home_team_id = participant.get('participant_id')
                            elif participant.get('meta', {}).get('location') == 'away':
                                away_team_id = participant.get('participant_id')
                        
                        if home_team_id and away_team_id:
                            # Get recent form for both teams
                            home_form = await self.get_team_form(home_team_id)
                            away_form = await self.get_team_form(away_team_id)
                            
                            if home_form or away_form:
                                logger.debug(f"Retrieved team form data for fixture {fixture_id} (can be used for xG estimation)")
                                return {
                                    "home_form": home_form,
                                    "away_form": away_form,
                                    "source": "team_form"
                                }
            except Exception as e:
                logger.debug(f"Team form fallback failed for fixture {fixture_id}: {e}")
            
            # If all strategies fail, log the limitation
            logger.debug(f"All xG data strategies failed for fixture {fixture_id} - this may be a plan limitation")
            return None
            
        except Exception as e:
            # Check if this is an API access denied error
            if "access denied" in str(e).lower() or "403" in str(e):
                logger.debug(f"xG data access denied for fixture {fixture_id} (plan limitation - xGFixture include not available)")
            else:
                logger.debug(f"Expected goals data failed for fixture {fixture_id}: {e}")
            return None
    
    async def get_predictions(self, fixture_id: int) -> Optional[Dict]:
        """Get predictions with multiple fallback strategies for plan limitations"""
        try:
            # Strategy 1: Try predictions endpoint with proper v3 path
            params = {
                'include': 'fixture;type'
            }
            data = await self._make_async_request(f'predictions/probabilities/fixtures/{fixture_id}', params)
            if data and 'data' in data and data['data']:
                logger.debug(f"Predictions retrieved via probabilities endpoint for fixture {fixture_id}")
                return data['data']
            else:
                logger.debug(f"Predictions probabilities endpoint returned empty for fixture {fixture_id}")
            
            # Strategy 2: Try value bets endpoint (alternative predictions source)
            try:
                value_bets_data = await self._make_async_request(f'predictions/value-bets/fixtures/{fixture_id}', params)
                if value_bets_data and 'data' in value_bets_data and value_bets_data['data']:
                    logger.debug(f"Value bets predictions retrieved for fixture {fixture_id}")
                    return {"value_bets": value_bets_data['data'], "source": "value_bets"}
            except Exception as e:
                logger.debug(f"Value bets predictions failed for fixture {fixture_id}: {e}")
            
            # Strategy 3: Try to get team form data which can be used for prediction-like analysis
            try:
                # Get home and away team IDs from the fixture
                fixture_info = await self._make_async_request(f'fixtures/{fixture_id}', {'include': 'participants'})
                if fixture_info and 'data' in fixture_info:
                    fixture_data = fixture_info['data']
                    if 'participants' in fixture_data:
                        participants = fixture_data['participants']
                        home_team_id = None
                        away_team_id = None
                        
                        for participant in participants:
                            if participant.get('meta', {}).get('location') == 'home':
                                home_team_id = participant.get('participant_id')
                            elif participant.get('meta', {}).get('location') == 'away':
                                away_team_id = participant.get('participant_id')
                        
                        if home_team_id and away_team_id:
                            # Get recent form for both teams
                            home_form = await self.get_team_form(home_team_id)
                            away_form = await self.get_team_form(away_team_id)
                            
                            if home_form or away_form:
                                logger.debug(f"Team form data retrieved for fixture {fixture_id} (can be used for prediction-like analysis)")
                                return {
                                    "home_form": home_form,
                                    "away_form": away_form,
                                    "source": "team_form_predictions"
                                }
            except Exception as e:
                logger.debug(f"Team form predictions fallback failed for fixture {fixture_id}: {e}")
            
            # Strategy 4: Try to get head-to-head data which can be used for predictions
            try:
                if home_team_id and away_team_id:
                    # Get head-to-head matches between these teams
                    h2h_data = await self._make_async_request(f'teams/{home_team_id}/fixtures/between/2024-01-01/2024-12-31/{away_team_id}')
                    if h2h_data and 'data' in h2h_data and h2h_data['data']:
                        logger.debug(f"Head-to-head data retrieved for fixture {fixture_id} (can be used for prediction-like analysis)")
                        return {"head_to_head": h2h_data['data'], "source": "h2h_predictions"}
            except Exception as e:
                logger.debug(f"Head-to-head predictions fallback failed for fixture {fixture_id}: {e}")
            
            # If all strategies fail, log the limitation
            logger.debug(f"All prediction strategies failed for fixture {fixture_id} - this may be a plan limitation")
            return None
            
        except Exception as e:
            # Check if this is an API access denied error
            if "access denied" in str(e).lower() or "403" in str(e):
                logger.debug(f"Predictions access denied for fixture {fixture_id} (plan limitation)")
            else:
                logger.debug(f"Predictions failed for fixture {fixture_id}: {e}")
            return None
    
    def extract_match_status(self, fixture: Dict) -> str:
        """Extract match status from fixture data with multiple fallbacks"""
        # Method 1: Check scores array for CURRENT status
        if 'scores' in fixture and fixture['scores']:
            for score in fixture['scores']:
                if score.get('description') == 'CURRENT':
                    return 'LIVE'
                elif score.get('description') == 'FULL_TIME':
                    return 'FINISHED'
        
        # Method 2: Check time.status field (v3 schema)
        if 'time' in fixture and fixture['time']:
            time_data = fixture['time']
            status = time_data.get('status', '')
            status_reason = time_data.get('status_reason', '')
            minute = time_data.get('minute')
            
            # Map various status values
            if status in ['LIVE', '1H', '2H', 'HT', 'ET', 'PEN']:
                return 'LIVE'
            elif status in ['FT', 'AET', 'PEN']:
                return 'FINISHED'
            elif status in ['NS', 'TBD']:
                return 'NOT_STARTED'
            elif minute and minute > 0:
                return 'LIVE'
        
        # Method 3: Check boolean live field
        if 'live' in fixture:
            if fixture['live']:
                return 'LIVE'
            else:
                # Check if it's finished or not started
                if 'starting_at' in fixture and 'ending_at' in fixture:
                    return 'FINISHED'
        else:
                    return 'NOT_STARTED'
        
        # Method 4: Check starting_at timestamp
        if 'starting_at' in fixture:
            start_time = fixture['starting_at']
            if start_time:
                # If we have a start time but no live indicator, assume not started
                return 'NOT_STARTED'
        
        # Method 5: Check for any live-related fields
        live_indicators = ['is_live', 'live_status', 'match_status', 'status']
        for indicator in live_indicators:
            if indicator in fixture:
                value = fixture[indicator]
                if isinstance(value, str):
                    if value.upper() in ['LIVE', '1H', '2H', 'HT', 'ET', 'PEN']:
                        return 'LIVE'
                    elif value.upper() in ['FT', 'AET', 'PEN', 'FINISHED']:
                        return 'FINISHED'
                    elif value.upper() in ['NS', 'TBD', 'NOT_STARTED']:
                        return 'NOT_STARTED'
                elif isinstance(value, bool) and value:
                    return 'LIVE'
        
        # Default fallback
        logger.debug(f"Could not determine match status for fixture, using UNKNOWN. Available fields: {list(fixture.keys())}")
        return 'UNKNOWN'

    def extract_team_names(self, fixture: Dict) -> Tuple[str, str]:
        """Extract team names from fixture participants"""
        home_team = "Unknown"
        away_team = "Unknown"
        
        if 'participants' in fixture and fixture['participants']:
            for participant in fixture['participants']:
                if participant.get('meta', {}).get('location') == 'home':
                    home_team = participant.get('name', 'Unknown')
                elif participant.get('meta', {}).get('location') == 'away':
                    away_team = participant.get('name', 'Unknown')
        
        return home_team, away_team

    def extract_score(self, fixture: Dict) -> Tuple[int, int]:
        """Extract current score from fixture"""
        home_score = 0
        away_score = 0
        
        if 'scores' in fixture and fixture['scores']:
            for score in fixture['scores']:
                if score.get('description') == 'CURRENT':
                    home_score = score.get('score', {}).get('participant_1', 0)
                    away_score = score.get('score', {}).get('participant_2', 0)
                    break
        
        return home_score, away_score

    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
