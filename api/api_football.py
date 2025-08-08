import requests
import time
from typing import Dict, List, Optional
import config

class APIFootballClient:
    """
    Client for API Football to fetch match data, odds, and statistics
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.API_FOOTBALL_KEY
        self.base_url = config.API_FOOTBALL_BASE_URL
        self.headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': self.api_key
        }
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with rate limiting"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            # Rate limiting - wait if needed
            if response.status_code == 429:
                time.sleep(60)  # Wait 1 minute
                return self._make_request(endpoint, params)
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    def get_today_matches(self, league_id: int = None) -> List[Dict]:
        """Get today's matches"""
        params = {'date': time.strftime('%Y-%m-%d')}
        if league_id:
            params['league'] = league_id
            
        response = self._make_request('fixtures', params)
        
        if response and 'response' in response:
            return response['response']
        return []
    
    def get_match_odds(self, fixture_id: int) -> List[Dict]:
        """Get odds for a specific match"""
        params = {'fixture': fixture_id}
        response = self._make_request('odds', params)
        
        if response and 'response' in response:
            return response['response']
        return []
    
    def get_match_statistics(self, fixture_id: int) -> Dict:
        """Get match statistics"""
        params = {'fixture': fixture_id}
        response = self._make_request('fixtures/statistics', params)
        
        if response and 'response' in response:
            return response['response']
        return {}
    
    def get_team_form(self, team_id: int, last_matches: int = 10) -> List[Dict]:
        """Get team's recent form"""
        params = {'team': team_id, 'last': last_matches}
        response = self._make_request('fixtures', params)
        
        if response and 'response' in response:
            return response['response']
        return []
    
    def get_league_standings(self, league_id: int, season: int = None) -> List[Dict]:
        """Get league standings"""
        params = {'league': league_id}
        if season:
            params['season'] = season
            
        response = self._make_request('standings', params)
        
        if response and 'response' in response:
            return response['response']
        return []
    
    def get_team_info(self, team_id: int) -> Optional[Dict]:
        """Get team information"""
        params = {'id': team_id}
        response = self._make_request('teams', params)
        
        if response and 'response' in response and response['response']:
            return response['response'][0]
        return None
    
    def get_fixture_details(self, fixture_id: int) -> Optional[Dict]:
        """Get detailed fixture information"""
        params = {'id': fixture_id}
        response = self._make_request('fixtures', params)
        
        if response and 'response' in response and response['response']:
            return response['response'][0]
        return None
    
    def get_league_matches(self, league_id: int, season: int = None, 
                          from_date: str = None, to_date: str = None) -> List[Dict]:
        """Get matches for a specific league"""
        params = {'league': league_id}
        if season:
            params['season'] = season
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
            
        response = self._make_request('fixtures', params)
        
        if response and 'response' in response:
            return response['response']
        return []
    
    def get_team_players(self, team_id: int, season: int = None) -> List[Dict]:
        """Get team players"""
        params = {'team': team_id}
        if season:
            params['season'] = season
            
        response = self._make_request('players', params)
        
        if response and 'response' in response:
            return response['response']
        return []
