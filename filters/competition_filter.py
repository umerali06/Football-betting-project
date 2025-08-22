import yaml
import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class CompetitionFilter:
    """Filter fixtures by allowed competitions (UEFA + domestic leagues)"""
    
    def __init__(self):
        self.config_path = Path("config/leagues.yaml")
        self.ids_path = Path("config/league_ids.yaml")
        self.allowed_competitions = self._load_competitions()
        self.league_ids = self._load_league_ids()
    
    def _load_competitions(self) -> Dict:
        """Load allowed competitions from config"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('include_competitions', {})
        except Exception as e:
            logger.error(f"Failed to load leagues config: {e}")
            return {}
    
    def _load_league_ids(self) -> Dict:
        """Load league IDs from config"""
        try:
            with open(self.ids_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config
        except Exception as e:
            logger.error(f"Failed to load league IDs config: {e}")
            return {}
    
    def is_allowed_competition(self, competition_name: str, provider: str = "api_football") -> bool:
        """Check if competition is in allowed list"""
        if not competition_name:
            return False
        
        # Check UEFA competitions
        uefa_comps = self.allowed_competitions.get('uefa', [])
        if competition_name in uefa_comps:
            return True
        
        # Check domestic competitions
        domestic_comps = self.allowed_competitions.get('domestics', [])
        if competition_name in domestic_comps:
            return True
        
        return False
    
    def get_competition_group(self, competition_name: str) -> Optional[str]:
        """Get display group for competition (UEFA or Domestic)"""
        if not competition_name:
            return None
        
        # Check UEFA competitions
        uefa_comps = self.allowed_competitions.get('uefa', [])
        if competition_name in uefa_comps:
            return "UEFA"
        
        # Check domestic competitions
        domestic_comps = self.allowed_competitions.get('domestics', [])
        if competition_name in domestic_comps:
            return "Domestic"
        
        return None
    
    def get_league_ids(self, provider: str = "api_football") -> List[int]:
        """Get all allowed league IDs for a provider"""
        ids = []
        
        if provider not in self.league_ids:
            return ids
        
        provider_ids = self.league_ids[provider]
        
        # Add UEFA league IDs
        uefa_ids = provider_ids.get('uefa', {}).values()
        ids.extend(uefa_ids)
        
        # Add domestic league IDs
        domestic_ids = provider_ids.get('domestics', {}).values()
        ids.extend(domestic_ids)
        
        return ids
    
    def filter_fixtures(self, fixtures: List[Dict]) -> List[Dict]:
        """Filter fixtures to only include allowed competitions"""
        filtered_fixtures = []
        
        for fixture in fixtures:
            competition_name = self._extract_competition_name(fixture)
            
            if self.is_allowed_competition(competition_name):
                # Add display group annotation
                fixture["display_group"] = self.get_competition_group(competition_name)
                filtered_fixtures.append(fixture)
            else:
                logger.debug(f"Excluded fixture from {competition_name} (not in allowed list)")
        
        logger.info(f"Filtered {len(fixtures)} fixtures to {len(filtered_fixtures)} allowed competitions")
        return filtered_fixtures
    
    def _extract_competition_name(self, fixture: Dict) -> str:
        """Extract competition name from fixture data"""
        # Try different possible keys for competition name
        possible_keys = [
            'league', 'competition', 'tournament', 'division'
        ]
        
        for key in possible_keys:
            if key in fixture:
                league_data = fixture[key]
                if isinstance(league_data, dict):
                    # Try different possible sub-keys
                    sub_keys = ['name', 'title', 'full_name']
                    for sub_key in sub_keys:
                        if sub_key in league_data:
                            return league_data[sub_key]
                elif isinstance(league_data, str):
                    return league_data
        
        # Fallback: try to extract from other fields
        if 'name' in fixture and ' vs ' in fixture['name']:
            # This might be a match name, not competition
            return "Unknown Competition"
        
        return "Unknown Competition"
    
    def validate_league_ids(self) -> Dict[str, List[str]]:
        """Validate that all configured league IDs exist and are accessible"""
        validation_results = {
            'missing_ids': [],
            'invalid_names': [],
            'valid_competitions': []
        }
        
        # Check if all configured competitions have IDs
        all_competitions = []
        all_competitions.extend(self.allowed_competitions.get('uefa', []))
        all_competitions.extend(self.allowed_competitions.get('domestics', []))
        
        for comp_name in all_competitions:
            has_id = False
            for provider in ['api_football', 'sportmonks']:
                if provider in self.league_ids:
                    provider_ids = self.league_ids[provider]
                    uefa_ids = provider_ids.get('uefa', {})
                    domestic_ids = provider_ids.get('domestics', {})
                    
                    if comp_name in uefa_ids or comp_name in domestic_ids:
                        has_id = True
                        break
            
            if has_id:
                validation_results['valid_competitions'].append(comp_name)
            else:
                validation_results['missing_ids'].append(comp_name)
        
        return validation_results
