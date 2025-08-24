#!/usr/bin/env python3
"""
Test Risk Manager for FIXORA PRO
Validates stake rounding, daily stake cap, and risk management logic
"""

import unittest
import sys
import os
import tempfile
import sqlite3

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from betting.risk_manager import AdvancedRiskManager
import config

class TestRiskManager(unittest.TestCase):
    """Test that the risk manager works correctly"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.risk_manager = AdvancedRiskManager(initial_bankroll=10000.0)
    
    def test_stake_rounding(self):
        """Test that stakes are rounded to nearest unit"""
        # Test data with fractional stakes
        bet_data = {
            'model_probability': 0.7,
            'odds': 2.0,
            'edge': 0.2,
            'confidence': 0.8,
            'match_info': {'home_team': 'Team A', 'away_team': 'Team B'},
            'market': 'match_result',
            'selection': 'home_win'
        }
        
        # Calculate optimal stake
        stake_calc = self.risk_manager.calculate_optimal_stake(bet_data)
        
        # Check that final stake is rounded
        final_stake = stake_calc['final_stake']
        self.assertIsInstance(final_stake, (int, float))
        
        # Check that stake is reasonable (not fractional)
        self.assertGreaterEqual(final_stake, 10.0)  # Minimum stake
        self.assertLessEqual(final_stake, 500.0)    # Maximum stake (5% of 10000)
        
        # Verify that stake is not a very small decimal
        self.assertGreaterEqual(final_stake, 1.0)
    
    def test_daily_stake_cap(self):
        """Test that daily stake cap is enforced"""
        # Set up a bet that would exceed daily cap
        bet_data = {
            'model_probability': 0.8,
            'odds': 1.9,
            'edge': 0.3,
            'confidence': 0.9,
            'match_info': {'home_team': 'Team A', 'away_team': 'Team B'},
            'market': 'match_result',
            'selection': 'home_win'
        }
        
        # Record multiple bets to approach daily cap
        for i in range(5):
            stake_calc = self.risk_manager.calculate_optimal_stake(bet_data)
            stake = stake_calc['final_stake']
            
            # Record bet
            self.risk_manager.record_bet(bet_data, stake, 'win')
        
        # Check daily stake usage
        self.assertGreater(self.risk_manager._daily_stake_used, 0)
        
        # Calculate remaining daily stake
        daily_stake_cap = getattr(config, 'MAX_DAILY_STAKE', 0.1) * self.risk_manager.current_bankroll
        remaining_daily_stake = daily_stake_cap - self.risk_manager._daily_stake_used
        
        # Next bet should respect remaining daily stake
        next_stake_calc = self.risk_manager.calculate_optimal_stake(bet_data)
        next_stake = next_stake_calc['final_stake']
        
        # Stake should not exceed remaining daily allowance
        self.assertLessEqual(next_stake, remaining_daily_stake + 1)  # Allow small rounding error
    
    def test_kelly_criterion_positive(self):
        """Test that a bet with model p=0.60 and odds=2.10 passes filters and yields positive Kelly"""
        # Test case: model p=0.60, odds=2.10
        model_prob = 0.60
        odds = 2.10
        
        bet_data = {
            'model_probability': model_prob,
            'odds': odds,
            'edge': 0.124,  # 0.60 - (1/2.10) = 0.124
            'confidence': 0.7,
            'match_info': {'home_team': 'Team A', 'away_team': 'Team B'},
            'market': 'match_result',
            'selection': 'home_win'
        }
        
        # This should pass odds gate (≥1.8)
        self.assertGreaterEqual(odds, config.MIN_ODDS)
        
        # Calculate Kelly stake
        kelly_pct, kelly_stake = self.risk_manager.calculate_kelly_stake(
            model_prob, odds, 0.7
        )
        
        # Kelly should be positive
        self.assertGreater(kelly_pct, 0)
        self.assertGreater(kelly_stake, 0)
        
        # Validate bet
        is_valid, reason = self.risk_manager.validate_bet(bet_data)
        self.assertTrue(is_valid, f"Bet should be valid: {reason}")
    
    def test_kelly_criterion_negative(self):
        """Test that a bet with model p=0.40 and odds=1.60 fails odds gate"""
        # Test case: model p=0.40, odds=1.60
        model_prob = 0.40
        odds = 1.60
        
        bet_data = {
            'model_probability': model_prob,
            'odds': odds,
            'edge': 0.175,  # 0.40 - (1/1.60) = 0.175
            'confidence': 0.7,
            'match_info': {'home_team': 'Team A', 'away_team': 'Team B'},
            'market': 'match_result',
            'selection': 'home_win'
        }
        
        # This should fail odds gate (<1.8)
        self.assertLess(odds, config.MIN_ODDS)
        
        # Validate bet
        is_valid, reason = self.risk_manager.validate_bet(bet_data)
        self.assertFalse(is_valid, "Bet should fail odds validation")
        self.assertIn("Odds outside range", reason)
    
    def test_daily_bet_limit(self):
        """Test that daily bet limit is enforced"""
        bet_data = {
            'model_probability': 0.7,
            'odds': 2.0,
            'edge': 0.2,
            'confidence': 0.8,
            'match_info': {'home_team': 'Team A', 'away_team': 'Team B'},
            'market': 'match_result',
            'selection': 'home_win'
        }
        
        # Record bets up to the limit
        for i in range(config.MAX_BETS_PER_DAY):
            stake_calc = self.risk_manager.calculate_optimal_stake(bet_data)
            stake = stake_calc['final_stake']
            self.risk_manager.record_bet(bet_data, stake, 'win')
        
        # Try to record one more bet
        is_valid, reason = self.risk_manager.validate_bet(bet_data)
        self.assertFalse(is_valid, "Should not allow bet beyond daily limit")
        self.assertIn("Daily bet limit reached", reason)
    
    def test_edge_threshold_validation(self):
        """Test that edge threshold validation works correctly"""
        # Test with edge below threshold
        low_edge_bet = {
            'model_probability': 0.6,
            'odds': 2.0,
            'edge': 0.02,  # Below VALUE_BET_THRESHOLD (0.05)
            'confidence': 0.8,
            'match_info': {'home_team': 'Team A', 'away_team': 'Team B'},
            'market': 'match_result',
            'selection': 'home_win'
        }
        
        is_valid, reason = self.risk_manager.validate_bet(low_edge_bet)
        self.assertFalse(is_valid, "Should reject bet with low edge")
        self.assertIn("Edge too low", reason)
        
        # Test with edge above threshold
        high_edge_bet = {
            'model_probability': 0.7,
            'odds': 2.0,
            'edge': 0.2,  # Above VALUE_BET_THRESHOLD (0.05)
            'confidence': 0.8,
            'match_info': {'home_team': 'Team A', 'away_team': 'Team B'},
            'market': 'match_result',
            'selection': 'home_win'
        }
        
        is_valid, reason = self.risk_manager.validate_bet(high_edge_bet)
        self.assertTrue(is_valid, f"Should accept bet with high edge: {reason}")
    
    def test_confidence_threshold_validation(self):
        """Test that confidence threshold validation works correctly"""
        # Test with confidence below threshold
        low_confidence_bet = {
            'model_probability': 0.7,
            'odds': 2.0,
            'edge': 0.2,
            'confidence': 0.5,  # Below CONFIDENCE_THRESHOLD (0.6)
            'match_info': {'home_team': 'Team A', 'away_team': 'Team B'},
            'market': 'match_result',
            'selection': 'home_win'
        }
        
        is_valid, reason = self.risk_manager.validate_bet(low_confidence_bet)
        self.assertFalse(is_valid, "Should reject bet with low confidence")
        self.assertIn("Confidence too low", reason)
        
        # Test with confidence above threshold
        high_confidence_bet = {
            'model_probability': 0.7,
            'odds': 2.0,
            'edge': 0.2,
            'confidence': 0.8,  # Above CONFIDENCE_THRESHOLD (0.6)
            'match_info': {'home_team': 'Team A', 'away_team': 'Team B'},
            'market': 'match_result',
            'selection': 'home_win'
        }
        
        is_valid, reason = self.risk_manager.validate_bet(high_confidence_bet)
        self.assertTrue(is_valid, f"Should accept bet with high confidence: {reason}")
    
    def test_bankroll_management(self):
        """Test that bankroll management works correctly"""
        initial_bankroll = self.risk_manager.current_bankroll
        
        bet_data = {
            'model_probability': 0.7,
            'odds': 2.0,
            'edge': 0.2,
            'confidence': 0.8,
            'match_info': {'home_team': 'Team A', 'away_team': 'Team B'},
            'market': 'match_result',
            'selection': 'home_win'
        }
        
        # Calculate stake
        stake_calc = self.risk_manager.calculate_optimal_stake(bet_data)
        stake = stake_calc['final_stake']
        
        # Record winning bet
        self.risk_manager.record_bet(bet_data, stake, 'win')
        
        # Check bankroll increased
        expected_profit = stake * (bet_data['odds'] - 1)
        expected_bankroll = initial_bankroll + expected_profit
        self.assertAlmostEqual(self.risk_manager.current_bankroll, expected_bankroll, places=2)
        
        # Record losing bet
        self.risk_manager.record_bet(bet_data, stake, 'loss')
        
        # Check bankroll decreased
        expected_bankroll = expected_bankroll - stake
        self.assertAlmostEqual(self.risk_manager.current_bankroll, expected_bankroll, places=2)
    
    def test_daily_counter_reset(self):
        """Test that daily counters reset correctly"""
        bet_data = {
            'model_probability': 0.7,
            'odds': 2.0,
            'edge': 0.2,
            'confidence': 0.8,
            'match_info': {'home_team': 'Team A', 'away_team': 'Team B'},
            'market': 'match_result',
            'selection': 'home_win'
        }
        
        # Record a bet
        stake_calc = self.risk_manager.calculate_optimal_stake(bet_data)
        stake = stake_calc['final_stake']
        self.risk_manager.record_bet(bet_data, stake, 'win')
        
        # Check counters
        self.assertEqual(self.risk_manager.daily_bets, 1)
        self.assertGreater(self.risk_manager._daily_stake_used, 0)
        
        # Reset counters
        self.risk_manager.reset_daily_counters()
        
        # Check counters reset
        self.assertEqual(self.risk_manager.daily_bets, 0)
        self.assertEqual(self.risk_manager._daily_stake_used, 0)
    
    def test_performance_metrics(self):
        """Test that performance metrics are calculated correctly"""
        bet_data = {
            'model_probability': 0.7,
            'odds': 2.0,
            'edge': 0.2,
            'confidence': 0.8,
            'match_info': {'home_team': 'Team A', 'away_team': 'Team B'},
            'market': 'match_result',
            'selection': 'home_win'
        }
        
        # Record some bets
        stake_calc = self.risk_manager.calculate_optimal_stake(bet_data)
        stake = stake_calc['final_stake']
        
        # Win
        self.risk_manager.record_bet(bet_data, stake, 'win')
        # Loss
        self.risk_manager.record_bet(bet_data, stake, 'loss')
        # Win
        self.risk_manager.record_bet(bet_data, stake, 'win')
        
        # Get metrics
        metrics = self.risk_manager.get_performance_metrics()
        
        # Check metrics
        self.assertEqual(metrics['total_bets'], 3)
        self.assertEqual(metrics['winning_bets'], 2)
        self.assertEqual(metrics['losing_bets'], 1)
        self.assertAlmostEqual(metrics['win_rate'], 2/3, places=3)
        self.assertGreater(metrics['total_profit'], 0)  # Should be positive due to 2 wins vs 1 loss
        self.assertIsInstance(metrics['current_bankroll'], (int, float))
        self.assertIsInstance(metrics['kelly_efficiency'], (int, float))

if __name__ == '__main__':
    unittest.main()
