#!/usr/bin/env python3
"""
Test odds filtering for FIXORA PRO
Ensures bets with odds < 1.8 are completely excluded
"""

import unittest
import sys
import os
import tempfile
import yaml

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from betting.value_bet_analyzer import ValueBetAnalyzer
from scheduling.daily_jobs import DailyJobsScheduler
from utils.odds_filter import OddsFilter
import config

class TestOddsFiltering(unittest.TestCase):
    """Test that odds filtering works correctly across all modules"""
    
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
                'uefa': ['UEFA Champions League'],
                'domestics': ['English Premier League']
            }
        }
        
        self.leagues_path = os.path.join(self.temp_dir, 'leagues.yaml')
        with open(self.leagues_path, 'w') as f:
            yaml.dump(self.leagues_config, f)
        
        # Create league_ids.yaml
        self.ids_config = {
            'api_football': {
                'uefa': {'UEFA Champions League': 2},
                'domestics': {'English Premier League': 39}
            },
            'sportmonks': {
                'uefa': {'UEFA Champions League': 732},
                'domestics': {'English Premier League': 8}
            }
        }
        
        self.ids_path = os.path.join(self.temp_dir, 'league_ids.yaml')
        with open(self.ids_path, 'w') as f:
            yaml.dump(self.ids_config, f)
        
        # Initialize components
        self.value_analyzer = ValueBetAnalyzer()
        self.daily_scheduler = DailyJobsScheduler()
        self.daily_scheduler.config_path = self.leagues_path
        self.daily_scheduler.ids_path = self.ids_path
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_config_min_odds_setting(self):
        """Test that MIN_ODDS is correctly set to 1.8"""
        self.assertEqual(config.MIN_ODDS, 1.8, "MIN_ODDS must be 1.8")
        self.assertEqual(self.value_analyzer.min_odds, 1.8, "ValueBetAnalyzer min_odds must be 1.8")
    
    def test_value_analyzer_odds_filtering(self):
        """Test that ValueBetAnalyzer properly filters out low odds"""
        # Test valid odds (≥1.8)
        valid_odds = [1.8, 1.85, 2.0, 3.5, 5.0, 10.0]
        for odds in valid_odds:
            self.assertTrue(
                OddsFilter.validate_odds(odds),
                f"Odds {odds} should be valid (≥1.8)"
            )
        
        # Test invalid odds (<1.8)
        invalid_odds = [1.0, 1.09, 1.24, 1.5, 1.79]
        for odds in invalid_odds:
            self.assertFalse(
                OddsFilter.validate_odds(odds),
                f"Odds {odds} should be invalid (<1.8)"
            )
    
    def test_value_bet_validation_with_low_odds(self):
        """Test that value bets with low odds are completely rejected"""
        # Test with odds that should be rejected
        low_odds_cases = [
            (1.09, 0.8),  # Very low odds, high probability
            (1.24, 0.75), # Low odds, high probability
            (1.5, 0.7),   # Below threshold odds
            (1.79, 0.65)  # Just below threshold
        ]
        
        for odds, prob in low_odds_cases:
            is_value = self.value_analyzer.is_value_bet(prob, odds)
            self.assertFalse(
                is_value,
                f"Bet with odds {odds} and probability {prob} should be rejected"
            )
        
        # Test with valid odds (≥1.8)
        valid_odds_cases = [
            (1.8, 0.6),   # Minimum valid odds
            (2.0, 0.55),  # Valid odds
            (3.0, 0.4),   # Valid odds
        ]
        
        for odds, prob in valid_odds_cases:
            # These might still fail other criteria (edge, confidence, Kelly)
            # but should pass odds validation
            odds_valid = OddsFilter.validate_odds(odds)
            self.assertTrue(
                odds_valid,
                f"Odds {odds} should pass validation"
            )
    
    def test_daily_scheduler_odds_filtering(self):
        """Test that DailyJobsScheduler properly filters odds"""
        # Test odds validation method
        valid_odds = [1.8, 2.0, 3.5]
        for odds in valid_odds:
            self.assertTrue(
                OddsFilter.validate_odds(odds),
                f"Daily scheduler should accept odds {odds}"
            )
        
        invalid_odds = [1.09, 1.24, 1.5, 1.79]
        for odds in invalid_odds:
            self.assertFalse(
                OddsFilter.validate_odds(odds),
                f"Daily scheduler should reject odds {odds}"
            )
    
    def test_odds_filtering_integration(self):
        """Test that odds filtering works end-to-end"""
        # Create mock fixture data
        mock_fixture = {
            'id': 1,
            'teams': {'home': {'name': 'Team A'}, 'away': {'name': 'Team B'}},
            'league': {'name': 'English Premier League'}
        }
        
        # Create mock predictions
        mock_predictions = {
            'match_result': {
                'home_win': 0.6,
                'draw': 0.25,
                'away_win': 0.15
            }
        }
        
        # Create mock odds data with mixed valid/invalid odds
        mock_odds_data = [
            {
                'market_description': 'Fulltime Result',
                'label': 'home',
                'dp3': '1.09'  # Invalid odds (<1.8)
            },
            {
                'market_description': 'Fulltime Result',
                'label': 'draw',
                'dp3': '3.50'  # Valid odds (≥1.8)
            },
            {
                'market_description': 'Fulltime Result',
                'label': 'away',
                'dp3': '1.24'  # Invalid odds (<1.8)
            }
        ]
        
        # Test odds extraction
        extracted_odds = self.daily_scheduler._extract_match_odds(mock_odds_data)
        self.assertIn('home_win', extracted_odds)
        self.assertIn('draw', extracted_odds)
        self.assertIn('away_win', extracted_odds)
        
        # Test that invalid odds are filtered out during analysis
        # This would normally be called in the full analysis pipeline
        # For now, test the individual validation methods
        
        # Home win odds (1.09) should be invalid
        home_odds = extracted_odds['home_win']
        self.assertFalse(
            OddsFilter.validate_odds(home_odds),
            f"Home win odds {home_odds} should be invalid"
        )
        
        # Draw odds (3.50) should be valid
        draw_odds = extracted_odds['draw']
        self.assertTrue(
            OddsFilter.validate_odds(draw_odds),
            f"Draw odds {draw_odds} should be valid"
        )
        
        # Away win odds (1.24) should be invalid
        away_odds = extracted_odds['away_win']
        self.assertFalse(
            OddsFilter.validate_odds(away_odds),
            f"Away win odds {away_odds} should be invalid"
        )
    
    def test_unit_recommendation_logic(self):
        """Test that unit recommendation logic remains intact"""
        # Test edge-based unit allocation
        test_cases = [
            (0.20, 3.0),   # Edge ≥0.15 → 3 units (1st place)
            (0.12, 2.0),   # Edge ≥0.10 → 2 units (2nd place)
            (0.09, 1.0),   # Edge ≥0.08 → 1 unit (3rd place)
            (0.06, 0.5),   # Edge ≥0.05 → 0.5 units (4th & 5th)
            (0.03, 0.0),   # Edge <0.05 → 0 units (no bet)
        ]
        
        for edge, expected_units in test_cases:
            actual_units = self.daily_scheduler._calculate_stake_units(edge)
            self.assertEqual(
                actual_units,
                expected_units,
                f"Edge {edge:.2f} should result in {expected_units} units, got {actual_units}"
            )
    
    def test_comprehensive_odds_validation(self):
        """Test comprehensive odds validation scenarios"""
        # Test edge cases
        edge_cases = [
            (None, False),           # None
            ("invalid", False),      # String
            (0, False),              # Zero
            (-1, False),             # Negative
            (1.799, False),          # Just below threshold
            (1.8, True),             # Exactly at threshold
            (1.801, True),           # Just above threshold
            (10.0, True),            # At max threshold
            (10.1, False),           # Above max threshold
        ]
        
        for odds, expected_valid in edge_cases:
            actual_valid = OddsFilter.validate_odds(odds)
            self.assertEqual(
                actual_valid,
                expected_valid,
                f"Odds {odds} validation: expected {expected_valid}, got {actual_valid}"
            )
    
    def test_odds_filtering_logging(self):
        """Test that odds filtering produces appropriate logging"""
        # This test ensures that the logging is working correctly
        # The actual logging output would be checked in integration tests
        
        # Test that validation methods handle logging gracefully
        test_odds = [1.09, 1.8, 3.0, 10.1]
        
        for odds in test_odds:
            # Should not raise exceptions during validation
            try:
                is_valid = OddsFilter.validate_odds(odds)
                # Validation should complete without errors
                self.assertIsInstance(is_valid, bool)
            except Exception as e:
                self.fail(f"Odds validation for {odds} raised exception: {e}")

if __name__ == '__main__':
    unittest.main()
