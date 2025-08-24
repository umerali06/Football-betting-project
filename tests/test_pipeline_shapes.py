#!/usr/bin/env python3
"""
Test Pipeline Shapes for FIXORA PRO
Verifies that pipeline creates tables with expected columns and data flow
"""

import unittest
import sys
import os
import tempfile
import sqlite3

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.run_daily import DailyPipeline
from etl.ingest import DataIngestion
from models.goal_model import GoalModel
import config

class TestPipelineShapes(unittest.TestCase):
    """Test that pipeline creates correct table structures and data flow"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Override config to use temp database
        self.original_db = config.DATABASE_FILE
        config.DATABASE_FILE = self.temp_db.name
        
        # Initialize pipeline components
        self.pipeline = DailyPipeline()
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Restore original config
        config.DATABASE_FILE = self.original_db
        
        # Remove temp database
        os.unlink(self.temp_db.name)
    
    def test_etl_table_creation(self):
        """Test that ETL creates tables with expected structure"""
        # Run ETL process
        success = self.pipeline.run_etl()
        self.assertTrue(success, "ETL process should complete successfully")
        
        # Check that tables exist
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'cleaned_match_data',
            'cleaned_odds_data', 
            'cleaned_fixtures'
        ]
        
        for table in expected_tables:
            self.assertIn(table, tables, f"Table {table} should be created")
        
        conn.close()
    
    def test_etl_table_columns(self):
        """Test that ETL tables have expected columns"""
        # Run ETL process
        success = self.pipeline.run_etl()
        self.assertTrue(success, "ETL process should complete successfully")
        
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # Check cleaned_match_data columns
        cursor.execute("PRAGMA table_info(cleaned_match_data)")
        columns = [row[1] for row in cursor.fetchall()]
        
        expected_columns = [
            'id', 'fixture_id', 'league_id', 'league_name', 'home_team', 'away_team',
            'match_date', 'home_possession', 'away_possession', 'home_pass_accuracy',
            'away_pass_accuracy', 'home_crosses', 'away_crosses', 'home_clearances',
            'away_clearances', 'home_tackles', 'away_tackles', 'home_fouls',
            'away_fouls', 'home_long_balls', 'away_long_balls', 'home_aerials',
            'away_aerials', 'referee', 'weather', 'home_goals', 'away_goals',
            'home_shots', 'away_shots', 'home_shots_on_target', 'away_shots_on_target',
            'home_corners', 'away_corners', 'home_yellow_cards', 'away_yellow_cards',
            'home_red_cards', 'away_red_cards', 'created_at'
        ]
        
        for column in expected_columns:
            self.assertIn(column, columns, f"Column {column} should exist in cleaned_match_data")
        
        # Check cleaned_odds_data columns
        cursor.execute("PRAGMA table_info(cleaned_odds_data)")
        columns = [row[1] for row in cursor.fetchall()]
        
        expected_columns = [
            'id', 'fixture_id', 'market_type', 'selection', 'odds', 'bookmaker',
            'line_moves', 'last_updated'
        ]
        
        for column in expected_columns:
            self.assertIn(column, columns, f"Column {column} should exist in cleaned_odds_data")
        
        # Check cleaned_fixtures columns
        cursor.execute("PRAGMA table_info(cleaned_fixtures)")
        columns = [row[1] for row in cursor.fetchall()]
        
        expected_columns = [
            'id', 'fixture_id', 'league_id', 'league_name', 'home_team', 'away_team',
            'match_date', 'kickoff_time', 'venue', 'home_formation', 'away_formation',
            'home_starting_xi', 'away_starting_xi', 'home_substitutes', 'away_substitutes',
            'home_manager', 'away_manager', 'status', 'created_at'
        ]
        
        for column in expected_columns:
            self.assertIn(column, columns, f"Column {column} should exist in cleaned_fixtures")
        
        conn.close()
    
    def test_model_table_creation(self):
        """Test that modelling creates table with expected structure"""
        # Run ETL first
        success = self.pipeline.run_etl()
        self.assertTrue(success, "ETL process should complete successfully")
        
        # Run modelling
        success = self.pipeline.run_modelling()
        self.assertTrue(success, "Modelling process should complete successfully")
        
        # Check that model_predictions table exists
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='model_predictions'")
        table_exists = cursor.fetchone() is not None
        
        self.assertTrue(table_exists, "model_predictions table should be created")
        
        conn.close()
    
    def test_model_table_columns(self):
        """Test that model_predictions table has expected columns"""
        # Run ETL and modelling
        success = self.pipeline.run_etl()
        self.assertTrue(success, "ETL process should complete successfully")
        
        success = self.pipeline.run_modelling()
        self.assertTrue(success, "Modelling process should complete successfully")
        
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # Check model_predictions columns
        cursor.execute("PRAGMA table_info(model_predictions)")
        columns = [row[1] for row in cursor.fetchall()]
        
        expected_columns = [
            'id', 'fixture_id', 'home_team', 'away_team', 'league_name', 'match_date',
            'lambda_home', 'lambda_away', 'lambda_total', 'home_win_prob', 'draw_prob',
            'away_win_prob', 'over_05_prob', 'under_05_prob', 'over_15_prob',
            'under_15_prob', 'over_25_prob', 'under_25_prob', 'btts_prob',
            'no_btts_prob', 'home_clean_sheet_prob', 'away_clean_sheet_prob',
            'model_confidence', 'created_at'
        ]
        
        for column in expected_columns:
            self.assertIn(column, columns, f"Column {column} should exist in model_predictions")
        
        conn.close()
    
    def test_data_flow_etl_to_modelling(self):
        """Test that data flows correctly from ETL to modelling"""
        # Run ETL
        success = self.pipeline.run_etl()
        self.assertTrue(success, "ETL process should complete successfully")
        
        # Check data was stored
        etl_data = self.pipeline.ingestion.get_cleaned_data()
        
        self.assertGreater(len(etl_data.get('match_stats', [])), 0, "Match stats should be stored")
        self.assertGreater(len(etl_data.get('odds', [])), 0, "Odds should be stored")
        self.assertGreater(len(etl_data.get('fixtures', [])), 0, "Fixtures should be stored")
        
        # Run modelling
        success = self.pipeline.run_modelling()
        self.assertTrue(success, "Modelling process should complete successfully")
        
        # Check predictions were generated
        predictions = self.pipeline.model.get_predictions()
        self.assertGreater(len(predictions), 0, "Predictions should be generated")
        
        # Check that predictions reference stored fixtures
        fixture_ids = [fixture['fixture_id'] for fixture in etl_data['fixtures']]
        prediction_fixture_ids = [pred['fixture_id'] for pred in predictions]
        
        for pred_id in prediction_fixture_ids:
            self.assertIn(pred_id, fixture_ids, f"Prediction should reference stored fixture {pred_id}")
    
    def test_value_engine_integration(self):
        """Test that value engine integrates with ETL and modelling data"""
        # Run complete pipeline
        success = self.pipeline.run_pipeline()
        self.assertTrue(success, "Complete pipeline should run successfully")
        
        # Check that value engine can access data
        etl_data = self.pipeline.ingestion.get_cleaned_data()
        predictions = self.pipeline.model.get_predictions()
        
        self.assertGreater(len(etl_data.get('odds', [])), 0, "Odds data should be available")
        self.assertGreater(len(predictions), 0, "Predictions should be available")
        
        # Check that odds filtering works
        from utils.odds_filter import OddsFilter
        
        for odd in etl_data['odds']:
            odds_valid = OddsFilter.validate_odds(odd['odds'])
            # All sample odds should be valid (≥1.8)
            self.assertTrue(odds_valid, f"Sample odds {odd['odds']} should be valid")
    
    def test_pipeline_status_reporting(self):
        """Test that pipeline status reporting works correctly"""
        # Run pipeline
        success = self.pipeline.run_pipeline()
        self.assertTrue(success, "Pipeline should run successfully")
        
        # Get status
        status = self.pipeline.get_pipeline_status()
        
        # Check status structure
        self.assertIn('etl_status', status)
        self.assertIn('model_status', status)
        self.assertIn('table_counts', status)
        self.assertIn('last_run', status)
        
        # Check ETL status
        etl_status = status['etl_status']
        self.assertIn('match_stats_count', etl_status)
        self.assertIn('odds_count', etl_status)
        self.assertIn('fixtures_count', etl_status)
        
        # Check model status
        model_status = status['model_status']
        self.assertIn('predictions_count', model_status)
        
        # Check table counts
        table_counts = status['table_counts']
        expected_tables = ['cleaned_match_data', 'cleaned_odds_data', 'cleaned_fixtures', 'model_predictions']
        
        for table in expected_tables:
            self.assertIn(table, table_counts)
            self.assertGreaterEqual(table_counts[table], 0, f"Table {table} should have non-negative count")
    
    def test_sample_data_quality(self):
        """Test that sample data meets quality requirements"""
        # Load sample data
        sample_data = self.pipeline.ingestion.load_sample_data()
        
        # Check match stats
        match_stats = sample_data['match_stats']
        self.assertGreater(len(match_stats), 0, "Should have sample match stats")
        
        for stat in match_stats:
            # Check required fields
            required_fields = ['fixture_id', 'home_team', 'away_team', 'home_goals', 'away_goals']
            for field in required_fields:
                self.assertIn(field, stat, f"Match stat should have {field}")
            
            # Check data types
            self.assertIsInstance(stat['fixture_id'], int)
            self.assertIsInstance(stat['home_goals'], int)
            self.assertIsInstance(stat['away_goals'], int)
        
        # Check odds data
        odds = sample_data['odds']
        self.assertGreater(len(odds), 0, "Should have sample odds")
        
        for odd in odds:
            # Check required fields
            required_fields = ['fixture_id', 'market_type', 'selection', 'odds']
            for field in required_fields:
                self.assertIn(field, odd, f"Odds should have {field}")
            
            # Check odds are valid
            from utils.odds_filter import OddsFilter
            odds_valid = OddsFilter.validate_odds(odd['odds'])
            self.assertTrue(odds_valid, f"Sample odds {odd['odds']} should be valid")
        
        # Check fixtures
        fixtures = sample_data['fixtures']
        self.assertGreater(len(fixtures), 0, "Should have sample fixtures")
        
        for fixture in fixtures:
            # Check required fields
            required_fields = ['fixture_id', 'home_team', 'away_team', 'league_name']
            for field in required_fields:
                self.assertIn(field, fixture, f"Fixture should have {field}")

if __name__ == '__main__':
    unittest.main()
