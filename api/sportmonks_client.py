import requests
import time
from typing import Dict, List, Optional
import config

class SportmonksClient:
    """
    Client for Sportmonks API to fetch match data, odds, and statistics
    Website: https://my.sportmonks.com/
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.SPORTMONKS_API_KEY
        self.base_url = config.SPORTMONKS_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json'
        }
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with rate limiting"""
        url = f"{self.base_url}/{endpoint}"
        
        # Use query parameter authentication as fallback
        if params is None:
            params = {}
        
        # Add API token as query parameter
        params['api_token'] = self.api_key
        
        try:
            # Try without Bearer token first, using query param only
            headers_minimal = {'Accept': 'application/json'}
            response = requests.get(url, headers=headers_minimal, params=params)
            response.raise_for_status()
            
            # Rate limiting - wait if needed
            if response.status_code == 429:
                time.sleep(60)  # Wait 1 minute
                return self._make_request(endpoint, params)
            
            json_response = response.json()
            
            # Check for subscription limitations
            if 'message' in json_response and 'subscription' in json_response:
                if 'No result(s) found' in json_response['message'] and 'subscription' in json_response['message']:
                    print(f"⚠️ Sportmonks API: Limited access with current subscription")
                    print(f"   Current plan: {json_response.get('subscription', [{}])[0].get('plans', [{}])[0].get('plan', 'Unknown')}")
                    print(f"   Consider upgrading your Sportmonks subscription for full access")
                    return json_response  # Return the response so we can handle it properly
            
            return json_response
            
        except requests.exceptions.RequestException as e:
            print(f"Sportmonks API request failed: {e}")
            return None
    
    def get_today_matches(self, league_id: int = None) -> List[Dict]:
        """Get today's matches"""
        endpoint = "fixtures"
        today = time.strftime("%Y-%m-%d")
        params = {
            'include': 'participants,scores',
            'filters': f'fixtureDate:{today}'
        }
        
        if league_id:
            params['filters'] += f';leagueId:{league_id}'
            
        response = self._make_request(endpoint, params)
        
        if response and 'data' in response:
            return self._normalize_fixtures(response['data'])
        return []
    
    def get_match_odds(self, fixture_id: int) -> List[Dict]:
        """Get odds for a specific match"""
        endpoint = f"fixtures/{fixture_id}"
        params = {'include': 'odds.bookmaker,odds.market'}
        
        response = self._make_request(endpoint, params)
        
        if response and 'data' in response:
            return self._normalize_odds(response['data'].get('odds', []))
        return []
    
    def get_match_statistics(self, fixture_id: int) -> Dict:
        """Get match statistics"""
        endpoint = f"fixtures/{fixture_id}"
        params = {'include': 'statistics'}
        
        response = self._make_request(endpoint, params)
        
        if response and 'data' in response:
            return self._normalize_statistics(response['data'])
        return {}
    
    def get_team_form(self, team_id: int, last_matches: int = 10) -> List[Dict]:
        """Get team's recent form"""
        endpoint = "fixtures"
        params = {
            'include': 'participants,scores',
            'filter': f'participant_id:{team_id}',
            'per_page': last_matches,
            'sort': '-starting_at'
        }
        
        response = self._make_request(endpoint, params)
        
        if response and 'data' in response:
            return self._normalize_fixtures(response['data'])
        return []
    
    def get_league_standings(self, league_id: int, season: int = None) -> List[Dict]:
        """Get league standings"""
        endpoint = f"standings/seasons/{season}" if season else "standings"
        params = {
            'include': 'participant',
            'filter': f'league_id:{league_id}'
        }
        
        response = self._make_request(endpoint, params)
        
        if response and 'data' in response:
            return self._normalize_standings(response['data'])
        return []
    
    def get_team_info(self, team_id: int) -> Optional[Dict]:
        """Get team information"""
        endpoint = f"teams/{team_id}"
        params = {'include': 'country,venue'}
        
        response = self._make_request(endpoint, params)
        
        if response and 'data' in response:
            return self._normalize_team(response['data'])
        return None
    
    def get_fixture_details(self, fixture_id: int) -> Optional[Dict]:
        """Get detailed fixture information"""
        endpoint = f"fixtures/{fixture_id}"
        params = {
            'include': 'participants,venue,league,season,statistics,scores'
        }
        
        response = self._make_request(endpoint, params)
        
        if response and 'data' in response:
            return self._normalize_fixture_detail(response['data'])
        return None
    
    def get_league_matches(self, league_id: int, season: int = None, 
                          from_date: str = None, to_date: str = None) -> List[Dict]:
        """Get matches for a specific league"""
        endpoint = "fixtures"
        params = {
            'include': 'participants,scores',
            'filter': f'league_id:{league_id}'
        }
        
        if season:
            params['filter'] += f';season_id:{season}'
        if from_date:
            params['filter'] += f';starts_at:>={from_date}'
        if to_date:
            params['filter'] += f';starts_at:<={to_date}'
            
        response = self._make_request(endpoint, params)
        
        if response and 'data' in response:
            return self._normalize_fixtures(response['data'])
        return []
    
    def get_team_players(self, team_id: int, season: int = None) -> List[Dict]:
        """Get team players"""
        endpoint = f"teams/{team_id}/squad"
        params = {'include': 'player,position'}
        
        if season:
            params['filter'] = f'season_id:{season}'
            
        response = self._make_request(endpoint, params)
        
        if response and 'data' in response:
            return self._normalize_players(response['data'])
        return []
    
    # Normalization methods to match API Football format
    def _normalize_fixtures(self, fixtures: List[Dict]) -> List[Dict]:
        """Normalize Sportmonks fixtures to API Football format"""
        normalized = []
        for fixture in fixtures:
            participants = fixture.get('participants', [])
            home_team = next((p for p in participants if p.get('meta', {}).get('location') == 'home'), {})
            away_team = next((p for p in participants if p.get('meta', {}).get('location') == 'away'), {})
            
            normalized_fixture = {
                'fixture': {
                    'id': fixture.get('id'),
                    'date': fixture.get('starting_at'),
                    'status': {
                        'short': fixture.get('state', {}).get('short_name', 'NS')
                    }
                },
                'teams': {
                    'home': {
                        'id': home_team.get('id'),
                        'name': home_team.get('name'),
                        'logo': home_team.get('image_path')
                    },
                    'away': {
                        'id': away_team.get('id'),
                        'name': away_team.get('name'),
                        'logo': away_team.get('image_path')
                    }
                },
                'goals': {
                    'home': None,
                    'away': None
                }
            }
            
            # Add scores if available
            scores = fixture.get('scores', [])
            if scores:
                for score in scores:
                    if score.get('description') == 'CURRENT':
                        if score.get('participant_id') == home_team.get('id'):
                            normalized_fixture['goals']['home'] = score.get('score', {}).get('goals')
                        elif score.get('participant_id') == away_team.get('id'):
                            normalized_fixture['goals']['away'] = score.get('score', {}).get('goals')
            
            normalized.append(normalized_fixture)
        
        return normalized
    
    def _normalize_odds(self, odds_data: List[Dict]) -> List[Dict]:
        """Normalize Sportmonks odds to API Football format"""
        # This is a simplified normalization - you may need to adjust based on your needs
        normalized = []
        for odd in odds_data:
            normalized_odd = {
                'bookmakers': [{
                    'id': odd.get('bookmaker_id'),
                    'name': odd.get('bookmaker', {}).get('name', 'Unknown'),
                    'bets': [{
                        'id': odd.get('market_id'),
                        'name': odd.get('market', {}).get('name', 'Unknown'),
                        'values': [{
                            'value': odd.get('label'),
                            'odd': str(odd.get('value', 1.0))
                        }]
                    }]
                }]
            }
            normalized.append(normalized_odd)
        
        return normalized
    
    def _normalize_statistics(self, fixture_data: Dict) -> Dict:
        """Normalize Sportmonks statistics to API Football format"""
        # Placeholder - implement based on your statistics needs
        return {'response': []}
    
    def _normalize_standings(self, standings_data: List[Dict]) -> List[Dict]:
        """Normalize Sportmonks standings to API Football format"""
        # Placeholder - implement based on your standings needs
        return []
    
    def _normalize_team(self, team_data: Dict) -> Dict:
        """Normalize Sportmonks team to API Football format"""
        return {
            'team': {
                'id': team_data.get('id'),
                'name': team_data.get('name'),
                'logo': team_data.get('image_path'),
                'country': team_data.get('country', {}).get('name')
            }
        }
    
    def _normalize_fixture_detail(self, fixture_data: Dict) -> Dict:
        """Normalize Sportmonks fixture detail to API Football format"""
        participants = fixture_data.get('participants', [])
        home_team = next((p for p in participants if p.get('meta', {}).get('location') == 'home'), {})
        away_team = next((p for p in participants if p.get('meta', {}).get('location') == 'away'), {})
        
        return {
            'fixture': {
                'id': fixture_data.get('id'),
                'date': fixture_data.get('starting_at'),
                'status': {
                    'short': fixture_data.get('state', {}).get('short_name', 'NS')
                }
            },
            'teams': {
                'home': {
                    'id': home_team.get('id'),
                    'name': home_team.get('name'),
                    'logo': home_team.get('image_path')
                },
                'away': {
                    'id': away_team.get('id'),
                    'name': away_team.get('name'),
                    'logo': away_team.get('image_path')
                }
            }
        }
    
    def _normalize_players(self, players_data: List[Dict]) -> List[Dict]:
        """Normalize Sportmonks players to API Football format"""
        normalized = []
        for player_data in players_data:
            player = player_data.get('player', {})
            normalized.append({
                'player': {
                    'id': player.get('id'),
                    'name': player.get('name'),
                    'age': player.get('age'),
                    'position': player_data.get('position', {}).get('name')
                }
            })
        return normalized