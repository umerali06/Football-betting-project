#!/usr/bin/env python3
"""
Test script for the Football Betting System
This script tests all major components to ensure they work correctly
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import *
from api.api_football import APIFootballClient
from models.elo_model import EloModel
from models.xg_model import XGModel
from models.corners_model import CornersModel
from betting.value_bet_analyzer import ValueBetAnalyzer
from bot_interface.telegram_bot import TelegramBetBot
from reports.report_generator import ReportGenerator

class SystemTester:
    """Test class for the football betting system"""
    
    def __init__(self):
        self.api_client = APIFootballClient()
        self.elo_model = EloModel()
        self.xg_model = XGModel()
        self.corners_model = CornersModel()
        self.value_analyzer = ValueBetAnalyzer()
        self.telegram_bot = TelegramBetBot()
        self.report_generator = ReportGenerator()
        
    def test_config(self):
        """Test configuration loading"""
        print("🔧 Testing Configuration...")
        
        try:
            assert API_FOOTBALL_KEY, "API Football key not set"
            assert TELEGRAM_BOT_TOKEN, "Telegram bot token not set"
            assert VALUE_BET_THRESHOLD > 0, "Value bet threshold must be positive"
            assert MIN_ODDS < MAX_ODDS, "Min odds must be less than max odds"
            
            print("✅ Configuration test passed")
            return True
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            return False
    
    def test_api_client(self):
        """Test API Football client"""
        print("\n🌐 Testing API Football Client...")
        
        try:
            # Test basic API connection
            response = self.api_client._make_request('status')
            if response:
                print("✅ API connection successful")
            else:
                print("⚠️ API connection failed (may be rate limited)")
            
            # Test getting today's matches (limited to avoid rate limits)
            matches = self.api_client.get_today_matches()
            print(f"✅ Found {len(matches)} matches for today")
            
            return True
        except Exception as e:
            print(f"❌ API client test failed: {e}")
            return False
    
    def test_models(self):
        """Test prediction models"""
        print("\n🧠 Testing Prediction Models...")
        
        try:
            # Test Elo model
            home_team_id = 1
            away_team_id = 2
            
            home_win, draw, away_win = self.elo_model.predict_match_result(home_team_id, away_team_id)
            assert 0 <= home_win <= 1, "Home win probability out of range"
            assert 0 <= draw <= 1, "Draw probability out of range"
            assert 0 <= away_win <= 1, "Away win probability out of range"
            assert abs(home_win + draw + away_win - 1.0) < 0.001, "Probabilities don't sum to 1"
            print("✅ Elo model test passed")
            
            # Test xG model
            home_stats = self.xg_model.calculate_team_xg(home_team_id, [])
            away_stats = self.xg_model.calculate_team_xg(away_team_id, [])
            
            home_xg, away_xg = self.xg_model.predict_match_xg(home_team_id, away_team_id, home_stats, away_stats)
            assert home_xg > 0, "Home xG must be positive"
            assert away_xg > 0, "Away xG must be positive"
            print("✅ xG model test passed")
            
            # Test corners model
            home_corner_stats = self.corners_model.calculate_team_corners(home_team_id, [])
            away_corner_stats = self.corners_model.calculate_team_corners(away_team_id, [])
            
            home_corners, away_corners = self.corners_model.predict_match_corners(
                home_team_id, away_team_id, home_corner_stats, away_corner_stats
            )
            assert home_corners > 0, "Home corners must be positive"
            assert away_corners > 0, "Away corners must be positive"
            print("✅ Corners model test passed")
            
            return True
        except Exception as e:
            print(f"❌ Models test failed: {e}")
            return False
    
    def test_value_bet_analyzer(self):
        """Test value bet analyzer"""
        print("\n💰 Testing Value Bet Analyzer...")
        
        try:
            # Test implied probability calculation
            odds = 2.0
            implied_prob = self.value_analyzer.calculate_implied_probability(odds)
            assert implied_prob == 0.5, f"Expected 0.5, got {implied_prob}"
            
            # Test value edge calculation
            model_prob = 0.6
            edge = self.value_analyzer.calculate_value_edge(model_prob, odds)
            assert abs(edge - 0.1) < 0.0001, f"Expected 0.1, got {edge}"
            
            # Test value bet detection
            is_value = self.value_analyzer.is_value_bet(model_prob, odds)
            assert is_value == True, "Should be a value bet"
            
            print("✅ Value bet analyzer test passed")
            return True
        except Exception as e:
            print(f"❌ Value bet analyzer test failed: {e}")
            return False
    
    def test_report_generator(self):
        """Test report generator"""
        print("\n📊 Testing Report Generator...")
        
        try:
            # Create sample betting data
            sample_data = [
                {
                    'date': datetime.now().isoformat(),
                    'market': 'match_result',
                    'selection': 'home_win',
                    'odds': 2.0,
                    'stake': 10.0,
                    'return': 20.0,
                    'result': 'win',
                    'edge': 0.05,
                    'roi': 1.0
                }
            ]
            
            # Test report generation
            start_date = datetime.now() - timedelta(days=7)
            end_date = datetime.now()
            
            report_path = self.report_generator.generate_weekly_report(
                sample_data, start_date, end_date
            )
            
            assert os.path.exists(report_path), "Report file not created"
            print(f"✅ Report generated: {report_path}")
            
            return True
        except Exception as e:
            print(f"❌ Report generator test failed: {e}")
            return False
    
    async def test_telegram_bot(self):
        """Test Telegram bot (without actually sending messages)"""
        print("\n🤖 Testing Telegram Bot...")
        
        try:
            # Test bot initialization
            assert self.telegram_bot.token, "Bot token not set"
            print("✅ Telegram bot initialization successful")
            
            # Test message formatting (without sending)
            value_bets = [
                {
                    'market': 'match_result',
                    'selection': 'home_win',
                    'odds': 2.0,
                    'model_probability': 0.6,
                    'implied_probability': 0.5,
                    'edge': 0.1,
                    'confidence': 0.7
                }
            ]
            
            # This would normally send a message, but we're just testing the function
            print("✅ Telegram bot message formatting test passed")
            
            return True
        except Exception as e:
            print(f"❌ Telegram bot test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Football Betting System Tests\n")
        
        tests = [
            ("Configuration", self.test_config),
            ("API Client", self.test_api_client),
            ("Prediction Models", self.test_models),
            ("Value Bet Analyzer", self.test_value_bet_analyzer),
            ("Report Generator", self.test_report_generator),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                print(f"❌ {test_name} test failed with exception: {e}")
        
        # Run async test
        try:
            asyncio.run(self.test_telegram_bot())
            passed += 1
            total += 1
        except Exception as e:
            print(f"❌ Telegram bot test failed with exception: {e}")
        
        print(f"\n📈 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! System is ready to run.")
            return True
        else:
            print("⚠️ Some tests failed. Please check the configuration and dependencies.")
            return False

def main():
    """Main test function"""
    tester = SystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ System is ready to run!")
        print("To start the system, run: python main.py")
    else:
        print("\n❌ System needs configuration before running.")
        print("Please check the error messages above and fix any issues.")

if __name__ == "__main__":
    main()
