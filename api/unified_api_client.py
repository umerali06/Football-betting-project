#!/usr/bin/env python3
"""
Unified API Client for FIXORA PRO
Uses API-Football as primary source, SportMonks as fallback
"""

import asyncio
import logging
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
    
    async def _try_api_football_first(self, method_name: str, *args, **kwargs):
        """
        Try API-Football first, fall back to SportMonks if it fails
        """
        try:
            # Try API-Football first
            if hasattr(self.api_football, method_name):
                method = getattr(self.api_football, method_name)
                result = await method(*args, **kwargs)
                
                if result is not None and result != []:
                    self.api_stats['api_football_success'] += 1
                    logger.info(f"API-Football {method_name} successful")
                    return result, "api_football"
                else:
                    logger.debug(f"API-Football {method_name} returned empty result (normal for many fixtures)")
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
                    
                    if result is not None and result != []:
                        self.api_stats['sportmonks_success'] += 1
                        self.api_stats['fallbacks_used'] += 1
                        logger.info(f"SportMonks fallback {method_name} successful")
                        return result, "sportmonks"
                    else:
                        logger.debug(f"SportMonks fallback {method_name} returned empty result (normal for many fixtures)")
                        return None, "none"
                else:
                    logger.error(f"Method {method_name} not found in SportMonks client")
                    return None, "none"
                    
            except Exception as fallback_error:
                self.api_stats['sportmonks_failures'] += 1
                logger.error(f"SportMonks fallback {method_name} also failed: {fallback_error}")
                return None, "none"
    
    async def get_today_matches(self, include_live: bool = True) -> List[Dict]:
        """Get today's matches with API-Football priority"""
        result, source = await self._try_api_football_first("get_today_matches", include_live)
        # Tag each fixture with its provider for consistent follow-up calls
        if result:
            for fixture in result:
                fixture["_provider"] = source
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
        """Get fixture details with API-Football priority"""
        result, source = await self._try_api_football_first("get_fixture_details", fixture_id)
        return result
    
    async def safe_fixture_details(self, fixture: Dict) -> Optional[Dict]:
        """Get fixture details using the correct provider based on fixture source"""
        prov = fixture.get("_provider", "api_football")
        if prov == "api_football":
            # Extract API-Football fixture ID
            fid = fixture.get("fixture", {}).get("id") or fixture.get("id")
            if fid:
                return await self.api_football.get_fixture_details(fid)
        elif prov == "sportmonks":
            # Use SportMonks fixture ID
            fid = fixture.get("id")
            if fid:
                return await self.sportmonks.get_fixture_details(fid)
        return None
    
    async def get_match_odds(self, fixture_id: int) -> List[Dict]:
        """Get match odds with API-Football priority"""
        result, source = await self._try_api_football_first("get_match_odds", fixture_id)
        return result if result else []
    
    async def safe_match_odds(self, fixture: Dict) -> List[Dict]:
        """Get match odds using the correct provider based on fixture source"""
        prov = fixture.get("_provider", "api_football")
        if prov == "api_football":
            # Extract API-Football fixture ID
            fid = fixture.get("fixture", {}).get("id") or fixture.get("id")
            if fid:
                return await self.api_football.get_match_odds(fid)
        elif prov == "sportmonks":
            # Use SportMonks fixture ID
            fid = fixture.get("id")
            if fid:
                return await self.sportmonks.get_match_odds(fid)
        return []
    
    async def get_team_form(self, team_id: int, start_date: str = None, end_date: str = None, limit: int = 5) -> List[Dict]:
        """Get team form with API-Football priority"""
        # Handle different parameter signatures between APIs
        if start_date and end_date:
            # SportMonks style parameters
            result, source = await self._try_api_football_first("get_team_form", team_id, limit)
        else:
            # API-Football style parameters
            result, source = await self._try_api_football_first("get_team_form", team_id, limit)
        
        return result if result else []
    
    async def get_expected_goals(self, fixture_id: int) -> Optional[Dict]:
        """Get expected goals with API-Football priority"""
        try:
            result, source = await self._try_api_football_first("get_expected_goals", fixture_id)
            # Don't treat empty/None as error - this is normal for many fixtures
            if not result:
                logger.debug("Expected goals not available for fixture %s (normal for many fixtures)", fixture_id)
            return result
        except Exception as e:
            logger.debug("Expected goals retrieval failed for fixture %s: %s", fixture_id, e)
            return None
    
    async def get_predictions(self, fixture_id: int) -> Optional[Dict]:
        """Get predictions with API-Football priority"""
        try:
            result, source = await self._try_api_football_first("get_predictions", fixture_id)
            # Don't treat empty/None as error - this is normal for many fixtures
            if not result:
                logger.debug("Predictions not available for fixture %s (normal for many fixtures)", fixture_id)
            return result
        except Exception as e:
            logger.debug("Predictions retrieval failed for fixture %s: %s", fixture_id, e)
            return None
    
    async def safe_predictions(self, fixture: Dict) -> Optional[Dict]:
        """Get predictions using the correct provider based on fixture source"""
        prov = fixture.get("_provider", "api_football")
        if prov == "api_football":
            # Extract API-Football fixture ID
            fid = fixture.get("fixture", {}).get("id") or fixture.get("id")
            if fid:
                return await self.api_football.get_predictions(fid)
        elif prov == "sportmonks":
            # Use SportMonks fixture ID
            fid = fixture.get("id")
            if fid:
                return await self.sportmonks.get_predictions(fid)
        return None
    
    def extract_match_status(self, fixture: Dict, source: str = "api_football") -> str:
        """Extract match status based on API source"""
        if source == "api_football":
            return self.api_football.extract_match_status(fixture)
        elif source == "sportmonks":
            # Use SportMonks status extraction logic
            status = fixture.get('status', 'UNKNOWN')
            if status in ['LIVE', '1H', '2H', 'ET', 'P', 'BT', 'HT']:
                return 'LIVE'
            elif status in ['FINISHED', 'FT', 'AET', 'PEN']:
                return 'FINISHED'
            elif status in ['NOT_STARTED', 'NS', 'TBD']:
                return 'NOT_STARTED'
            else:
                return status
        else:
            return 'UNKNOWN'
    
    def extract_fixture_id(self, fixture: Dict, source: str = "api_football") -> Optional[int]:
        """Extract fixture ID based on API source"""
        if source == "api_football":
            # API-Football structure: fixture.id
            fixture_data = fixture.get('fixture', {})
            if fixture_data:
                return fixture_data.get('id')
            # Fallback: direct id
            return fixture.get('id')
        elif source == "sportmonks":
            # SportMonks structure: direct id
            return fixture.get('id')
        else:
            # Try common patterns
            return (fixture.get('id') or 
                   fixture.get('fixture_id') or 
                   fixture.get('fixture', {}).get('id'))
    
    def debug_fixture_structure(self, fixture: Dict, source: str = "api_football") -> str:
        """Debug fixture structure to understand ID location"""
        if source == "api_football":
            fixture_data = fixture.get('fixture', {})
            return f"API-Football: fixture.id={fixture_data.get('id') if fixture_data else 'None'}, direct.id={fixture.get('id')}"
        elif source == "sportmonks":
            return f"SportMonks: direct.id={fixture.get('id')}"
        else:
            return f"Unknown: id={fixture.get('id')}, fixture_id={fixture.get('fixture_id')}, fixture.id={fixture.get('fixture', {}).get('id')}"
    
    def extract_team_names(self, fixture: Dict, source: str = "api_football") -> Tuple[str, str]:
        """Extract team names based on API source"""
        if source == "api_football":
            return self.api_football.extract_team_names(fixture)
        elif source == "sportmonks":
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
    
    def extract_score(self, fixture: Dict, source: str = "api_football") -> Tuple[int, int]:
        """Extract score based on API source"""
        if source == "api_football":
            return self.api_football.extract_score(fixture)
        elif source == "sportmonks":
            # Extract from SportMonks format
            scores = fixture.get('scores', {})
            home_score = scores.get('home', 0) if scores else 0
            away_score = scores.get('away', 0) if scores else 0
            return home_score, away_score
        else:
            return 0, 0
    
    def get_api_stats(self) -> Dict:
        """Get API usage statistics"""
        total_requests = (self.api_stats['api_football_success'] + 
                         self.api_stats['api_football_failures'] + 
                         self.api_stats['sportmonks_success'] + 
                         self.api_stats['sportmonks_failures'])
        
        api_football_success_rate = 0
        sportmonks_success_rate = 0
        
        if self.api_stats['api_football_success'] + self.api_stats['api_football_failures'] > 0:
            api_football_success_rate = (self.api_stats['api_football_success'] / 
                                       (self.api_stats['api_football_success'] + self.api_stats['api_football_failures'])) * 100
        
        if self.api_stats['sportmonks_success'] + self.api_stats['sportmonks_failures'] > 0:
            sportmonks_success_rate = (self.api_stats['sportmonks_success'] / 
                                     (self.api_stats['sportmonks_success'] + self.api_stats['sportmonks_failures'])) * 100
        
        return {
            'total_requests': total_requests,
            'api_football': {
                'success': self.api_stats['api_football_success'],
                'failures': self.api_stats['api_football_failures'],
                'success_rate': round(api_football_success_rate, 2)
            },
            'sportmonks': {
                'success': self.api_stats['sportmonks_success'],
                'failures': self.api_stats['sportmonks_failures'],
                'success_rate': round(sportmonks_success_rate, 2)
            },
            'fallbacks_used': self.api_stats['fallbacks_used'],
            'primary_api': self.primary_api,
            'fallback_api': self.fallback_api
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
