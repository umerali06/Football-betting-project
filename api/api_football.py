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
            print(f"🔄 Making API request to: {endpoint}")
            response = requests.get(url, headers=self.headers, params=params)
            
            # Rate limiting - wait if needed
            if response.status_code == 429:
                print("⏳ Rate limit hit, waiting 60 seconds...")
                time.sleep(60)  # Wait 1 minute
                return self._make_request(endpoint, params)
            
            if response.status_code == 401:
                print("❌ API key error - check your API_FOOTBALL_KEY in config.py")
                return None
                
            if response.status_code == 403:
                print("❌ API access forbidden - check your subscription")
                return None
            
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data:
                print(f"❌ API errors: {data['errors']}")
                return None
                
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error in API request: {e}")
            return None
    
    def get_today_matches(self, league_id: int = None, days_ahead: int = 7) -> List[Dict]:
        """Get today's matches and upcoming matches - REAL TIME ONLY"""
        import datetime
        
        all_matches = []
        
        # Check today and next few days
        for i in range(days_ahead):
            check_date = datetime.datetime.now() + datetime.timedelta(days=i)
            date_str = check_date.strftime('%Y-%m-%d')
            
            params = {'date': date_str}
            if league_id:
                params['league'] = league_id
            
            print(f"🔍 Checking for matches on {date_str}...")
            response = self._make_request('fixtures', params)
            
            if response and 'response' in response:
                matches = response['response']
                if matches:
                    print(f"✅ Found {len(matches)} matches on {date_str}")
                    all_matches.extend(matches)
                else:
                    print(f"📭 No matches found on {date_str}")
            else:
                print(f"❌ Failed to fetch matches for {date_str}")
        
        # If no matches found, try popular leagues
        if not all_matches:
            print("🔍 No matches found on specific dates, trying popular leagues...")
            popular_leagues = [39, 140, 135, 78, 61]  # Premier League, La Liga, Serie A, Bundesliga, Ligue 1
            
            for league in popular_leagues:
                params = {'league': league, 'season': 2024}
                response = self._make_request('fixtures', params)
                
                if response and 'response' in response:
                    matches = response['response']
                    if matches:
                        print(f"✅ Found {len(matches)} matches in league {league}")
                        all_matches.extend(matches[:5])  # Limit to 5 matches per league
                        break
        
        if not all_matches:
            print("📭 No matches available at the moment")
        
        return all_matches
    
    def get_match_odds(self, fixture_id: int) -> List[Dict]:
        """Get odds for a specific match - REAL TIME ONLY"""
        params = {'fixture': fixture_id}
        response = self._make_request('odds', params)
        
        if response and 'response' in response:
            odds = response['response']
            if odds:
                print(f"✅ Found {len(odds)} odds for fixture {fixture_id}")
                return odds
            else:
                print(f"📭 No odds available for fixture {fixture_id}")
                return []
        else:
            print(f"❌ Failed to fetch odds for fixture {fixture_id}")
            return []
    
    def get_match_statistics(self, fixture_id: int) -> Dict:
        """Get match statistics - REAL TIME ONLY"""
        params = {'fixture': fixture_id}
        response = self._make_request('fixtures/statistics', params)
        
        if response and 'response' in response:
            stats = response['response']
            if stats:
                print(f"✅ Found statistics for fixture {fixture_id}")
                return stats
            else:
                print(f"📭 No statistics available for fixture {fixture_id}")
                return {}
        else:
            print(f"❌ Failed to fetch statistics for fixture {fixture_id}")
        return {}
    
    def get_team_form(self, team_id: int, last_matches: int = 10) -> List[Dict]:
        """Get team's recent form - REAL TIME ONLY"""
        params = {'team': team_id, 'last': last_matches}
        response = self._make_request('fixtures', params)
        
        if response and 'response' in response:
            form = response['response']
            if form:
                print(f"✅ Found {len(form)} recent matches for team {team_id}")
                return form
            else:
                print(f"📭 No recent matches found for team {team_id}")
                return []
        else:
            print(f"❌ Failed to fetch team form for team {team_id}")
            return []
    
    def get_league_standings(self, league_id: int, season: int = None) -> List[Dict]:
        """Get league standings - REAL TIME ONLY"""
        params = {'league': league_id}
        if season:
            params['season'] = season
            
        response = self._make_request('standings', params)
        
        if response and 'response' in response:
            standings = response['response']
            if standings:
                print(f"✅ Found standings for league {league_id}")
                return standings
            else:
                print(f"📭 No standings available for league {league_id}")
                return []
        else:
            print(f"❌ Failed to fetch standings for league {league_id}")
        return []
    
    def get_team_info(self, team_id: int) -> Optional[Dict]:
        """Get team information - REAL TIME ONLY"""
        params = {'id': team_id}
        response = self._make_request('teams', params)
        
        if response and 'response' in response and response['response']:
            print(f"✅ Found team info for team {team_id}")
            return response['response'][0]
        else:
            print(f"❌ Failed to fetch team info for team {team_id}")
        return None
    
    def get_fixture_details(self, fixture_id: int) -> Optional[Dict]:
        """Get detailed fixture information - REAL TIME ONLY"""
        params = {'id': fixture_id}
        response = self._make_request('fixtures', params)
        
        if response and 'response' in response and response['response']:
            print(f"✅ Found fixture details for fixture {fixture_id}")
            return response['response'][0]
        else:
            print(f"❌ Failed to fetch fixture details for fixture {fixture_id}")
        return None
    
    def get_league_matches(self, league_id: int, season: int = None, 
                          from_date: str = None, to_date: str = None) -> List[Dict]:
        """Get matches for a specific league - REAL TIME ONLY"""
        params = {'league': league_id}
        if season:
            params['season'] = season
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
            
        response = self._make_request('fixtures', params)
        
        if response and 'response' in response:
            matches = response['response']
            if matches:
                print(f"✅ Found {len(matches)} matches for league {league_id}")
                return matches
            else:
                print(f"📭 No matches found for league {league_id}")
                return []
        else:
            print(f"❌ Failed to fetch matches for league {league_id}")
        return []
    
    def get_team_players(self, team_id: int, season: int = None) -> List[Dict]:
        """Get team players - REAL TIME ONLY"""
        params = {'team': team_id}
        if season:
            params['season'] = season
            
        response = self._make_request('players', params)
        
        if response and 'response' in response:
            players = response['response']
            if players:
                print(f"✅ Found {len(players)} players for team {team_id}")
                return players
            else:
                print(f"📭 No players found for team {team_id}")
                return []
        else:
            print(f"❌ Failed to fetch players for team {team_id}")
        return []
