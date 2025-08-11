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
        """Get expected goals data using correct v3 xGFixture include"""
        try:
            # Try to get xG using the xGFixture include (cleanest method)
            params = {
                'include': 'xGFixture'
            }
            
            data = await self._make_async_request(f'fixtures/{fixture_id}', params)
            if not data or 'data' not in data:
                logger.debug(f"Expected goals data not accessible for fixture {fixture_id}")
                return None
            
            fixture_data = data['data']
            if 'xGFixture' in fixture_data:
                xg_data = fixture_data['xGFixture']
                logger.info(f"Retrieved xG data for fixture {fixture_id}")
                return xg_data
            
            return None
            
        except Exception as e:
            logger.debug(f"Expected goals data failed for fixture {fixture_id}: {e}")
            return None
    
    async def get_predictions(self, fixture_id: int) -> Optional[Dict]:
        """Get predictions using correct v3 endpoint"""
        try:
            # Try predictions endpoint with proper v3 path
            params = {
                'include': 'fixture;type'
            }
            data = await self._make_async_request(f'predictions/probabilities/fixtures/{fixture_id}', params)
            if not data or 'data' not in data:
                logger.debug(f"Predictions not accessible for fixture {fixture_id}")
                return None
            
            return data['data']
            
        except Exception as e:
            logger.debug(f"Predictions failed for fixture {fixture_id}: {e}")
            return None

    def extract_match_status(self, fixture: Dict) -> str:
        """Extract match status from fixture data"""
        if 'scores' in fixture and fixture['scores']:
            for score in fixture['scores']:
                if score.get('description') == 'CURRENT':
                    return 'LIVE'
                elif score.get('description') == 'FULL_TIME':
                    return 'FINISHED'
        
        if 'starting_at' in fixture:
            start_time = fixture['starting_at']
            if start_time:
                return 'NOT_STARTED'
        
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
