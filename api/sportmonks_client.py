import requests
import time
from typing import Dict, List, Optional
import config
import json
from datetime import datetime

class SportmonksClient:
    """
    Real-time Sportmonks API client using exact v3 endpoints
    Website: https://my.sportmonks.com/api/tester
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.SPORTMONKS_API_KEY
        self.base_url = config.SPORTMONKS_BASE_URL
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'Football-Betting-System/1.0'
        }
        print(f"🔑 Sportmonks API initialized with key: {self.api_key[:15]}...")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with proper error handling"""
        url = f"{self.base_url}/{endpoint}"
        
        if params is None:
            params = {}
        
        # Add API token as query parameter (Sportmonks standard)
        params['api_token'] = self.api_key
        
        try:
            print(f"📡 Requesting: {endpoint}")
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            # Handle rate limiting
            if response.status_code == 429:
                print(f"⏳ Rate limited, waiting 60 seconds...")
                time.sleep(60)
                return self._make_request(endpoint, params)
            
            response.raise_for_status()
            json_response = response.json()
            
            # Check for subscription/access issues
            if 'message' in json_response and 'subscription' in json_response:
                if 'No result(s) found' in json_response.get('message', ''):
                    print(f"⚠️ Limited access: {json_response['message']}")
                    plan = json_response.get('subscription', [{}])[0].get('plans', [{}])[0].get('plan', 'Unknown')
                    print(f"   Current plan: {plan}")
                    return None
            
            # Success - show data info
            if 'data' in json_response:
                data_count = len(json_response['data']) if isinstance(json_response['data'], list) else 1
                print(f"✅ Received {data_count} items from {endpoint}")
            
            return json_response
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed for {endpoint}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error for {endpoint}: {e}")
            return None
    
    def get_today_matches(self, league_id: int = None) -> List[Dict]:
        """
        Get today's fixtures using real-time endpoint
        Endpoint: GET /fixtures?filters=todayDate&include=participants;league;states
        """
        print(f"\n🏆 Fetching today's matches...")
        
        # Use todayDate filter as per Sportmonks documentation
        params = {
            'filters': 'todayDate',
            'include': 'participants,league,states,scores'
        }
        
        if league_id:
            params['filters'] += f';leagueId:{league_id}'
        
        response = self._make_request('football/fixtures', params)
        
        if response and 'data' in response:
            matches = response['data']
            print(f"📊 Found {len(matches)} live fixtures for today")
            return self._normalize_fixtures(matches)
        
        print("⚠️ No matches found for today")
        return []
    
    def get_fixtures_by_date(self, date: str) -> List[Dict]:
        """
        Get fixtures by specific date
        Endpoint: GET /fixtures/date/{YYYY-MM-DD}?include=participants;states
        """
        print(f"\n📅 Fetching fixtures for {date}...")
        
        params = {
            'include': 'participants,states,scores,league'
        }
        
        response = self._make_request(f'football/fixtures/date/{date}', params)
        
        if response and 'data' in response:
            matches = response['data']
            print(f"📊 Found {len(matches)} fixtures for {date}")
            return self._normalize_fixtures(matches)
        
        return []
    
    def get_match_odds(self, fixture_id: int) -> List[Dict]:
        """
        Get real-time pre-match odds for a fixture
        Endpoint: GET /odds/pre-match/fixtures/{fixture_id}
        """
        print(f"\n💰 Fetching live odds for fixture {fixture_id}...")
        
        response = self._make_request(f'football/odds/pre-match/fixtures/{fixture_id}')
        
        if response and 'data' in response:
            odds_data = response['data']
            print(f"📊 Found odds from {len(odds_data)} sources")
            return self._normalize_odds(odds_data)
        
        print("⚠️ No odds data available")
        return []
    
    def get_market_odds(self, fixture_id: int, market_id: int) -> List[Dict]:
        """
        Get odds for specific market (e.g., BTTS, Over/Under, Corners)
        Endpoint: GET /odds/pre-match/fixtures/{fixture_id}/markets/{market_id}
        """
        print(f"\n🎯 Fetching market {market_id} odds for fixture {fixture_id}...")
        
        response = self._make_request(f'football/odds/pre-match/fixtures/{fixture_id}/markets/{market_id}')
        
        if response and 'data' in response:
            return self._normalize_odds(response['data'])
        
        return []
    
    def get_latest_odds_updates(self) -> List[Dict]:
        """
        Get latest updated pre-match odds (for real-time monitoring)
        Endpoint: GET /odds/pre-match/latest
        """
        print(f"\n🔄 Fetching latest odds updates...")
        
        response = self._make_request('football/odds/pre-match/latest')
        
        if response and 'data' in response:
            updates = response['data']
            print(f"📊 Found {len(updates)} recent odds updates")
            return updates
        
        return []
    
    def get_team_form(self, team_id: int, last_matches: int = 5) -> List[Dict]:
        """
        Get team form with recent results
        Endpoint: GET /teams/{team_id}?include=latest:5;latest.opponent;latest.league
        """
        print(f"\n📈 Fetching form for team {team_id} (last {last_matches} matches)...")
        
        params = {
            'include': f'latest:{last_matches},latest.opponent,latest.league,latest.scores'
        }
        
        response = self._make_request(f'football/teams/{team_id}', params)
        
        if response and 'data' in response:
            team_data = response['data']
            latest_matches = team_data.get('latest', [])
            print(f"📊 Found {len(latest_matches)} recent matches")
            return self._normalize_team_form(latest_matches)
        
        return []
    
    def get_fixture_xg_data(self, fixture_id: int) -> Dict:
        """
        Get xG data for fixture
        Endpoint: GET /fixtures/{fixture_id}?include=xGFixture
        """
        print(f"\n⚽ Fetching xG data for fixture {fixture_id}...")
        
        params = {
            'include': 'xGFixture,participants,scores'
        }
        
        response = self._make_request(f'football/fixtures/{fixture_id}', params)
        
        if response and 'data' in response:
            xg_data = response['data'].get('xGFixture', {})
            if xg_data:
                print(f"📊 xG data available")
                return self._normalize_xg_data(xg_data)
        
        print("⚠️ No xG data available")
        return {}
    
    def get_fixture_statistics(self, fixture_id: int) -> Dict:
        """
        Get detailed fixture statistics including corners
        Endpoint: GET /fixtures/{fixture_id}?include=statistics;statistics.type
        """
        print(f"\n📊 Fetching statistics for fixture {fixture_id}...")
        
        params = {
            'include': 'statistics,statistics.type,participants'
        }
        
        response = self._make_request(f'football/fixtures/{fixture_id}', params)
        
        if response and 'data' in response:
            stats = response['data'].get('statistics', [])
            print(f"📊 Found {len(stats)} statistical categories")
            return self._normalize_statistics(stats)
        
        return {}
    
    def get_markets_list(self) -> List[Dict]:
        """
        Get all available betting markets
        Endpoint: GET /odds/markets
        """
        print(f"\n🏪 Fetching available betting markets...")
        
        response = self._make_request('football/odds/markets')
        
        if response and 'data' in response:
            markets = response['data']
            print(f"📊 Found {len(markets)} betting markets")
            return markets
        
        return []
    
    def search_market_by_name(self, market_name: str) -> List[Dict]:
        """
        Search for specific market (e.g., 'btts', 'corners', 'match winner')
        Endpoint: GET /odds/markets/search/{query}
        """
        print(f"\n🔍 Searching for market: {market_name}...")
        
        response = self._make_request(f'football/odds/markets/search/{market_name}')
        
        if response and 'data' in response:
            markets = response['data']
            print(f"📊 Found {len(markets)} matching markets")
            return markets
        
        return []
    
    def get_sportmonks_predictions(self, fixture_id: int) -> Dict:
        """
        Get SportMonks AI predictions for fixture
        Endpoint: GET /predictions/probabilities/fixtures/{fixture_id}
        """
        print(f"\n🤖 Fetching AI predictions for fixture {fixture_id}...")
        
        response = self._make_request(f'football/predictions/probabilities/fixtures/{fixture_id}')
        
        if response and 'data' in response:
            predictions = response['data']
            print(f"📊 AI predictions available")
            return predictions
        
        return {}
    
    def get_value_bets(self, fixture_id: int) -> List[Dict]:
        """
        Get SportMonks value bet recommendations
        Endpoint: GET /predictions/value-bets/fixtures/{fixture_id}
        """
        print(f"\n💎 Fetching value bets for fixture {fixture_id}...")
        
        response = self._make_request(f'football/predictions/value-bets/fixtures/{fixture_id}')
        
        if response and 'data' in response:
            value_bets = response['data']
            print(f"📊 Found {len(value_bets)} value bet opportunities")
            return value_bets
        
        return []
    
    # Normalization methods to maintain compatibility
    def _normalize_fixtures(self, fixtures: List[Dict]) -> List[Dict]:
        """Normalize Sportmonks fixtures to standard format"""
        normalized = []
        
        for fixture in fixtures:
            participants = fixture.get('participants', [])
            home_team = next((p for p in participants if p.get('meta', {}).get('location') == 'home'), {})
            away_team = next((p for p in participants if p.get('meta', {}).get('location') == 'away'), {})
            
            # Get scores
            scores = fixture.get('scores', [])
            home_score = None
            away_score = None
            
            for score in scores:
                if score.get('description') == 'CURRENT' or score.get('description') == 'FT':
                    participant_id = score.get('participant_id')
                    goals = score.get('score', {}).get('goals', 0)
                    
                    if participant_id == home_team.get('id'):
                        home_score = goals
                    elif participant_id == away_team.get('id'):
                        away_score = goals
            
            normalized_fixture = {
                'fixture': {
                    'id': fixture.get('id'),
                    'date': fixture.get('starting_at'),
                    'status': {
                        'short': fixture.get('state', {}).get('short_name', 'NS'),
                        'long': fixture.get('state', {}).get('state', 'Not Started')
                    },
                    'venue': {
                        'name': fixture.get('venue', {}).get('name', 'Unknown'),
                        'city': fixture.get('venue', {}).get('city', 'Unknown')
                    }
                },
                'league': {
                    'id': fixture.get('league', {}).get('id'),
                    'name': fixture.get('league', {}).get('name', 'Unknown League'),
                    'country': fixture.get('league', {}).get('country', {}).get('name', 'Unknown')
                },
                'teams': {
                    'home': {
                        'id': home_team.get('id'),
                        'name': home_team.get('name', 'Home Team'),
                        'logo': home_team.get('image_path')
                    },
                    'away': {
                        'id': away_team.get('id'),
                        'name': away_team.get('name', 'Away Team'),
                        'logo': away_team.get('image_path')
                    }
                },
                'goals': {
                    'home': home_score,
                    'away': away_score
                },
                'score': {
                    'halftime': {
                        'home': None,
                        'away': None
                    },
                    'fulltime': {
                        'home': home_score,
                        'away': away_score
                    }
                }
            }
            
            normalized.append(normalized_fixture)
        
        return normalized
    
    def _normalize_odds(self, odds_data: List[Dict]) -> List[Dict]:
        """Normalize Sportmonks odds to standard format"""
        normalized = []
        
        for odd_item in odds_data:
            bookmaker = odd_item.get('bookmaker', {})
            market = odd_item.get('market', {})
            
            normalized_odd = {
                'bookmaker': {
                    'id': bookmaker.get('id'),
                    'name': bookmaker.get('name', 'Unknown'),
                },
                'market': {
                    'id': market.get('id'),
                    'name': market.get('name', 'Unknown Market'),
                    'description': market.get('description', '')
                },
                'odds': {
                    'value': odd_item.get('value'),
                    'label': odd_item.get('label'),
                    'dp3': odd_item.get('dp3'),
                    'fractional': odd_item.get('fractional'),
                    'american': odd_item.get('american'),
                    'winning': odd_item.get('winning'),
                    'stopped': odd_item.get('stopped'),
                    'handicap': odd_item.get('handicap'),
                    'total': odd_item.get('total'),
                    'last_update': odd_item.get('last_update')
                }
            }
            
            normalized.append(normalized_odd)
        
        return normalized
    
    def _normalize_team_form(self, matches: List[Dict]) -> List[Dict]:
        """Normalize team form data"""
        normalized = []
        
        for match in matches:
            normalized_match = {
                'fixture': {
                    'id': match.get('id'),
                    'date': match.get('starting_at')
                },
                'teams': {
                    'home': {
                        'id': match.get('home_team_id'),
                        'name': match.get('home_team', {}).get('name', 'Home Team')
                    },
                    'away': {
                        'id': match.get('away_team_id'),
                        'name': match.get('away_team', {}).get('name', 'Away Team')
                    }
                },
                'goals': {
                    'home': match.get('home_score'),
                    'away': match.get('away_score')
                },
                'league': {
                    'name': match.get('league', {}).get('name', 'Unknown League')
                }
            }
            normalized.append(normalized_match)
        
        return normalized
    
    def _normalize_xg_data(self, xg_data: Dict) -> Dict:
        """Normalize xG data"""
        return {
            'home_xg': xg_data.get('home_xg', 0.0),
            'away_xg': xg_data.get('away_xg', 0.0),
            'total_xg': xg_data.get('total_xg', 0.0)
        }
    
    def _normalize_statistics(self, stats: List[Dict]) -> Dict:
        """Normalize fixture statistics"""
        normalized_stats = {
            'home': {},
            'away': {}
        }
        
        for stat in stats:
            stat_type = stat.get('type', {})
            participant_id = stat.get('participant_id')
            value = stat.get('value')
            
            location = 'home' if stat.get('location') == 'home' else 'away'
            stat_name = stat_type.get('name', 'unknown').lower().replace(' ', '_')
            
            normalized_stats[location][stat_name] = value
        
        return normalized_stats
    
    # Keep compatibility methods
    def get_match_statistics(self, fixture_id: int) -> Dict:
        """Compatibility method"""
        return self.get_fixture_statistics(fixture_id)
    
    def get_league_standings(self, league_id: int, season: int = None) -> List[Dict]:
        """Get league standings (placeholder for now)"""
        print(f"⚠️ League standings not implemented in real-time version")
        return []
    
    def get_team_info(self, team_id: int) -> Optional[Dict]:
        """Get team information"""
        response = self._make_request(f'football/teams/{team_id}')
        if response and 'data' in response:
            team = response['data']
            return {
                'team': {
                    'id': team.get('id'),
                    'name': team.get('name'),
                    'logo': team.get('image_path'),
                    'founded': team.get('founded'),
                    'venue': team.get('venue', {}).get('name')
                }
            }
        return None
    
    def get_fixture_details(self, fixture_id: int) -> Optional[Dict]:
        """Get detailed fixture information"""
        params = {
            'include': 'participants,venue,league,season,statistics,scores,states'
        }
        
        response = self._make_request(f'football/fixtures/{fixture_id}', params)
        
        if response and 'data' in response:
            return self._normalize_fixtures([response['data']])[0]
        return None