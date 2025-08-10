from typing import Dict, List, Optional
import config
from .api_football import APIFootballClient
from .sportmonks_client import SportmonksClient

class UnifiedAPIClient:
    """
    Unified API client that supports both Sportmonks and API Football
    Automatically selects the appropriate client based on configuration
    """
    
    def __init__(self):
        self.primary_client = None
        self.fallback_client = None
        
        # Initialize clients based on configuration
        if config.PRIMARY_API == "sportmonks" and config.SPORTMONKS_ENABLED:
            self.primary_client = SportmonksClient()
            print("🚀 Primary API: Sportmonks")
        elif config.PRIMARY_API == "api_football":
            self.primary_client = APIFootballClient()
            print("🚀 Primary API: API Football")
        
        # Initialize fallback client
        if config.FALLBACK_API == "api_football" and config.PRIMARY_API != "api_football":
            self.fallback_client = APIFootballClient()
            print("🔄 Fallback API: API Football")
        elif config.FALLBACK_API == "sportmonks" and config.PRIMARY_API != "sportmonks" and config.SPORTMONKS_ENABLED:
            self.fallback_client = SportmonksClient()
            print("🔄 Fallback API: Sportmonks")
        
        if not self.primary_client:
            # Default to API Football if no valid primary is set
            self.primary_client = APIFootballClient()
            print("⚠️ Defaulting to API Football client")
    
    def _execute_with_fallback(self, method_name: str, *args, **kwargs):
        """Execute method with fallback support"""
        try:
            # Try primary client first
            method = getattr(self.primary_client, method_name)
            result = method(*args, **kwargs)
            
            # If result is empty or None, try fallback
            if not result and self.fallback_client:
                print(f"⚠️ Primary API returned empty result for {method_name}, trying fallback...")
                fallback_method = getattr(self.fallback_client, method_name)
                result = fallback_method(*args, **kwargs)
                
            return result
            
        except Exception as e:
            print(f"❌ Primary API error for {method_name}: {e}")
            
            # Try fallback client
            if self.fallback_client:
                print(f"🔄 Trying fallback API for {method_name}...")
                try:
                    fallback_method = getattr(self.fallback_client, method_name)
                    return fallback_method(*args, **kwargs)
                except Exception as fallback_error:
                    print(f"❌ Fallback API also failed for {method_name}: {fallback_error}")
            
            return [] if 'get_' in method_name and 'List' in str(type([])) else {}
    
    def get_today_matches(self, league_id: int = None) -> List[Dict]:
        """Get today's matches"""
        return self._execute_with_fallback('get_today_matches', league_id)
    
    def get_match_odds(self, fixture_id: int) -> List[Dict]:
        """Get odds for a specific match"""
        return self._execute_with_fallback('get_match_odds', fixture_id)
    
    def get_match_statistics(self, fixture_id: int) -> Dict:
        """Get match statistics"""
        return self._execute_with_fallback('get_match_statistics', fixture_id)
    
    def get_team_form(self, team_id: int, last_matches: int = 10) -> List[Dict]:
        """Get team's recent form"""
        return self._execute_with_fallback('get_team_form', team_id, last_matches)
    
    def get_league_standings(self, league_id: int, season: int = None) -> List[Dict]:
        """Get league standings"""
        return self._execute_with_fallback('get_league_standings', league_id, season)
    
    def get_team_info(self, team_id: int) -> Optional[Dict]:
        """Get team information"""
        return self._execute_with_fallback('get_team_info', team_id)
    
    def get_fixture_details(self, fixture_id: int) -> Optional[Dict]:
        """Get detailed fixture information"""
        return self._execute_with_fallback('get_fixture_details', fixture_id)
    
    def get_league_matches(self, league_id: int, season: int = None, 
                          from_date: str = None, to_date: str = None) -> List[Dict]:
        """Get matches for a specific league"""
        return self._execute_with_fallback('get_league_matches', league_id, season, from_date, to_date)
    
    def get_team_players(self, team_id: int, season: int = None) -> List[Dict]:
        """Get team players"""
        return self._execute_with_fallback('get_team_players', team_id, season)
    
    def get_api_status(self) -> Dict:
        """Get status of both APIs"""
        status = {
            'primary_api': config.PRIMARY_API,
            'fallback_api': config.FALLBACK_API,
            'sportmonks_enabled': config.SPORTMONKS_ENABLED,
            'primary_working': False,
            'fallback_working': False
        }
        
        # Test primary API
        try:
            if hasattr(self.primary_client, 'get_today_matches'):
                result = self.primary_client.get_today_matches()
                status['primary_working'] = True
        except:
            status['primary_working'] = False
        
        # Test fallback API
        if self.fallback_client:
            try:
                if hasattr(self.fallback_client, 'get_today_matches'):
                    result = self.fallback_client.get_today_matches()
                    status['fallback_working'] = True
            except:
                status['fallback_working'] = False
        
        return status