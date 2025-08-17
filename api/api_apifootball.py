import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import aiohttp
import config

logger = logging.getLogger(__name__)

class ApiFootballClient:
    """
    API-FOOTBALL (api-sports.io) client that mirrors SportMonksClient's interface.
    Docs: https://api-sports.io/documentation/football/v3
    Base URL example: https://v3.football.api-sports.io
    Auth: header 'x-apisports-key': <API_KEY>
    """

    def __init__(self):
        self.base_url = getattr(config, "API_FOOTBALL_BASE_URL", "https://v3.football.api-sports.io")
        self.api_key = config.API_FOOTBALL_API_KEY
        # Use Asia/Karachi timezone for better date handling
        self.timezone = getattr(config, "API_FOOTBALL_TIMEZONE", "Asia/Karachi")
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = 0.0
        # Reduced rate limit for paid plans
        self.rate_limit_delay = 0.1  # 100ms between requests for paid plans

    async def _init_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    "User-Agent": "FIXORA-PRO-Betting-System/1.0",
                    "x-apisports-key": self.api_key,
                },
            )

    async def _make_async_request(self, path: str, params: Dict = None) -> Optional[Dict]:
        await self._init_session()

        # Simple rate limiting
        now = time.time()
        dt = now - self.last_request_time
        if dt < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - dt)

        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        
        # Retry logic for 429/timeout errors - lightweight with shorter delays
        max_retries = 3
        base_delay = 0.25  # Reduced from 0.5s to 0.25s
        
        for attempt in range(max_retries):
            try:
                async with self.session.get(url, params=params) as resp:
                    self.last_request_time = time.time()
                    
                    if resp.status == 200:
                        data = await resp.json()
                        
                        # Check for API-Football error responses (they return 200 with errors)
                        if "errors" in data and data.get("results", 0) == 0:
                            logger.debug("API-Football returned errors: %s", data.get("errors"))
                            return None
                        
                        # Check if we have actual data
                        if "response" not in data:
                            logger.debug("No 'response' field in API-Football response: %s", data.keys())
                            return None
                        
                        # Log successful responses for debugging
                        logger.debug("API-Football %s successful: %d results", path, data.get("results", 0))
                        return data
                    
                    elif resp.status == 429:  # Rate limit exceeded
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)  # 0.25s, 0.5s, 1s
                            logger.debug("Rate limit exceeded (429), retrying in %.2fs (attempt %d/%d)", delay, attempt + 1, max_retries)
                            await asyncio.sleep(delay)
                            continue
                        else:
                            logger.warning("Rate limit exceeded (429) after %d retries", max_retries)
                            return None
                    
                    elif resp.status == 408 or resp.status == 504:  # Timeout errors
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)
                            logger.debug("Timeout error (%d), retrying in %.2fs (attempt %d/%d)", resp.status, delay, attempt + 1, max_retries)
                            await asyncio.sleep(delay)
                            continue
                        else:
                            logger.debug("Timeout error (%d) after %d retries", resp.status, max_retries)
                            return None
                    
                    else:
                        text = await resp.text()
                        logger.debug("API-Football request failed %s %s -> %s %s", url, params, resp.status, text)
                        return None
                        
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.debug("Request timeout, retrying in %.2fs (attempt %d/%d)", delay, attempt + 1, max_retries)
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.debug("Request timeout after %d retries", max_retries)
                    return None
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.debug("Request error: %s, retrying in %.2fs (attempt %d/%d)", e, delay, attempt + 1, max_retries)
                    await asyncio.sleep(delay)
                    continue
                else:
                    logger.debug("API-Football request error after %d retries: %s", max_retries, e)
                    return None
        
        return None

    # ---------- Public methods (mirror SportMonksClient) ----------

    async def get_today_matches(self, include_live: bool = True) -> List[Dict]:
        """
        GET /fixtures?date=YYYY-MM-DD&timezone=...
        """
        # Use proper timezone-aware date
        try:
            from datetime import datetime
            import pytz
            
            # Get current date in Asia/Karachi timezone
            tz = pytz.timezone(self.timezone)
            day = datetime.now(tz).strftime("%Y-%m-%d")
        except ImportError:
            # Fallback to UTC if pytz not available
            day = datetime.now().strftime("%Y-%m-%d")
            logger.warning("pytz not available, using UTC timezone")
        
        params = {"date": day, "timezone": self.timezone}
        logger.info("Fetching today's matches for date: %s (timezone: %s)", day, self.timezone)
        
        data = await self._make_async_request("fixtures", params)
        if not data or "response" not in data:
            logger.warning("No data returned for today's matches")
            return []
        
        fixtures = data["response"]
        logger.info("Found %d fixtures for today (%s)", len(fixtures), day)
        
        # Add provider tag for consistency
        for fixture in fixtures:
            fixture["_provider"] = "api_football"
        
        return fixtures

    async def get_matches_in_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        GET /fixtures?date=YYYY-MM-DD&timezone=... for date range
        """
        try:
            from datetime import datetime
            import pytz
            
            # Get current date in Asia/Karachi timezone
            tz = pytz.timezone(self.timezone)
            current_date = datetime.now(tz)
            
            # Parse start and end dates
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            all_matches = []
            
            # Iterate through each date in the range
            current_dt = start_dt
            while current_dt <= end_dt:
                day = current_dt.strftime("%Y-%m-%d")
                params = {"date": day, "timezone": self.timezone}
                
                logger.info("Fetching matches for date: %s (timezone: %s)", day, self.timezone)
                
                data = await self._make_async_request("fixtures", params)
                if data and "response" in data:
                    fixtures = data["response"]
                    logger.info("Found %d fixtures for %s", len(fixtures), day)
                    
                    # Add provider tag and date for consistency
                    for fixture in fixtures:
                        fixture["_provider"] = "api_football"
                        fixture["_date"] = day
                    
                    all_matches.extend(fixtures)
                
                # Move to next day (using timedelta to avoid month boundary issues)
                current_dt = current_dt + timedelta(days=1)
                
                # Rate limiting between requests
                await asyncio.sleep(0.1)
            
            logger.info("Total matches found for date range %s to %s: %d", start_date, end_date, len(all_matches))
            return all_matches
            
        except Exception as e:
            logger.error(f"Failed to get matches in date range: {e}")
            return []

    async def get_live_scores(self) -> List[Dict]:
        """
        GET /fixtures?live=all&timezone=...
        """
        params = {"live": "all", "timezone": self.timezone}
        data = await self._make_async_request("fixtures", params)
        if not data or "response" not in data:
            logger.warning("No data returned for live scores")
            return []
        
        live = data["response"]
        logger.info("Retrieved %d live matches", len(live))
        
        # Add provider tag for consistency
        for fixture in live:
            fixture["_provider"] = "api_football"
        
        return live

    async def get_fixture_details(self, fixture_id: int) -> Optional[Dict]:
        """
        Core details: GET /fixtures?id={fixture_id}
        """
        params = {"id": fixture_id, "timezone": self.timezone}
        data = await self._make_async_request("fixtures", params)
        if not data or "response" not in data or not data["response"]:
            logger.warning("No data returned for fixture %s", fixture_id)
            return None
        return data["response"][0]

    async def get_match_odds(self, fixture_id: int) -> List[Dict]:
        """
        Pre-match odds: GET /odds?fixture={fixture_id}
        """
        params = {"fixture": fixture_id}
        
        # Try the standard odds endpoint first
        data = await self._make_async_request("odds", params)
        
        # Enhanced debug logging to see what's actually returned
        logger.info(f"Raw API response for fixture {fixture_id}: {type(data)} - {data is not None}")
        if data:
            logger.info(f"API response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            if "response" in data:
                logger.info(f"Response data for fixture {fixture_id}: {type(data['response'])} - {len(data['response']) if isinstance(data['response'], list) else 'not a list'}")
                if isinstance(data['response'], list) and len(data['response']) > 0:
                    logger.info(f"First odds item: {data['response'][0]}")
            if "errors" in data:
                logger.warning(f"API errors for fixture {fixture_id}: {data['errors']}")
            if "results" in data:
                logger.info(f"API results count for fixture {fixture_id}: {data['results']}")
        else:
            logger.warning(f"No data returned from API for fixture {fixture_id}")
        
        # If standard odds endpoint fails, try alternative approaches
        if not data or "response" not in data or not data["response"]:
            logger.info(f"Standard odds endpoint failed for fixture {fixture_id}, trying alternatives...")
            
            # Try to get fixture details to see if the fixture exists
            fixture_details = await self.get_fixture_details(fixture_id)
            if fixture_details:
                logger.info(f"Fixture {fixture_id} exists but no odds available")
                
                # Try to get odds for the league instead
                league_id = fixture_details.get('league', {}).get('id')
                if league_id:
                    logger.info(f"Trying to get odds for league {league_id} instead of fixture {fixture_id}")
                    league_params = {"league": league_id, "season": datetime.now().year}
                    league_odds = await self._make_async_request("odds", league_params)
                    if league_odds and "response" in league_odds and league_odds["response"]:
                        logger.info(f"Found {len(league_odds['response'])} odds for league {league_id}")
                        # Filter odds for this specific fixture
                        fixture_odds = [odds for odds in league_odds["response"] if odds.get('fixture', {}).get('id') == fixture_id]
                        if fixture_odds:
                            logger.info(f"Found {len(fixture_odds)} odds for fixture {fixture_id} from league odds")
                            return fixture_odds
                        else:
                            logger.info(f"No odds found for fixture {fixture_id} in league {league_id} odds")
                    else:
                        logger.info(f"No odds available for league {league_id}")
                else:
                    logger.info(f"Could not extract league ID from fixture {fixture_id}")
            else:
                logger.warning(f"Fixture {fixture_id} not found")
            
            logger.debug("No odds available for fixture %s", fixture_id)
            return []
        
        return data["response"]

    async def get_live_odds(self, fixture_id: int) -> List[Dict]:
        """
        Live odds: GET /odds/live?fixture={fixture_id}
        """
        params = {"fixture": fixture_id}
        data = await self._make_async_request("odds/live", params)
        if not data or "response" not in data or not data["response"]:
            logger.debug("No live odds available for fixture %s", fixture_id)
            return []
        return data["response"]

    async def get_team_form(self, team_id: int, limit: int = 5) -> List[Dict]:
        """
        Recent fixtures for team: GET /fixtures?team={team_id}&last={limit}
        """
        params = {"team": team_id, "last": limit, "timezone": self.timezone}
        data = await self._make_async_request("fixtures", params)
        if not data or "response" not in data:
            logger.warning("No recent fixtures available for team %s", team_id)
            return []
        return data["response"]

    async def get_team_statistics(self, fixture_id: int, team_id: int) -> Optional[Dict]:
        """
        Get detailed team statistics for a specific fixture and team
        This can include possession, shots, cards, etc.
        """
        try:
            params = {"fixture": fixture_id, "team": team_id}
            data = await self._make_async_request("fixtures/statistics", params)
            if data and "response" in data and data["response"]:
                logger.debug("Team statistics available for fixture %s, team %s", fixture_id, team_id)
                return data["response"]
            else:
                logger.debug("Team statistics not available for fixture %s, team %s", fixture_id, team_id)
                return None
        except Exception as e:
            logger.debug("Team statistics retrieval failed for fixture %s, team %s: %s", fixture_id, team_id, e)
            return None

    async def get_fixture_statistics(self, fixture_id: int) -> Optional[Dict]:
        """
        Get comprehensive statistics for both teams in a fixture
        """
        try:
            # First get fixture details to extract team IDs
            fixture_details = await self.get_fixture_details(fixture_id)
            if not fixture_details:
                logger.debug("Could not get fixture details for statistics: %s", fixture_id)
                return None
            
            teams = fixture_details.get('teams', {})
            home_team_id = teams.get('home', {}).get('id')
            away_team_id = teams.get('away', {}).get('id')
            
            if not home_team_id or not away_team_id:
                logger.debug("Could not extract team IDs from fixture %s: home=%s, away=%s", 
                           fixture_id, home_team_id, away_team_id)
                return None
            
            # Get statistics for both teams
            home_stats = await self.get_team_statistics(fixture_id, home_team_id)
            away_stats = await self.get_team_statistics(fixture_id, away_team_id)
            
            if home_stats or away_stats:
                result = {
                    'home_team': home_stats,
                    'away_team': away_stats,
                    'fixture_id': fixture_id
                }
                logger.debug("Retrieved statistics for fixture %s: home=%s, away=%s", 
                           fixture_id, bool(home_stats), bool(away_stats))
                return result
            else:
                logger.debug("No statistics available for fixture %s", fixture_id)
                return None
                
        except Exception as e:
            logger.debug("Fixture statistics retrieval failed for fixture %s: %s", fixture_id, e)
            return None

    async def get_expected_goals(self, fixture_id: int) -> Optional[Dict]:
        """
        Expected goals data - API-Football doesn't provide xG directly
        """
        try:
            # Try to get fixture statistics which might contain xG-like data
            stats = await self.get_fixture_statistics(fixture_id)
            if stats:
                logger.debug(f"Retrieved statistics for fixture {fixture_id} (can be used for xG estimation)")
                return {"statistics": stats, "source": "statistics"}
            
            # Fallback: try to get team form data for estimation
            fixture = await self.get_fixture_details(fixture_id)
            if fixture and "teams" in fixture:
                home_team_id = fixture["teams"]["home"]["id"]
                away_team_id = fixture["teams"]["away"]["id"]
                
                # Get recent form for both teams
                home_form = await self.get_team_form(home_team_id, limit=5)
                away_form = await self.get_team_form(away_team_id, limit=5)
                
                if home_form or away_form:
                    logger.debug(f"Retrieved team form data for fixture {fixture_id} (can be used for xG estimation)")
                    return {
                        "home_form": home_form,
                        "away_form": away_form,
                        "source": "team_form"
                    }
            
            logger.debug(f"xG data not available for fixture {fixture_id} - this may be a plan limitation")
            return None
            
        except Exception as e:
            logger.debug(f"Error getting expected goals for fixture {fixture_id}: {e}")
            return None

    async def get_predictions(self, fixture_id: int) -> Optional[Dict]:
        """
        GET /predictions?fixture={fixture_id}
        """
        params = {"fixture": fixture_id}
        data = await self._make_async_request("predictions", params)
        if not data or "response" not in data or not data["response"]:
            logger.debug(f"Predictions not accessible for fixture {fixture_id}")
            return None
        return data["response"][0].get("predictions", data["response"][0])

    async def get_events_for_roi(self, start_date: str, end_date: str, league_id: int = None) -> List[Dict]:
        """
        Fetch finished fixtures for ROI calculation within a date range
        GET /fixtures?from=YYYY-MM-DD&to=YYYY-MM-DD&timezone=Asia/Karachi
        """
        try:
            params = {
                "from": start_date,
                "to": end_date,
                "timezone": self.timezone
            }
            
            # Add league filter if specified
            if league_id:
                params["league"] = league_id
            
            logger.info(f"Fetching finished fixtures for ROI: {start_date} to {end_date} (league_id: {league_id})")
            
            data = await self._make_async_request("fixtures", params)
            if not data or "response" not in data:
                logger.warning(f"No fixtures data available for date range {start_date} to {end_date}")
                return []
            
            fixtures = data["response"]
            
            # Filter for finished fixtures only (FT, AET, PEN)
            finished_fixtures = []
            for fixture in fixtures:
                status = fixture.get("fixture", {}).get("status", {}).get("short", "")
                if status in ["FT", "AET", "PEN"]:
                    # Add provider tag and date for consistency
                    fixture["_provider"] = "api_football"
                    fixture["_date"] = start_date
                    finished_fixtures.append(fixture)
            
            logger.info(f"Retrieved {len(finished_fixtures)} finished fixtures for ROI calculation")
            return finished_fixtures
            
        except Exception as e:
            logger.error(f"Error fetching events for ROI: {e}")
            return []

    async def get_odds_for_roi(self, start_date: str, end_date: str, league_id: int = None) -> List[Dict]:
        """
        Fetch pre-match odds for ROI calculation within a date range
        GET /odds?from=YYYY-MM-DD&to=YYYY-MM-DD
        """
        try:
            params = {
                "from": start_date,
                "to": end_date
            }
            
            # Add league filter if specified
            if league_id:
                params["league"] = league_id
            
            logger.info(f"Fetching odds for ROI: {start_date} to {end_date} (league_id: {league_id})")
            
            data = await self._make_async_request("odds", params)
            if not data or "response" not in data:
                logger.warning(f"No odds data available for date range {start_date} to {end_date}")
                return []
            
            odds_data = data["response"]
            
            # Add provider tag and date for consistency
            for odds_record in odds_data:
                odds_record["_provider"] = "api_football"
                odds_record["_date"] = start_date
            
            logger.info(f"Retrieved {len(odds_data)} odds records for ROI calculation")
            return odds_data
            
        except Exception as e:
            logger.error(f"Error fetching odds for ROI: {e}")
            return []

    async def get_complete_roi_data(self, start_date: str, end_date: str, league_id: int = None) -> Dict:
        """
        Get complete ROI data combining events and odds for a date range
        """
        try:
            # Fetch both events and odds
            events = await self.get_events_for_roi(start_date, end_date, league_id)
            odds = await self.get_odds_for_roi(start_date, end_date, league_id)
            
            # Create a mapping of fixture_id to odds
            odds_map = {}
            for odds_record in odds:
                fixture_id = odds_record.get("fixture", {}).get("id")
                if fixture_id:
                    odds_map[fixture_id] = odds_record
            
            # Combine events with their corresponding odds
            combined_data = []
            for event in events:
                fixture_id = event.get("fixture", {}).get("id")
                event_odds = odds_map.get(fixture_id, {})
                
                combined_record = {
                    "event": event,
                    "odds": event_odds,
                    "fixture_id": fixture_id,
                    "has_odds": bool(event_odds),
                    "_provider": "api_football",
                    "_date": start_date
                }
                combined_data.append(combined_record)
            
            return {
                "data": combined_data,
                "metadata": {
                    "provider": "api_football",
                    "start_date": start_date,
                    "end_date": end_date,
                    "league_id": league_id,
                    "total_events": len(events),
                    "events_with_odds": sum(1 for record in combined_data if record["has_odds"])
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching complete ROI data: {e}")
            return {
                "data": [],
                "metadata": {
                    "provider": "api_football",
                    "start_date": start_date,
                    "end_date": end_date,
                    "league_id": league_id,
                    "total_events": 0,
                    "events_with_odds": 0,
                    "error": str(e)
                }
            }

    async def get_league_odds(self, league_id: int, season: int = None) -> List[Dict]:
        """
        Get odds for a specific league: GET /odds?league={league_id}&season={season}
        This is often more reliable than getting odds for individual fixtures
        """
        if season is None:
            season = datetime.now().year
        
        params = {"league": league_id, "season": season}
        data = await self._make_async_request("odds", params)
        
        logger.info(f"🔍 League odds for league {league_id}, season {season}: {type(data)} - {data is not None}")
        if data:
            logger.info(f"🔍 League odds response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            if "response" in data:
                logger.info(f"🔍 League odds count: {len(data['response']) if isinstance(data['response'], list) else 'not a list'}")
                if isinstance(data['response'], list) and len(data['response']) > 0:
                    logger.info(f"🔍 First league odds item: {data['response'][0]}")
            if "errors" in data:
                logger.warning(f"🔍 League odds API errors: {data['errors']}")
            if "results" in data:
                logger.info(f"🔍 League odds API results count: {data['results']}")
        
        if not data or "response" not in data or not data["response"]:
            logger.warning(f"🔍 No odds available for league {league_id}, season {season}")
            return []
        
        return data["response"]

    async def get_fixtures_for_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Get fixtures for a specific date range: GET /fixtures?from={start_date}&to={end_date}
        """
        params = {"from": start_date, "to": end_date, "timezone": self.timezone}
        data = await self._make_async_request("fixtures", params)
        
        logger.info(f"🔍 Fixtures for date range {start_date} to {end_date}: {type(data)} - {data is not None}")
        if data:
            logger.info(f"🔍 Fixtures response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            if "response" in data:
                logger.info(f"🔍 Fixtures count: {len(data['response']) if isinstance(data['response'], list) else 'not a list'}")
                if isinstance(data['response'], list) and len(data['response']) > 0:
                    logger.info(f"🔍 First fixture: {data['response'][0].get('fixture', {}).get('id', 'unknown')}")
            if "errors" in data:
                logger.warning(f"🔍 Fixtures API errors: {data['errors']}")
            if "results" in data:
                logger.info(f"🔍 Fixtures API results count: {data['results']}")
        
        if not data or "response" not in data or not data["response"]:
            logger.warning(f"🔍 No fixtures available for date range {start_date} to {end_date}")
            return []
        
        return data["response"]

    # ---------- Helpers to match your analyzer's expectations ----------

    def extract_match_status(self, fixture: Dict) -> str:
        """
        Map API-FOOTBALL's status.short to your labels.
        """
        status = (fixture.get("fixture", {}).get("status", {}) or {})
        short = (status.get("short") or "").upper()
        if short in {"1H", "2H", "ET", "P", "BT", "HT"}:
            return "LIVE"
        if short in {"FT", "AET", "PEN"}:
            return "FINISHED"
        if short in {"NS", "TBD", "PST", "CANC"}:
            return "NOT_STARTED" if short == "NS" else short
        return "UNKNOWN"

    def extract_team_names(self, fixture: Dict) -> Tuple[str, str]:
        teams = fixture.get("teams", {})
        return (
            (teams.get("home", {}) or {}).get("name", "Unknown"),
            (teams.get("away", {}) or {}).get("name", "Unknown"),
        )

    def extract_score(self, fixture: Dict) -> Tuple[int, int]:
        goals = fixture.get("goals", {}) or {}
        return goals.get("home", 0) or 0, goals.get("away", 0) or 0

    def extract_fixture_id(self, fixture: Dict) -> Optional[int]:
        """
        Extract fixture ID from API-Football response structure
        """
        # API-Football structure: fixture.id
        fixture_data = fixture.get("fixture", {})
        if fixture_data and "id" in fixture_data:
            return fixture_data["id"]
        
        # Fallback to direct id field
        if "id" in fixture:
            return fixture["id"]
        
        return None

    async def cleanup(self):
        """Clean up resources and close sessions"""
        try:
            if self.session and not self.session.closed:
                await self.session.close()
                logger.info("✅ API-Football session closed")
        except Exception as e:
            logger.warning(f"⚠️ Warning during API-Football cleanup: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            if hasattr(self, 'session') and self.session and not self.session.closed:
                logger.warning("API-Football destructor called without cleanup")
        except:
            pass
