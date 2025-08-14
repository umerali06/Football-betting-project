#!/usr/bin/env python3
"""
Unified API Client for FIXORA PRO
Uses API-Football as primary source, SportMonks as fallback
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .api_apifootball import ApiFootballClient
from .api_sportmonks import SportMonksClient
import config

logger = logging.getLogger(__name__)

class UnifiedAPIClient:
    """
    Unified API client that prioritizes API-Football and falls back to SportMonks
    """
    
    def __init__(self):
        self.api_football = ApiFootballClient()
        self.sportmonks = SportMonksClient()
        self.primary_api = "api_football"
        self.fallback_api = "sportmonks"
        self.api_stats = {
            'api_football_success': 0,
            'api_football_failures': 0,
            'sportmonks_success': 0,
            'sportmonks_failures': 0,
            'fallbacks_used': 0
        }
        # Cache for fixture ID resolution
        self.fixture_id_cache = {}
    
    async def _try_api_football_first(self, method_name: str, *args, allow_empty: bool = False, **kwargs):
        """
        Try API-Football first, fall back to SportMonks if it fails
        allow_empty: If True, empty results are not treated as failures (for odds/predictions/xG)
        """
        try:
            # Try API-Football first
            if hasattr(self.api_football, method_name):
                method = getattr(self.api_football, method_name)
                result = await method(*args, **kwargs)
                
                # Check if result is valid (not None, and not empty if allow_empty=False)
                if result is not None and (allow_empty or result != []):
                    self.api_stats['api_football_success'] += 1
                    logger.info(f"API-Football {method_name} successful")
                    return result, "api_football"
                elif allow_empty and result == []:
                    # Empty result is acceptable for odds/predictions/xG
                    logger.debug(f"API-Football {method_name} returned empty result (acceptable for {method_name})")
                    return result, "api_football"
                else:
                    logger.debug(f"API-Football {method_name} returned empty result (treating as failure)")
                    raise Exception("Empty result from API-Football")
            else:
                raise Exception(f"Method {method_name} not found in API-Football client")
                
        except Exception as e:
            self.api_stats['api_football_failures'] += 1
            logger.warning(f"API-Football {method_name} failed: {e}")
            
            # Fall back to SportMonks
            try:
                if hasattr(self.sportmonks, method_name):
                    method = getattr(self.sportmonks, method_name)
                    result = await method(*args, **kwargs)
                    
                    if result is not None and (allow_empty or result != []):
                        self.api_stats['sportmonks_success'] += 1
                        self.api_stats['fallbacks_used'] += 1
                        logger.info(f"SportMonks fallback {method_name} successful")
                        return result, "sportmonks"
                    elif allow_empty and result == []:
                        logger.debug(f"SportMonks fallback {method_name} returned empty result (acceptable)")
                        return result, "sportmonks"
                    else:
                        logger.debug(f"SportMonks fallback {method_name} returned empty result")
                        return None, "none"
                else:
                    logger.error(f"Method {method_name} not found in SportMonks client")
                    return None, "none"
                    
            except Exception as fallback_error:
                self.api_stats['sportmonks_failures'] += 1
                logger.error(f"SportMonks fallback {method_name} also failed: {fallback_error}")
                return None, "none"
    
    async def resolve_api_football_fixture_id(self, sportmonks_fixture: Dict) -> Optional[int]:
        """
        Resolve API-Football fixture ID from SportMonks fixture data
        Uses team names and date to find the corresponding API-Football fixture
        """
        try:
            # Extract key data from SportMonks fixture
            participants = sportmonks_fixture.get('participants', [])
            home_team_name = None
            away_team_name = None
            
            for participant in participants:
                if participant.get('meta', {}).get('location') == 'home':
                    home_team_name = participant.get('name')
                elif participant.get('meta', {}).get('location') == 'away':
                    away_team_name = participant.get('name')
            
            if not home_team_name or not away_team_name:
                logger.debug("Could not extract team names from SportMonks fixture")
                return None
            
            # Create cache key
            cache_key = f"{home_team_name}_{away_team_name}_{sportmonks_fixture.get('date', '')}"
            
            # Check cache first
            if cache_key in self.fixture_id_cache:
                logger.debug(f"Using cached API-Football fixture ID: {self.fixture_id_cache[cache_key]}")
                return self.fixture_id_cache[cache_key]
            
            # Try to find fixture in API-Football by searching today's matches
            today_matches = await self.api_football.get_today_matches()
            
            for match in today_matches:
                teams = match.get('teams', {})
                home_team = teams.get('home', {}).get('name', '')
                away_team = teams.get('away', {}).get('name', '')
                
                # Simple name matching (could be enhanced with fuzzy matching)
                if (home_team.lower() == home_team_name.lower() and 
                    away_team.lower() == away_team_name.lower()):
                    fixture_id = self.api_football.extract_fixture_id(match)
                    if fixture_id:
                        # Cache the result
                        self.fixture_id_cache[cache_key] = fixture_id
                        logger.info(f"Resolved API-Football fixture ID {fixture_id} for {home_team_name} vs {away_team_name}")
                        return fixture_id
            
            logger.debug(f"Could not resolve API-Football fixture ID for {home_team_name} vs {away_team_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error resolving API-Football fixture ID: {e}")
            return None
    
    async def get_today_matches(self, include_live: bool = True) -> List[Dict]:
        """Get today's matches with optional live matches included"""
        result, source = await self._try_api_football_first("get_today_matches", include_live)
        
        # Tag each fixture with its provider for consistent follow-up calls
        if result:
            for fixture in result:
                fixture["_provider"] = source
        
        # Optionally include live matches if requested
        if include_live:
            try:
                live_result, live_source = await self._try_api_football_first("get_live_scores")
                if live_result:
                    # Tag live fixtures and merge them
                    for fixture in live_result:
                        fixture["_provider"] = live_source
                        fixture["_is_live"] = True
                    
                    # Merge live matches with today's matches, avoiding duplicates
                    if result:
                        existing_ids = {f.get("fixture", {}).get("id") or f.get("id") for f in result}
                        for live_fixture in live_result:
                            live_id = live_fixture.get("fixture", {}).get("id") or live_fixture.get("id")
                            if live_id not in existing_ids:
                                result.append(live_fixture)
                                existing_ids.add(live_id)
                    else:
                        result = live_result
                        
                    logger.info(f"Merged {len(live_result)} live matches with today's fixtures")
            except Exception as e:
                logger.debug(f"Failed to fetch live matches: {e}")
        
        return result if result else []
    
    async def get_live_scores(self) -> List[Dict]:
        """Get live scores with API-Football priority"""
        result, source = await self._try_api_football_first("get_live_scores")
        # Tag each fixture with its provider for consistent follow-up calls
        if result:
            for fixture in result:
                fixture["_provider"] = source
        return result if result else []
    
    async def get_fixture_details(self, fixture_id: int) -> Optional[Dict]:
        """Get fixture details from the appropriate API"""
        # Try API-Football first
        try:
            result = await self.api_football.get_fixture_details(fixture_id)
            if result:
                return result
        except Exception as e:
            logger.debug(f"API-Football fixture details failed: {e}")
        
        # Fall back to SportMonks
        try:
            result = await self.sportmonks.get_fixture_details(fixture_id)
            return result
        except Exception as e:
            logger.debug(f"SportMonks fixture details failed: {e}")
            return None
    
    async def safe_fixture_details(self, fixture: Dict) -> Optional[Dict]:
        """Get fixture details using the correct provider with explicit ID validation"""
        prov = fixture.get("_provider", "api_football")
        
        if prov == "api_football":
            fid = fixture.get("fixture", {}).get("id") or fixture.get("id")
            if fid is not None:  # Explicit None check
                return await self.api_football.get_fixture_details(fid)
            else:
                logger.warning("Missing fixture ID for API-Football fixture details")
                return None
        elif prov == "sportmonks":
            fid = fixture.get("id")
            if fid is not None:  # Explicit None check
                return await self.sportmonks.get_fixture_details(fid)
            else:
                logger.warning("Missing fixture ID for SportMonks fixture details")
                return None
        else:
            logger.warning(f"Unknown provider {prov} for fixture details")
            return None
    
    async def get_match_odds(self, fixture_id: int) -> List[Dict]:
        """Get match odds with allow_empty=True since odds might not be available"""
        result, source = await self._try_api_football_first("get_match_odds", fixture_id, allow_empty=True)
        return result if result else []
    
    async def safe_match_odds(self, fixture: Dict) -> List[Dict]:
        """Get match odds using the correct provider with explicit ID validation"""
        prov = fixture.get("_provider", "api_football")
        
        if prov == "api_football":
            fid = fixture.get("fixture", {}).get("id") or fixture.get("id")
            if fid is not None:  # Explicit None check
                return await self.api_football.get_match_odds(fid)
            else:
                logger.warning("Missing fixture ID for API-Football match odds")
                return []
        elif prov == "sportmonks":
            fid = fixture.get("id")
            if fid is not None:  # Explicit None check
                return await self.sportmonks.get_match_odds(fid)
            else:
                logger.warning("Missing fixture ID for SportMonks match odds")
                return []
        else:
            logger.warning(f"Unknown provider {prov} for match odds")
            return []
    
    async def get_live_odds(self, fixture_id: int) -> List[Dict]:
        """Get live odds with allow_empty=True"""
        result, source = await self._try_api_football_first("get_live_odds", fixture_id, allow_empty=True)
        return result if result else []
    
    async def get_team_form(self, team_id: int, start_date: str = None, end_date: str = None, limit: int = 5) -> List[Dict]:
        """Get team form from the appropriate API"""
        # Try API-Football first
        try:
            result = await self.api_football.get_team_form(team_id, limit)
            if result:
                return result
        except Exception as e:
            logger.debug(f"API-Football team form failed: {e}")
        
        # Fall back to SportMonks
        try:
            result = await self.sportmonks.get_team_form(team_id, start_date, end_date, limit)
            return result
        except Exception as e:
            logger.debug(f"SportMonks team form failed: {e}")
            return []
    
    async def get_expected_goals(self, fixture_id: int) -> Optional[Dict]:
        """Get expected goals with proper handling of API plan limitations"""
        # Try API-Football first - this endpoint often returns empty for many fixtures
        try:
            result = await self.api_football.get_expected_goals(fixture_id)
            if result:
                logger.debug(f"API-Football xG data retrieved for fixture {fixture_id}")
                return result
            else:
                # Empty result is normal for API-Football xG - not a failure
                logger.debug(f"API-Football xG returned empty for fixture {fixture_id} (normal for this API)")
        except Exception as e:
            logger.debug(f"API-Football expected goals failed for fixture {fixture_id}: {e}")
        
        # Fall back to SportMonks - this is where the xGFixture include error occurs
        try:
            result = await self.sportmonks.get_expected_goals(fixture_id)
            if result:
                logger.debug(f"SportMonks xG data retrieved for fixture {fixture_id}")
                return result
            else:
                # Empty result from SportMonks might indicate plan limitation
                logger.debug(f"SportMonks xG returned empty for fixture {fixture_id} (may be plan limitation)")
                return None
        except Exception as e:
            # Check if this is an API access denied error (plan limitation)
            if "access denied" in str(e).lower() or "403" in str(e):
                logger.debug(f"SportMonks xG access denied for fixture {fixture_id} (plan limitation)")
            else:
                logger.debug(f"SportMonks expected goals failed for fixture {fixture_id}: {e}")
            return None
    
    async def get_predictions(self, fixture_id: int) -> Optional[Dict]:
        """Get predictions with proper handling of API plan limitations"""
        # Try API-Football first - predictions endpoint often returns empty for many fixtures
        try:
            result = await self.api_football.get_predictions(fixture_id)
            if result:
                logger.debug(f"API-Football predictions retrieved for fixture {fixture_id}")
                return result
            else:
                # Empty result is normal for API-Football predictions - not a failure
                logger.debug(f"API-Football predictions returned empty for fixture {fixture_id} (normal for this API)")
        except Exception as e:
            logger.debug(f"API-Football predictions failed for fixture {fixture_id}: {e}")
        
        # Fall back to SportMonks - this might have plan limitations
        try:
            result = await self.sportmonks.get_predictions(fixture_id)
            if result:
                logger.debug(f"SportMonks predictions retrieved for fixture {fixture_id}")
                return result
            else:
                # Empty result from SportMonks might indicate plan limitation
                logger.debug(f"SportMonks predictions returned empty for fixture {fixture_id} (may be plan limitation)")
                return None
        except Exception as e:
            # Check if this is an API access denied error (plan limitation)
            if "access denied" in str(e).lower() or "403" in str(e):
                logger.debug(f"SportMonks predictions access denied for fixture {fixture_id} (plan limitation)")
            else:
                logger.debug(f"SportMonks predictions failed for fixture {fixture_id}: {e}")
            return None
    
    async def safe_predictions(self, fixture: Dict) -> Optional[Dict]:
        """Get predictions using the correct provider with explicit ID validation"""
        prov = fixture.get("_provider", "api_football")
        
        if prov == "api_football":
            fid = fixture.get("fixture", {}).get("id") or fixture.get("id")
            if fid is not None:  # Explicit None check
                return await self.api_football.get_predictions(fid)
            else:
                logger.warning("Missing fixture ID for API-Football predictions")
                return None
        elif prov == "sportmonks":
            fid = fixture.get("id")
            if fid is not None:  # Explicit None check
                return await self.sportmonks.get_predictions(fid)
            else:
                logger.warning("Missing fixture ID for SportMonks predictions")
                return None
        else:
            logger.warning(f"Unknown provider {prov} for predictions")
            return None
    
    def extract_match_status(self, fixture: Dict) -> str:
        """Extract match status based on fixture's _provider tag"""
        provider = fixture.get("_provider", "api_football")
        
        if provider == "api_football":
            return self.api_football.extract_match_status(fixture)
        elif provider == "sportmonks":
            # Extract from SportMonks format
            status = fixture.get('time', {}).get('status', '')
            if status in ['LIVE', 'HT', '1H', '2H', 'ET', 'PEN']:
                return 'LIVE'
            elif status in ['FT', 'AET', 'PEN']:
                return 'FINISHED'
            elif status in ['NS', 'TBD']:
                return 'NOT_STARTED'
            else:
                return 'UNKNOWN'
        else:
            return 'UNKNOWN'
    
    def extract_fixture_id(self, fixture: Dict) -> Optional[int]:
        """Extract fixture ID based on fixture's _provider tag"""
        # Get the provider from the fixture itself
        provider = fixture.get("_provider", "api_football")
        
        if provider == "api_football":
            # API-Football structure: fixture.id
            fixture_data = fixture.get('fixture', {})
            if fixture_data and 'id' in fixture_data:
                return fixture_data.get('id')
            # Fallback: direct id
            return fixture.get('id')
        elif provider == "sportmonks":
            # SportMonks structure: direct id
            return fixture.get('id')
        else:
            # Try common patterns for unknown providers
            return (fixture.get('id') or 
                   fixture.get('fixture_id') or 
                   fixture.get('fixture', {}).get('id'))
    
    def debug_fixture_structure(self, fixture: Dict) -> str:
        """Debug fixture structure to understand ID location"""
        provider = fixture.get("_provider", "api_football")
        
        if provider == "api_football":
            fixture_data = fixture.get('fixture', {})
            return f"API-Football: fixture.id={fixture_data.get('id') if fixture_data else 'None'}, direct.id={fixture.get('id')}"
        elif provider == "sportmonks":
            return f"SportMonks: direct.id={fixture.get('id')}"
        else:
            return f"Unknown: id={fixture.get('id')}, fixture_id={fixture.get('fixture_id')}, fixture.id={fixture.get('fixture', {}).get('id')}"
    
    def extract_team_names(self, fixture: Dict) -> Tuple[str, str]:
        """Extract team names based on fixture's _provider tag"""
        provider = fixture.get("_provider", "api_football")
        
        if provider == "api_football":
            return self.api_football.extract_team_names(fixture)
        elif provider == "sportmonks":
            # Extract from SportMonks format
            participants = fixture.get('participants', [])
            home_team = "Unknown"
            away_team = "Unknown"
            
            for participant in participants:
                if participant.get('meta', {}).get('location') == 'home':
                    home_team = participant.get('name', 'Unknown')
                elif participant.get('meta', {}).get('location') == 'away':
                    away_team = participant.get('name', 'Unknown')
            
            return home_team, away_team
        else:
            return "Unknown", "Unknown"
    
    def extract_score(self, fixture: Dict) -> Tuple[int, int]:
        """Extract score based on fixture's _provider tag"""
        provider = fixture.get("_provider", "api_football")
        
        if provider == "api_football":
            return self.api_football.extract_score(fixture)
        elif provider == "sportmonks":
            # Extract from SportMonks format
            scores = fixture.get('scores', {})
            home_score = scores.get('home', 0) if scores else 0
            away_score = scores.get('away', 0) if scores else 0
            return home_score, away_score
        else:
            return 0, 0
    
    def get_api_stats(self) -> Dict:
        """Get comprehensive API usage statistics"""
        total_requests = (
            self.api_stats['api_football_success'] + 
            self.api_stats['api_football_failures'] +
            self.api_stats['sportmonks_success'] + 
            self.api_stats['sportmonks_failures']
        )
        
        api_football_total = self.api_stats['api_football_success'] + self.api_stats['api_football_failures']
        sportmonks_total = self.api_stats['sportmonks_success'] + self.api_stats['sportmonks_failures']
        
        return {
            'total_requests': total_requests,
            'fallbacks_used': self.api_stats['fallbacks_used'],
            'api_football': {
                'success': self.api_stats['api_football_success'],
                'failures': self.api_stats['api_football_failures'],
                'total': api_football_total,
                'success_rate': round((self.api_stats['api_football_success'] / api_football_total * 100) if api_football_total > 0 else 0, 1)
            },
            'sportmonks': {
                'success': self.api_stats['sportmonks_success'],
                'failures': self.api_stats['sportmonks_failures'],
                'total': sportmonks_total,
                'success_rate': round((self.api_stats['sportmonks_success'] / sportmonks_total * 100) if sportmonks_total > 0 else 0, 1)
            }
        }
    
    async def close(self):
        """Close both API clients"""
        try:
            await self.api_football.close()
            await self.sportmonks.close()
            logger.info("Unified API client closed successfully")
        except Exception as e:
            logger.error(f"Error closing unified API client: {e}")
    
    async def test_connection(self) -> Dict[str, bool]:
        """Test connection to both APIs"""
        results = {}
        
        # Test API-Football
        try:
            today_matches = await self.api_football.get_today_matches()
            results['api_football'] = len(today_matches) > 0
            logger.info(f"API-Football connection test: {'SUCCESS' if results['api_football'] else 'FAILED'}")
        except Exception as e:
            results['api_football'] = False
            logger.error(f"API-Football connection test failed: {e}")
        
        # Test SportMonks
        try:
            today_matches = await self.sportmonks.get_today_matches()
            results['sportmonks'] = len(today_matches) > 0
            logger.info(f"SportMonks connection test: {'SUCCESS' if results['sportmonks'] else 'FAILED'}")
        except Exception as e:
            results['sportmonks'] = False
            logger.error(f"SportMonks connection test failed: {e}")
        
        return results

    async def get_fixture_statistics(self, fixture_id: int) -> Optional[Dict]:
        """Get comprehensive statistics for a fixture from the appropriate API"""
        # Try API-Football first
        try:
            result = await self.api_football.get_fixture_statistics(fixture_id)
            if result:
                return result
        except Exception as e:
            logger.debug(f"API-Football fixture statistics failed: {e}")
        
        # SportMonks doesn't have equivalent statistics endpoint
        logger.debug(f"No statistics available for fixture {fixture_id}")
        return None

    async def safe_fixture_statistics(self, fixture: Dict) -> Optional[Dict]:
        """Get fixture statistics using the correct provider with explicit ID validation"""
        prov = fixture.get("_provider", "api_football")
        
        if prov == "api_football":
            fid = fixture.get("fixture", {}).get("id") or fixture.get("id")
            if fid is not None:  # Explicit None check
                return await self.api_football.get_fixture_statistics(fid)
            else:
                logger.warning("Missing fixture ID for API-Football statistics")
                return None
        elif prov == "sportmonks":
            # SportMonks doesn't have statistics endpoint
            logger.debug("Statistics not available for SportMonks fixtures")
            return None
        else:
            logger.warning(f"Unknown provider {prov} for fixture statistics")
            return None

    async def safe_live_odds(self, fixture: Dict) -> List[Dict]:
        """Get live odds using the correct provider with explicit ID validation"""
        prov = fixture.get("_provider", "api_football")
        
        if prov == "api_football":
            fid = fixture.get("fixture", {}).get("id") or fixture.get("id")
            if fid is not None:  # Explicit None check
                return await self.api_football.get_live_odds(fid)
            else:
                logger.warning("Missing fixture ID for API-Football live odds")
                return []
        elif prov == "sportmonks":
            # SportMonks doesn't have live odds endpoint
            logger.debug("Live odds not available for SportMonks fixtures")
            return []
        else:
            logger.warning(f"Unknown provider {prov} for live odds")
            return []
