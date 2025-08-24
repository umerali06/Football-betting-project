#!/usr/bin/env python3
"""
Test ROI Contract for FIXORA PRO
Ensures tracker outputs percent values and reports read correct keys
"""

import unittest
import sys
import os
import tempfile
import sqlite3
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from betting.roi_tracker import ROITracker
from reports.roi_weekly_report import ROIWeeklyReportGenerator
import config

class TestROIContract(unittest.TestCase):
    """Test that ROI contract is consistent across all modules"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Initialize ROI tracker with temp database
        self.roi_tracker = ROITracker(self.temp_db.name)
        
        # Seed test data
        self._seed_test_data()
    
    def tearDown(self):
        """Clean up test fixtures"""
        os.unlink(self.temp_db.name)
    
    def _seed_test_data(self):
        """Seed the database with test betting data"""
        # Create test bets: 6 won, 4 lost; total stake 100; total return 112
        test_bets = [
            # Winning bets
            {
                'fixture_id': 1, 'league_id': 39, 'league_name': 'EPL',
                'home_team': 'Team A', 'away_team': 'Team B',
                'market_type': 'match_result', 'selection': 'home_win',
                'odds': 2.0, 'stake': 10.0, 'potential_return': 20.0,
                'bet_date': '2024-08-24', 'match_date': '2024-08-24',
                'result': 'won', 'actual_return': 20.0, 'profit_loss': 10.0,
                'roi_percentage': 100.0, 'status': 'won'
            },
            {
                'fixture_id': 2, 'league_id': 39, 'league_name': 'EPL',
                'home_team': 'Team C', 'away_team': 'Team D',
                'market_type': 'match_result', 'selection': 'away_win',
                'odds': 1.8, 'stake': 10.0, 'potential_return': 18.0,
                'bet_date': '2024-08-24', 'match_date': '2024-08-24',
                'result': 'won', 'actual_return': 18.0, 'profit_loss': 8.0,
                'roi_percentage': 80.0, 'status': 'won'
            },
            {
                'fixture_id': 3, 'league_id': 39, 'league_name': 'EPL',
                'home_team': 'Team E', 'away_team': 'Team F',
                'market_type': 'match_result', 'selection': 'draw',
                'odds': 3.5, 'stake': 10.0, 'potential_return': 35.0,
                'bet_date': '2024-08-24', 'match_date': '2024-08-24',
                'result': 'won', 'actual_return': 35.0, 'profit_loss': 25.0,
                'roi_percentage': 250.0, 'status': 'won'
            },
            {
                'fixture_id': 4, 'league_id': 39, 'league_name': 'EPL',
                'home_team': 'Team G', 'away_team': 'Team H',
                'market_type': 'both_teams_to_score', 'selection': 'yes',
                'odds': 1.9, 'stake': 10.0, 'potential_return': 19.0,
                'bet_date': '2024-08-24', 'match_date': '2024-08-24',
                'result': 'won', 'actual_return': 19.0, 'profit_loss': 9.0,
                'roi_percentage': 90.0, 'status': 'won'
            },
            {
                'fixture_id': 5, 'league_id': 39, 'league_name': 'EPL',
                'home_team': 'Team I', 'away_team': 'Team J',
                'market_type': 'over_under_goals', 'selection': 'over_2.5',
                'odds': 2.1, 'stake': 10.0, 'potential_return': 21.0,
                'bet_date': '2024-08-24', 'match_date': '2024-08-24',
                'result': 'won', 'actual_return': 21.0, 'profit_loss': 11.0,
                'roi_percentage': 110.0, 'status': 'won'
            },
            {
                'fixture_id': 6, 'league_id': 39, 'league_name': 'EPL',
                'home_team': 'Team K', 'away_team': 'Team L',
                'market_type': 'corners', 'selection': 'over_10.5',
                'odds': 1.85, 'stake': 10.0, 'potential_return': 18.5,
                'bet_date': '2024-08-24', 'match_date': '2024-08-24',
                'result': 'won', 'actual_return': 18.5, 'profit_loss': 8.5,
                'roi_percentage': 85.0, 'status': 'won'
            },
            # Losing bets
            {
                'fixture_id': 7, 'league_id': 39, 'league_name': 'EPL',
                'home_team': 'Team M', 'away_team': 'Team N',
                'market_type': 'match_result', 'selection': 'home_win',
                'odds': 1.5, 'stake': 10.0, 'potential_return': 15.0,
                'bet_date': '2024-08-24', 'match_date': '2024-08-24',
                'result': 'lost', 'actual_return': 0.0, 'profit_loss': -10.0,
                'roi_percentage': -100.0, 'status': 'lost'
            },
            {
                'fixture_id': 8, 'league_id': 39, 'league_name': 'EPL',
                'home_team': 'Team O', 'away_team': 'Team P',
                'market_type': 'both_teams_to_score', 'selection': 'no',
                'odds': 2.2, 'stake': 10.0, 'potential_return': 22.0,
                'bet_date': '2024-08-24', 'match_date': '2024-08-24',
                'result': 'lost', 'actual_return': 0.0, 'profit_loss': -10.0,
                'roi_percentage': -100.0, 'status': 'lost'
            },
            {
                'fixture_id': 9, 'league_id': 39, 'league_name': 'EPL',
                'home_team': 'Team Q', 'away_team': 'Team R',
                'market_type': 'over_under_goals', 'selection': 'under_2.5',
                'odds': 1.7, 'stake': 10.0, 'potential_return': 17.0,
                'bet_date': '2024-08-24', 'match_date': '2024-08-24',
                'result': 'lost', 'actual_return': 0.0, 'profit_loss': -10.0,
                'roi_percentage': -100.0, 'status': 'lost'
            },
            {
                'fixture_id': 10, 'league_id': 39, 'league_name': 'EPL',
                'home_team': 'Team S', 'away_team': 'Team T',
                'market_type': 'corners', 'selection': 'under_10.5',
                'odds': 1.95, 'stake': 10.0, 'potential_return': 19.5,
                'bet_date': '2024-08-24', 'match_date': '2024-08-24',
                'result': 'lost', 'actual_return': 0.0, 'profit_loss': -10.0,
                'roi_percentage': -100.0, 'status': 'lost'
            }
        ]
        
        # Insert test bets
        for bet in test_bets:
            success, bet_id = self.roi_tracker.record_bet(bet)
            if success and bet.get('result') in ['won', 'lost']:
                # Update bet result for completed bets
                result = 'win' if bet['result'] == 'won' else 'loss'
                actual_return = bet.get('actual_return', 0.0)
                self.roi_tracker.update_bet_result(bet['fixture_id'], result, actual_return)
    
    def test_overall_performance_contract(self):
        """Test that overall performance returns correct fields and percent values"""
        overall = self.roi_tracker.get_overall_performance()
        
        # Check required fields exist
        required_fields = ['total_bets', 'winning_bets', 'total_stake', 
                          'total_return', 'total_profit_loss', 'win_rate', 'overall_roi']
        
        for field in required_fields:
            self.assertIn(field, overall, f"Missing required field: {field}")
        
        # Check values are correct
        self.assertEqual(overall['total_bets'], 10)
        self.assertEqual(overall['winning_bets'], 6)
        self.assertEqual(overall['total_stake'], 100.0)
        self.assertEqual(overall['total_return'], 131.5)  # Corrected: 6 winning bets with different odds
        self.assertEqual(overall['total_profit_loss'], 31.5)  # Corrected: 131.5 - 100
        
        # Check percent values
        self.assertEqual(overall['win_rate'], 60.0)  # 6/10 * 100
        self.assertEqual(overall['overall_roi'], 31.5)  # Corrected: 31.5/100 * 100
    
    def test_weekly_performance_contract(self):
        """Test that weekly performance returns correct fields and percent values"""
        weekly = self.roi_tracker.get_weekly_performance(days=365)  # Use 1 year to include test data
        
        # Check that we have data for match_result market
        self.assertIn('match_result', weekly)
        
        match_result = weekly['match_result']
        
        # Check required fields exist
        required_fields = ['total_bets', 'winning_bets', 'win_rate', 
                          'total_stake', 'total_return', 'total_profit_loss', 'roi']
        
        for field in required_fields:
            self.assertIn(field, match_result, f"Missing required field: {field}")
        
        # Check percent values
        self.assertEqual(match_result['win_rate'], 75.0)  # 3 wins, 1 loss
        self.assertEqual(match_result['roi'], 82.5)  # (33)/40 * 100 = 82.5%
    
    def test_market_performance_contract(self):
        """Test that market performance returns correct fields and percent values"""
        market_perf = self.roi_tracker.get_market_performance()
        
        # Check that we have data
        self.assertGreater(len(market_perf), 0)
        
        for market in market_perf:
            # Check required fields exist
            required_fields = ['market_type', 'total_bets', 'winning_bets', 
                              'total_stake', 'total_return', 'total_profit_loss', 'overall_roi']
            
            for field in required_fields:
                self.assertIn(field, market, f"Missing required field: {field}")
            
            # Check that ROI is a percent value (not decimal)
            self.assertIsInstance(market['overall_roi'], (int, float))
            # ROI should be reasonable (not 0.15 but 15.0)
            self.assertGreater(market['overall_roi'], -200)  # Allow for losses
            self.assertLess(market['overall_roi'], 300)      # Allow for big wins
    
    def test_league_performance_contract(self):
        """Test that league performance returns correct fields and percent values"""
        league_perf = self.roi_tracker.get_league_performance()
        
        # Check that we have data
        self.assertGreater(len(league_perf), 0)
        
        for league in league_perf:
            # Check required fields exist
            required_fields = ['league_id', 'league_name', 'total_bets', 'winning_bets', 
                              'total_stake', 'total_return', 'total_profit_loss', 'overall_roi']
            
            for field in required_fields:
                self.assertIn(field, league, f"Missing required field: {field}")
            
            # Check that ROI is a percent value
            self.assertIsInstance(league['overall_roi'], (int, float))
            self.assertEqual(league['overall_roi'], 31.5)  # Should be 31.5% for our test data
    
    def test_no_double_percent_formatting(self):
        """Test that reports don't double-format percent values"""
        # Get overall performance
        overall = self.roi_tracker.get_overall_performance()
        
        # Check that values are already in percent format (not decimals)
        self.assertEqual(overall['win_rate'], 60.0)  # Not 0.6
        self.assertEqual(overall['overall_roi'], 31.5)  # Not 0.315
        
        # Check that values are reasonable percentages
        self.assertGreaterEqual(overall['win_rate'], 0)
        self.assertLessEqual(overall['win_rate'], 100)
        self.assertGreaterEqual(overall['overall_roi'], -100)  # Allow for losses
        self.assertLessEqual(overall['overall_roi'], 1000)     # Allow for big wins
    
    def test_roi_calculation_accuracy(self):
        """Test that ROI calculations are mathematically correct"""
        overall = self.roi_tracker.get_overall_performance()
        
        # Manual calculation
        total_stake = overall['total_stake']
        total_profit_loss = overall['total_profit_loss']
        expected_roi = (total_profit_loss / total_stake) * 100
        
        # Check that calculated ROI matches expected
        self.assertAlmostEqual(overall['overall_roi'], expected_roi, places=2)
        
        # Check that win rate calculation is correct
        total_bets = overall['total_bets']
        winning_bets = overall['winning_bets']
        expected_win_rate = (winning_bets / total_bets) * 100
        
        self.assertAlmostEqual(overall['win_rate'], expected_win_rate, places=2)

if __name__ == '__main__':
    unittest.main()
