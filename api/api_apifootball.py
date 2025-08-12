import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
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
        data = await self._make_async_request("odds", params)
        if not data or "response" not in data or not data["response"]:
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
        API-Football doesn't provide xG directly, but we can try statistics endpoint
        """
        try:
            # Try to get comprehensive statistics which might contain xG-like data
            stats = await self.get_fixture_statistics(fixture_id)
            if stats:
                logger.debug("Statistics available for fixture %s (can be used for xG-like analysis)", fixture_id)
                return {"statistics": stats}
            else:
                logger.debug("xG/statistics not available for fixture %s (API-Football limitation)", fixture_id)
                return None
        except Exception as e:
            logger.debug("xG retrieval failed for fixture %s: %s", fixture_id, e)
            return None

    async def get_predictions(self, fixture_id: int) -> Optional[Dict]:
        """
        GET /predictions?fixture={fixture_id}
        """
        params = {"fixture": fixture_id}
        data = await self._make_async_request("predictions", params)
        if not data or "response" not in data or not data["response"]:
            logger.debug("Predictions not accessible for fixture %s", fixture_id)
            return None
        return data["response"][0].get("predictions", data["response"][0])

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

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None
