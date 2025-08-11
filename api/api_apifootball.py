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
        self.api_key = config.API_FOOTBALL_API_KEY  # add this to your config
        self.timezone = getattr(config, "API_FOOTBALL_TIMEZONE", "UTC")
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = 0.0
        self.rate_limit_delay = 0.15  # API-FOOTBALL free plans can be tight; adjust to your plan

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
        try:
            params = params or {}
            async with self.session.get(url, params=params) as resp:
                self.last_request_time = time.time()
                if resp.status == 200:
                    data = await resp.json()
                    # API-FOOTBALL wraps results in {"get": "...", "parameters": {...}, "results": N, "response": [...]}
                    return data
                else:
                    text = await resp.text()
                    logger.error("API-FOOTBALL request failed %s %s -> %s %s", url, params, resp.status, text)
                    return None
        except Exception as e:
            logger.error("API-FOOTBALL request error: %s", e)
            return None

    # ---------- Public methods (mirror SportMonksClient) ----------

    async def get_today_matches(self, include_live: bool = True) -> List[Dict]:
        """
        GET /fixtures?date=YYYY-MM-DD&timezone=...
        """
        day = datetime.now().strftime("%Y-%m-%d")
        params = {"date": day, "timezone": self.timezone}
        data = await self._make_async_request("fixtures", params)
        if not data or "response" not in data:
            logger.warning("No data returned for today's matches")
            return []
        fixtures = data["response"]
        logger.info("Found %d fixtures for today", len(fixtures))
        return fixtures

    async def get_live_scores(self) -> List[Dict]:
        """
        GET /fixtures?live=all  (optionally add &timezone=...)
        """
        params = {"live": "all", "timezone": self.timezone}
        data = await self._make_async_request("fixtures", params)
        if not data or "response" not in data:
            logger.warning("No data returned for live scores")
            return []
        live = data["response"]
        logger.info("Retrieved %d live matches", len(live))
        return live

    async def get_fixture_details(self, fixture_id: int) -> Optional[Dict]:
        """
        Core details: GET /fixtures?id={fixture_id}
        (Events, lineups, and team/player statistics live on separate endpoints if you need them.)
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
        (Live odds exist at /odds/live?fixture=... if you want them.)
        """
        params = {"fixture": fixture_id}
        data = await self._make_async_request("odds", params)
        if not data or "response" not in data or not data["response"]:
            logger.warning("No odds available for fixture %s", fixture_id)
            return []
        # Response structure: list per bookmaker with bets/values; keep original for your analyzer
        return data["response"]

    async def get_team_form(self, team_id: int, limit: int = 5) -> List[Dict]:
        """
        Recent fixtures for team: GET /fixtures?team={team_id}&last={limit}
        API-FOOTBALL returns only the last finished fixtures when using 'last'.
        """
        params = {"team": team_id, "last": limit, "timezone": self.timezone}
        data = await self._make_async_request("fixtures", params)
        if not data or "response" not in data:
            logger.warning("No recent fixtures available for team %s", team_id)
            return []
        return data["response"]

    async def get_expected_goals(self, fixture_id: int) -> Optional[Dict]:
        """
        API-FOOTBALL generally does not provide xG.
        We try statistics and look for any 'expected_goals' style entry; otherwise return None.
        - Team stats: /fixtures/statistics?fixture={fixture_id}&team={team_id}
        - There is no documented general xG endpoint.
        """
        try:
            # Without team IDs we can't call /fixtures/statistics per team here.
            # You can extend your analyzer to pass team IDs and query both.
            logger.debug("xG not available for fixture %s (API-Football limitation)", fixture_id)
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
        # API-FOOTBALL returns a structure with 'predictions' and 'teams' etc.; normalize below if you wish.
        return data["response"][0].get("predictions", data["response"][0])

    # ---------- Helpers to match your analyzer's expectations ----------

    def extract_match_status(self, fixture: Dict) -> str:
        """
        Map API-FOOTBALL's status.short to your labels.
        - 'NS' not started, '1H/2H/ET/P' live, 'FT/AET/PEN' finished, etc.
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
        # During live, 'goals' is current; after FT it's the final
        return goals.get("home", 0) or 0, goals.get("away", 0) or 0

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None
