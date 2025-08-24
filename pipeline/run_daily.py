#!/usr/bin/env python3
"""
Daily Pipeline Runner for FIXORA PRO
Orchestrates the complete data flow: ETL → Modelling → Value Engine → Reporting
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.ingest import DataIngestion
from models.goal_model import GoalModel
from betting.value_bet_analyzer import ValueBetAnalyzer
from utils.odds_filter import OddsFilter
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DailyPipeline:
    """
    Orchestrates the daily data processing pipeline
    """
    
    def __init__(self):
        self.ingestion = DataIngestion()
        self.model = GoalModel()
        self.value_analyzer = ValueBetAnalyzer()
    
    def run_etl(self) -> bool:
        """Run the ETL process"""
        try:
            logger.info("Starting ETL process...")
            
            # Load sample data (in production, this would be real API calls)
            sample_data = self.ingestion.load_sample_data()
            
            # Clean and store data
            success = self.ingestion.clean_and_store(sample_data)
            
            if success:
                logger.info("ETL process completed successfully")
                return True
            else:
                logger.error("ETL process failed")
                return False
                
        except Exception as e:
            logger.error(f"ETL process failed with error: {e}")
            return False
    
    def run_modelling(self) -> bool:
        """Run the modelling process"""
        try:
            logger.info("Starting modelling process...")
            
            # Get cleaned data
            cleaned_data = self.ingestion.get_cleaned_data()
            
            if not cleaned_data.get('fixtures'):
                logger.error("No fixtures found for modelling")
                return False
            
            # Generate predictions for each fixture
            success_count = 0
            total_fixtures = len(cleaned_data['fixtures'])
            
            for fixture in cleaned_data['fixtures']:
                try:
                    predictions = self.model.fit_predict(fixture, cleaned_data.get('match_stats', []))
                    if predictions:
                        success_count += 1
                        logger.info(f"Generated predictions for {fixture['home_team']} vs {fixture['away_team']}")
                    else:
                        logger.warning(f"Failed to generate predictions for {fixture['home_team']} vs {fixture['away_team']}")
                except Exception as e:
                    logger.error(f"Error generating predictions for fixture {fixture['fixture_id']}: {e}")
            
            success_rate = success_count / total_fixtures if total_fixtures > 0 else 0
            logger.info(f"Modelling process completed: {success_count}/{total_fixtures} fixtures processed successfully")
            
            return success_rate > 0.5  # Consider successful if >50% fixtures processed
            
        except Exception as e:
            logger.error(f"Modelling process failed with error: {e}")
            return False
    
    def run_value_engine(self) -> bool:
        """Run the value engine analysis"""
        try:
            logger.info("Starting value engine analysis...")
            
            # Get model predictions
            predictions = self.model.get_predictions()
            
            if not predictions:
                logger.warning("No model predictions found for value analysis")
                return False
            
            # Get cleaned odds data
            cleaned_data = self.ingestion.get_cleaned_data()
            odds_data = cleaned_data.get('odds', [])
            
            if not odds_data:
                logger.warning("No odds data found for value analysis")
                return False
            
            # Analyze value bets
            value_bets_found = 0
            
            for prediction in predictions:
                fixture_id = prediction['fixture_id']
                
                # Get odds for this fixture
                fixture_odds = [odd for odd in odds_data if odd['fixture_id'] == fixture_id]
                
                if not fixture_odds:
                    continue
                
                # Convert odds to the format expected by value analyzer
                odds_dict = {}
                for odd in fixture_odds:
                    if odd['market_type'] == 'match_result':
                        if odd['selection'] == 'home_win':
                            odds_dict['home_win'] = odd['odds']
                        elif odd['selection'] == 'draw':
                            odds_dict['draw'] = odd['odds']
                        elif odd['selection'] == 'away_win':
                            odds_dict['away_win'] = odd['odds']
                
                # Filter odds using centralized filter
                valid_odds = OddsFilter.filter_odds_dict(odds_dict)
                
                if not valid_odds:
                    logger.debug(f"No valid odds (≥{config.MIN_ODDS}) for fixture {fixture_id}")
                    continue
                
                # Check for value bets
                for outcome, odds in valid_odds.items():
                    if outcome == 'home_win':
                        prob = prediction['home_win_prob']
                    elif outcome == 'draw':
                        prob = prediction['draw_prob']
                    elif outcome == 'away_win':
                        prob = prediction['away_win_prob']
                    else:
                        continue
                    
                    # Check if this is a value bet
                    if self.value_analyzer.is_value_bet(prob, odds):
                        value_bets_found += 1
                        logger.info(f"Value bet found: {outcome} @ {odds:.2f} (model prob: {prob:.3f})")
            
            logger.info(f"Value engine analysis completed: {value_bets_found} value bets found")
            return True
            
        except Exception as e:
            logger.error(f"Value engine analysis failed with error: {e}")
            return False
    
    def run_pipeline(self) -> bool:
        """Run the complete daily pipeline"""
        try:
            logger.info("=" * 60)
            logger.info("Starting FIXORA PRO Daily Pipeline")
            logger.info("=" * 60)
            
            start_time = datetime.now()
            
            # Step 1: ETL
            logger.info("Step 1/4: ETL Process")
            if not self.run_etl():
                logger.error("Pipeline failed at ETL step")
                return False
            
            # Step 2: Modelling
            logger.info("Step 2/4: Modelling Process")
            if not self.run_modelling():
                logger.error("Pipeline failed at Modelling step")
                return False
            
            # Step 3: Value Engine
            logger.info("Step 3/4: Value Engine Analysis")
            if not self.run_value_engine():
                logger.error("Pipeline failed at Value Engine step")
                return False
            
            # Step 4: Reporting (placeholder for now)
            logger.info("Step 4/4: Reporting Process")
            logger.info("Reporting step completed (placeholder)")
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info("=" * 60)
            logger.info("Daily Pipeline Completed Successfully!")
            logger.info(f"Total Duration: {duration}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Pipeline failed with unexpected error: {e}")
            return False
    
    def get_pipeline_status(self) -> Dict:
        """Get the current status of the pipeline"""
        try:
            # Check ETL data
            etl_data = self.ingestion.get_cleaned_data()
            etl_status = {
                'match_stats_count': len(etl_data.get('match_stats', [])),
                'odds_count': len(etl_data.get('odds', [])),
                'fixtures_count': len(etl_data.get('fixtures', []))
            }
            
            # Check model predictions
            predictions = self.model.get_predictions()
            model_status = {
                'predictions_count': len(predictions),
                'latest_prediction': predictions[0] if predictions else None
            }
            
            # Check database tables
            import sqlite3
            conn = sqlite3.connect(config.DATABASE_FILE)
            cursor = conn.cursor()
            
            # Get table row counts
            tables = ['cleaned_match_data', 'cleaned_odds_data', 'cleaned_fixtures', 'model_predictions']
            table_counts = {}
            
            for table in tables:
                try:
                    cursor.execute(f'SELECT COUNT(*) FROM {table}')
                    count = cursor.fetchone()[0]
                    table_counts[table] = count
                except:
                    table_counts[table] = 0
            
            conn.close()
            
            return {
                'etl_status': etl_status,
                'model_status': model_status,
                'table_counts': table_counts,
                'last_run': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get pipeline status: {e}")
            return {'error': str(e)}

def main():
    """Main entry point for the pipeline"""
    pipeline = DailyPipeline()
    
    # Run the complete pipeline
    success = pipeline.run_pipeline()
    
    if success:
        # Get and display status
        status = pipeline.get_pipeline_status()
        logger.info("Pipeline Status:")
        logger.info(f"  ETL: {status['etl_status']['match_stats_count']} match stats, "
                   f"{status['etl_status']['odds_count']} odds, "
                   f"{status['etl_status']['fixtures_count']} fixtures")
        logger.info(f"  Model: {status['model_status']['predictions_count']} predictions")
        logger.info(f"  Database: {status['table_counts']}")
        
        print("\n🎉 Pipeline completed successfully!")
        print(f"📊 Generated {status['model_status']['predictions_count']} predictions")
        print(f"💾 Stored data in {len([k for k, v in status['table_counts'].items() if v > 0])} tables")
        
    else:
        print("\n❌ Pipeline failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
