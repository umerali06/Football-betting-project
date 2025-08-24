#!/usr/bin/env python3
"""
Development Seeding Script for FIXORA PRO
Quickly populates database with test data for development and testing
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from betting.roi_tracker import ROITracker
from etl.ingest import DataIngestion
import config

def seed_roi_data():
    """Seed ROI tracking data with sample bets"""
    print("🌱 Seeding ROI tracking data...")
    
    roi_tracker = ROITracker()
    
    # Sample betting data: 6 won, 4 lost; total stake 100; total return 112
    sample_bets = [
        # Winning bets
        {
            'fixture_id': 1, 'league_id': 39, 'league_name': 'English Premier League',
            'home_team': 'Manchester City', 'away_team': 'Arsenal',
            'market_type': 'match_result', 'selection': 'home_win',
            'odds': 2.0, 'stake': 10.0, 'potential_return': 20.0,
            'bet_date': '2024-08-24', 'match_date': '2024-08-24',
            'result': 'won', 'actual_return': 20.0, 'profit_loss': 10.0,
            'roi_percentage': 100.0, 'status': 'won'
        },
        {
            'fixture_id': 2, 'league_id': 39, 'league_name': 'English Premier League',
            'home_team': 'Liverpool', 'away_team': 'Chelsea',
            'market_type': 'match_result', 'selection': 'away_win',
            'odds': 1.8, 'stake': 10.0, 'potential_return': 18.0,
            'bet_date': '2024-08-24', 'match_date': '2024-08-24',
            'result': 'won', 'actual_return': 18.0, 'profit_loss': 8.0,
            'roi_percentage': 80.0, 'status': 'won'
        },
        {
            'fixture_id': 3, 'league_id': 39, 'league_name': 'English Premier League',
            'home_team': 'Manchester United', 'away_team': 'Tottenham',
            'market_type': 'match_result', 'selection': 'draw',
            'odds': 3.5, 'stake': 10.0, 'potential_return': 35.0,
            'bet_date': '2024-08-24', 'match_date': '2024-08-24',
            'result': 'won', 'actual_return': 35.0, 'profit_loss': 25.0,
            'roi_percentage': 250.0, 'status': 'won'
        },
        {
            'fixture_id': 4, 'league_id': 39, 'league_name': 'English Premier League',
            'home_team': 'Newcastle', 'away_team': 'Aston Villa',
            'market_type': 'both_teams_to_score', 'selection': 'yes',
            'odds': 1.9, 'stake': 10.0, 'potential_return': 19.0,
            'bet_date': '2024-08-24', 'match_date': '2024-08-24',
            'result': 'won', 'actual_return': 19.0, 'profit_loss': 9.0,
            'roi_percentage': 90.0, 'status': 'won'
        },
        {
            'fixture_id': 5, 'league_id': 39, 'league_name': 'English Premier League',
            'home_team': 'Brighton', 'away_team': 'West Ham',
            'market_type': 'over_under_goals', 'selection': 'over_2.5',
            'odds': 2.1, 'stake': 10.0, 'potential_return': 21.0,
            'bet_date': '2024-08-24', 'match_date': '2024-08-24',
            'result': 'won', 'actual_return': 21.0, 'profit_loss': 11.0,
            'roi_percentage': 110.0, 'status': 'won'
        },
        {
            'fixture_id': 6, 'league_id': 39, 'league_name': 'English Premier League',
            'home_team': 'Crystal Palace', 'away_team': 'Brentford',
            'market_type': 'corners', 'selection': 'over_10.5',
            'odds': 1.85, 'stake': 10.0, 'potential_return': 18.5,
            'bet_date': '2024-08-24', 'match_date': '2024-08-24',
            'result': 'won', 'actual_return': 18.5, 'profit_loss': 8.5,
            'roi_percentage': 85.0, 'status': 'won'
        },
        # Losing bets
        {
            'fixture_id': 7, 'league_id': 39, 'league_name': 'English Premier League',
            'home_team': 'Fulham', 'away_team': 'Burnley',
            'market_type': 'match_result', 'selection': 'home_win',
            'odds': 1.5, 'stake': 10.0, 'potential_return': 15.0,
            'bet_date': '2024-08-24', 'match_date': '2024-08-24',
            'result': 'lost', 'actual_return': 0.0, 'profit_loss': -10.0,
            'roi_percentage': -100.0, 'status': 'lost'
        },
        {
            'fixture_id': 8, 'league_id': 39, 'league_name': 'English Premier League',
            'home_team': 'Wolves', 'away_team': 'Sheffield United',
            'market_type': 'both_teams_to_score', 'selection': 'no',
            'odds': 2.2, 'stake': 10.0, 'potential_return': 22.0,
            'bet_date': '2024-08-24', 'match_date': '2024-08-24',
            'result': 'lost', 'actual_return': 0.0, 'profit_loss': -10.0,
            'roi_percentage': -100.0, 'status': 'lost'
        },
        {
            'fixture_id': 9, 'league_id': 39, 'league_name': 'English Premier League',
            'home_team': 'Nottingham Forest', 'away_team': 'Luton',
            'market_type': 'over_under_goals', 'selection': 'under_2.5',
            'odds': 1.7, 'stake': 10.0, 'potential_return': 17.0,
            'bet_date': '2024-08-24', 'match_date': '2024-08-24',
            'result': 'lost', 'actual_return': 0.0, 'profit_loss': -10.0,
            'roi_percentage': -100.0, 'status': 'lost'
        },
        {
            'fixture_id': 10, 'league_id': 39, 'league_name': 'English Premier League',
            'home_team': 'Everton', 'away_team': 'Bournemouth',
            'market_type': 'corners', 'selection': 'under_10.5',
            'odds': 1.95, 'stake': 10.0, 'potential_return': 19.5,
            'bet_date': '2024-08-24', 'match_date': '2024-08-24',
            'result': 'lost', 'actual_return': 0.0, 'profit_loss': -10.0,
            'roi_percentage': -100.0, 'status': 'lost'
        }
    ]
    
    # Insert sample bets
    for bet in sample_bets:
        success, bet_id = roi_tracker.record_bet(bet)
        if success:
            print(f"  ✅ Added bet {bet_id}: {bet['home_team']} vs {bet['away_team']}")
        else:
            print(f"  ❌ Failed to add bet: {bet['home_team']} vs {bet['away_team']}")
    
    print(f"📊 Seeded {len(sample_bets)} betting records")
    
    # Verify data
    overall = roi_tracker.get_overall_performance()
    print(f"📈 Overall Performance:")
    print(f"  Total Bets: {overall['total_bets']}")
    print(f"  Winning Bets: {overall['winning_bets']}")
    print(f"  Win Rate: {overall['win_rate']:.1f}%")
    print(f"  Total Stake: ${overall['total_stake']:.2f}")
    print(f"  Total Return: ${overall['total_return']:.2f}")
    print(f"  Total P/L: ${overall['total_profit_loss']:.2f}")
    print(f"  Overall ROI: {overall['overall_roi']:.2f}%")

def seed_etl_data():
    """Seed ETL data with sample match statistics and odds"""
    print("🌱 Seeding ETL data...")
    
    ingestion = DataIngestion()
    
    # Load and store sample data
    success = ingestion.clean_and_store(ingestion.load_sample_data())
    
    if success:
        print("  ✅ ETL data seeded successfully")
        
        # Verify data
        etl_data = ingestion.get_cleaned_data()
        print(f"📊 ETL Data Summary:")
        print(f"  Match Stats: {len(etl_data.get('match_stats', []))}")
        print(f"  Odds Records: {len(etl_data.get('odds', []))}")
        print(f"  Fixtures: {len(etl_data.get('fixtures', []))}")
    else:
        print("  ❌ Failed to seed ETL data")

def main():
    """Main seeding function"""
    print("🚀 FIXORA PRO - Development Data Seeding")
    print("=" * 50)
    
    try:
        # Seed ROI data
        seed_roi_data()
        print()
        
        # Seed ETL data
        seed_etl_data()
        print()
        
        print("🎉 Seeding completed successfully!")
        print()
        print("📋 Next steps:")
        print("  1. Run tests: python run_tests.py")
        print("  2. Generate reports: python reports/roi_weekly_report.py")
        print("  3. Run pipeline: python pipeline/run_daily.py")
        
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
