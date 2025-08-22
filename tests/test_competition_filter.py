#!/usr/bin/env python3
"""
Test competition filter for FIXORA PRO
"""

import unittest
import sys
import os
import tempfile
import yaml

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from filters.competition_filter import CompetitionFilter

class TestCompetitionFilter(unittest.TestCase):
    """Test competition filtering functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary config files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create leagues.yaml
        self.leagues_config = {
            'timezone': 'Europe/London',
            'show_past_matches': False,
            'future_cutoff_minutes': 0,
            'include_competitions': {
                'uefa': [
                    'UEFA Champions League',
                    'UEFA Europa League',
                    'UEFA Europa Conference League'
                ],
                'domestics': [
                    'English Premier League',
                    'La Liga',
                    'Serie A',
                    'Bundesliga',
                    'Ligue 1'
                ]
            }
        }
        
        self.leagues_path = os.path.join(self.temp_dir, 'leagues.yaml')
        with open(self.leagues_path, 'w') as f:
            yaml.dump(self.leagues_config, f)
        
        # Create league_ids.yaml
        self.ids_config = {
            'api_football': {
                'uefa': {
                    'UEFA Champions League': 2,
                    'UEFA Europa League': 3,
                    'UEFA Europa Conference League': 848
                },
                'domestics': {
                    'English Premier League': 39,
                    'La Liga': 140,
                    'Serie A': 135,
                    'Bundesliga': 78,
                    'Ligue 1': 61
                }
            },
            'sportmonks': {
                'uefa': {
                    'UEFA Champions League': 732,
                    'UEFA Europa League': 733,
                    'UEFA Europa Conference League': 1129
                },
                'domestics': {
                    'English Premier League': 8,
                    'La Liga': 564,
                    'Serie A': 384,
                    'Bundesliga': 8,
                    'Ligue 1': 301
                }
            }
        }
        
        self.ids_path = os.path.join(self.temp_dir, 'league_ids.yaml')
        with open(self.ids_path, 'w') as f:
            yaml.dump(self.ids_config, f)
        
        # Create filter with custom paths
        self.filter = CompetitionFilter()
        self.filter.config_path = self.leagues_path
        self.filter.ids_path = self.ids_path
        self.filter.allowed_competitions = self.filter._load_competitions()
        self.filter.league_ids = self.filter._load_league_ids()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_competitions(self):
        """Test loading competitions from config"""
        competitions = self.filter._load_competitions()
        self.assertIn('uefa', competitions)
        self.assertIn('domestics', competitions)
        self.assertEqual(len(competitions['uefa']), 3)
        self.assertEqual(len(competitions['domestics']), 5)
    
    def test_load_league_ids(self):
        """Test loading league IDs from config"""
        ids = self.filter._load_league_ids()
        self.assertIn('api_football', ids)
        self.assertIn('sportmonks', ids)
        self.assertEqual(ids['api_football']['uefa']['UEFA Champions League'], 2)
        self.assertEqual(ids['sportmonks']['domestics']['English Premier League'], 8)
    
    def test_is_allowed_competition(self):
        """Test competition allowance checking"""
        # Test UEFA competitions
        self.assertTrue(self.filter.is_allowed_competition('UEFA Champions League'))
        self.assertTrue(self.filter.is_allowed_competition('UEFA Europa League'))
        self.assertTrue(self.filter.is_allowed_competition('UEFA Europa Conference League'))
        
        # Test domestic competitions
        self.assertTrue(self.filter.is_allowed_competition('English Premier League'))
        self.assertTrue(self.filter.is_allowed_competition('La Liga'))
        self.assertTrue(self.filter.is_allowed_competition('Serie A'))
        self.assertTrue(self.filter.is_allowed_competition('Bundesliga'))
        self.assertTrue(self.filter.is_allowed_competition('Ligue 1'))
        
        # Test non-allowed competitions
        self.assertFalse(self.filter.is_allowed_competition('Scottish Premiership'))
        self.assertFalse(self.filter.is_allowed_competition('Unknown League'))
        self.assertFalse(self.filter.is_allowed_competition(''))
        self.assertFalse(self.filter.is_allowed_competition(None))
    
    def test_get_competition_group(self):
        """Test getting competition display group"""
        # Test UEFA competitions
        self.assertEqual(self.filter.get_competition_group('UEFA Champions League'), 'UEFA')
        self.assertEqual(self.filter.get_competition_group('UEFA Europa League'), 'UEFA')
        self.assertEqual(self.filter.get_competition_group('UEFA Europa Conference League'), 'UEFA')
        
        # Test domestic competitions
        self.assertEqual(self.filter.get_competition_group('English Premier League'), 'Domestic')
        self.assertEqual(self.filter.get_competition_group('La Liga'), 'Domestic')
        self.assertEqual(self.filter.get_competition_group('Serie A'), 'Domestic')
        
        # Test non-allowed competitions
        self.assertIsNone(self.filter.get_competition_group('Scottish Premiership'))
        self.assertIsNone(self.filter.get_competition_group(''))
        self.assertIsNone(self.filter.get_competition_group(None))
    
    def test_get_league_ids(self):
        """Test getting league IDs for providers"""
        # Test API-Football IDs
        api_football_ids = self.filter.get_league_ids('api_football')
        self.assertIn(2, api_football_ids)  # UEFA Champions League
        self.assertIn(39, api_football_ids)  # English Premier League
        self.assertEqual(len(api_football_ids), 8)  # 3 UEFA + 5 domestic
        
        # Test SportMonks IDs
        sportmonks_ids = self.filter.get_league_ids('sportmonks')
        self.assertIn(732, sportmonks_ids)  # UEFA Champions League
        self.assertIn(8, sportmonks_ids)    # English Premier League
        self.assertEqual(len(sportmonks_ids), 8)  # 3 UEFA + 5 domestic
        
        # Test non-existent provider
        empty_ids = self.filter.get_league_ids('non_existent')
        self.assertEqual(len(empty_ids), 0)
    
    def test_filter_fixtures(self):
        """Test filtering fixtures by allowed competitions"""
        # Create test fixtures
        test_fixtures = [
            {
                'id': 1,
                'league': {'name': 'UEFA Champions League'},
                'teams': {'home': {'name': 'Team A'}, 'away': {'name': 'Team B'}}
            },
            {
                'id': 2,
                'league': {'name': 'English Premier League'},
                'teams': {'home': {'name': 'Team C'}, 'away': {'name': 'Team D'}}
            },
            {
                'id': 3,
                'league': {'name': 'Scottish Premiership'},
                'teams': {'home': {'name': 'Team E'}, 'away': {'name': 'Team F'}}
            },
            {
                'id': 4,
                'competition': {'name': 'La Liga'},
                'teams': {'home': {'name': 'Team G'}, 'away': {'name': 'Team H'}}
            }
        ]
        
        # Filter fixtures
        filtered_fixtures = self.filter.filter_fixtures(test_fixtures)
        
        # Should only include allowed competitions
        self.assertEqual(len(filtered_fixtures), 3)
        
        # Check display groups are set
        uefa_count = sum(1 for f in filtered_fixtures if f.get('display_group') == 'UEFA')
        domestic_count = sum(1 for f in filtered_fixtures if f.get('display_group') == 'Domestic')
        
        self.assertEqual(uefa_count, 1)  # UEFA Champions League
        self.assertEqual(domestic_count, 2)  # EPL + La Liga
        
        # Scottish Premiership should be excluded
        scottish_fixtures = [f for f in filtered_fixtures if 'Scottish Premiership' in str(f)]
        self.assertEqual(len(scottish_fixtures), 0)
    
    def test_extract_competition_name(self):
        """Test extracting competition names from different fixture formats"""
        # Test with 'league' key
        fixture1 = {'league': {'name': 'UEFA Champions League'}}
        self.assertEqual(self.filter._extract_competition_name(fixture1), 'UEFA Champions League')
        
        # Test with 'competition' key
        fixture2 = {'competition': {'name': 'English Premier League'}}
        self.assertEqual(self.filter._extract_competition_name(fixture2), 'English Premier League')
        
        # Test with string value
        fixture3 = {'league': 'La Liga'}
        self.assertEqual(self.filter._extract_competition_name(fixture3), 'La Liga')
        
        # Test with nested structure
        fixture4 = {'tournament': {'title': 'Serie A'}}
        self.assertEqual(self.filter._extract_competition_name(fixture4), 'Serie A')
        
        # Test fallback for unknown format
        fixture5 = {'name': 'Team A vs Team B'}
        self.assertEqual(self.filter._extract_competition_name(fixture5), 'Unknown Competition')
    
    def test_validate_league_ids(self):
        """Test league ID validation"""
        validation = self.filter.validate_league_ids()
        
        self.assertIn('valid_competitions', validation)
        self.assertIn('missing_ids', validation)
        
        # All configured competitions should have IDs
        self.assertEqual(len(validation['valid_competitions']), 8)
        self.assertEqual(len(validation['missing_ids']), 0)
        
        # Check specific competitions are valid
        self.assertIn('UEFA Champions League', validation['valid_competitions'])
        self.assertIn('English Premier League', validation['valid_competitions'])

if __name__ == '__main__':
    unittest.main()
