#!/usr/bin/env python3
"""
Goal Prediction Model for FIXORA PRO
Poisson-based model for predicting match goals and outcomes
"""

import numpy as np
import sqlite3
import logging
from typing import Dict, List, Optional, Tuple
from scipy.stats import poisson
import config

logger = logging.getLogger(__name__)

class GoalModel:
    """
    Poisson-based goal prediction model
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_FILE
        self.init_database()
    
    def init_database(self):
        """Initialize the database with model predictions table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create model predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fixture_id INTEGER NOT NULL,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    league_name TEXT NOT NULL,
                    match_date TEXT NOT NULL,
                    lambda_home REAL NOT NULL,
                    lambda_away REAL NOT NULL,
                    lambda_total REAL NOT NULL,
                    home_win_prob REAL NOT NULL,
                    draw_prob REAL NOT NULL,
                    away_win_prob REAL NOT NULL,
                    over_05_prob REAL NOT NULL,
                    under_05_prob REAL NOT NULL,
                    over_15_prob REAL NOT NULL,
                    under_15_prob REAL NOT NULL,
                    over_25_prob REAL NOT NULL,
                    under_25_prob REAL NOT NULL,
                    btts_prob REAL NOT NULL,
                    no_btts_prob REAL NOT NULL,
                    home_clean_sheet_prob REAL NOT NULL,
                    away_clean_sheet_prob REAL NOT NULL,
                    model_confidence REAL NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Goal model database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize goal model database: {e}")
    
    def calculate_team_strength(self, team_stats: List[Dict], team_name: str, is_home: bool = True) -> float:
        """
        Calculate team strength based on historical performance
        
        Args:
            team_stats: List of historical match statistics
            team_name: Name of the team
            is_home: Whether calculating home or away strength
            
        Returns:
            float: Team strength score
        """
        if not team_stats:
            return 1.0  # Default neutral strength
        
        # Filter stats for the specific team
        team_matches = [stat for stat in team_stats if 
                       (is_home and stat['home_team'] == team_name) or
                       (not is_home and stat['away_team'] == team_name)]
        
        if not team_matches:
            return 1.0
        
        # Calculate average goals scored
        goals_scored = []
        for match in team_matches:
            if is_home:
                goals_scored.append(match['home_goals'])
            else:
                goals_scored.append(match['away_goals'])
        
        avg_goals = np.mean(goals_scored) if goals_scored else 1.0
        
        # Calculate average goals conceded
        goals_conceded = []
        for match in team_matches:
            if is_home:
                goals_conceded.append(match['away_goals'])
            else:
                goals_conceded.append(match['home_goals'])
        
        avg_conceded = np.mean(goals_conceded) if goals_conceded else 1.0
        
        # Calculate possession and pass accuracy factors
        possession_factor = 1.0
        pass_factor = 1.0
        
        if team_matches:
            possessions = []
            pass_accuracies = []
            
            for match in team_matches:
                if is_home:
                    possessions.append(match.get('home_possession', 50.0))
                    pass_accuracies.append(match.get('home_pass_accuracy', 80.0))
                else:
                    possessions.append(match.get('away_possession', 50.0))
                    pass_accuracies.append(match.get('away_pass_accuracy', 80.0))
            
            if possessions:
                avg_possession = np.mean(possessions)
                possession_factor = 1.0 + (avg_possession - 50.0) / 100.0
            
            if pass_accuracies:
                avg_pass = np.mean(pass_accuracies)
                pass_factor = 1.0 + (avg_pass - 80.0) / 100.0
        
        # Calculate final strength
        attack_strength = avg_goals * possession_factor * pass_factor
        defense_strength = 1.0 / (avg_conceded * 0.8)  # Lower is better for defense
        
        # Home advantage factor
        home_advantage = 1.1 if is_home else 0.95
        
        return (attack_strength + defense_strength) * home_advantage
    
    def fit_predict(self, fixture_data: Dict, historical_stats: List[Dict]) -> Dict:
        """
        Fit the model and generate predictions for a fixture
        
        Args:
            fixture_data: Fixture information
            historical_stats: Historical match statistics
            
        Returns:
            Dict: Model predictions
        """
        try:
            home_team = fixture_data['home_team']
            away_team = fixture_data['away_team']
            
            # Calculate team strengths
            home_strength = self.calculate_team_strength(historical_stats, home_team, is_home=True)
            away_strength = self.calculate_team_strength(historical_stats, away_team, is_home=False)
            
            # Base goal expectations (league average)
            base_home_goals = 1.5
            base_away_goals = 1.2
            
            # Calculate lambda values (expected goals)
            lambda_home = base_home_goals * home_strength
            lambda_away = base_away_goals * away_strength
            lambda_total = lambda_home + lambda_away
            
            # Calculate match outcome probabilities
            home_win_prob = self._calculate_win_probability(lambda_home, lambda_away, 'home')
            away_win_prob = self._calculate_win_probability(lambda_home, lambda_away, 'away')
            draw_prob = 1.0 - home_win_prob - away_win_prob
            
            # Calculate over/under probabilities
            over_05_prob = self._calculate_over_probability(lambda_total, 0.5)
            under_05_prob = 1.0 - over_05_prob
            over_15_prob = self._calculate_over_probability(lambda_total, 1.5)
            under_15_prob = 1.0 - over_15_prob
            over_25_prob = self._calculate_over_probability(lambda_total, 2.5)
            under_25_prob = 1.0 - over_25_prob
            
            # Calculate both teams to score probabilities
            btts_prob = self._calculate_btts_probability(lambda_home, lambda_away)
            no_btts_prob = 1.0 - btts_prob
            
            # Calculate clean sheet probabilities
            home_clean_sheet_prob = poisson.pmf(0, lambda_away)
            away_clean_sheet_prob = poisson.pmf(0, lambda_home)
            
            # Calculate model confidence based on data quality
            model_confidence = self._calculate_model_confidence(historical_stats, home_team, away_team)
            
            predictions = {
                'fixture_id': fixture_data['fixture_id'],
                'home_team': home_team,
                'away_team': away_team,
                'league_name': fixture_data['league_name'],
                'match_date': fixture_data['match_date'],
                'lambda_home': lambda_home,
                'lambda_away': lambda_away,
                'lambda_total': lambda_total,
                'home_win_prob': home_win_prob,
                'draw_prob': draw_prob,
                'away_win_prob': away_win_prob,
                'over_05_prob': over_05_prob,
                'under_05_prob': under_05_prob,
                'over_15_prob': over_15_prob,
                'under_15_prob': under_15_prob,
                'over_25_prob': over_25_prob,
                'under_25_prob': under_25_prob,
                'btts_prob': btts_prob,
                'no_btts_prob': no_btts_prob,
                'home_clean_sheet_prob': home_clean_sheet_prob,
                'away_clean_sheet_prob': away_clean_sheet_prob,
                'model_confidence': model_confidence
            }
            
            # Store predictions in database
            self._store_predictions(predictions)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to fit and predict: {e}")
            return {}
    
    def _calculate_win_probability(self, lambda_home: float, lambda_away: float, winner: str) -> float:
        """Calculate probability of a specific team winning"""
        if winner == 'home':
            # Home wins if home scores more goals than away
            prob = 0.0
            for home_goals in range(0, 10):  # Limit to reasonable range
                home_prob = poisson.pmf(home_goals, lambda_home)
                away_prob = poisson.cdf(home_goals - 1, lambda_away)
                prob += home_prob * away_prob
            return prob
        elif winner == 'away':
            # Away wins if away scores more goals than home
            prob = 0.0
            for away_goals in range(0, 10):  # Limit to reasonable range
                away_prob = poisson.pmf(away_goals, lambda_away)
                home_prob = poisson.cdf(away_goals - 1, lambda_home)
                prob += away_prob * home_prob
            return prob
        else:
            return 0.0
    
    def _calculate_over_probability(self, lambda_total: float, threshold: float) -> float:
        """Calculate probability of total goals exceeding threshold"""
        return 1.0 - poisson.cdf(threshold, lambda_total)
    
    def _calculate_btts_probability(self, lambda_home: float, lambda_away: float) -> float:
        """Calculate probability of both teams scoring"""
        home_scores = 1.0 - poisson.pmf(0, lambda_home)
        away_scores = 1.0 - poisson.pmf(0, lambda_away)
        return home_scores * away_scores
    
    def _calculate_model_confidence(self, historical_stats: List[Dict], home_team: str, away_team: str) -> float:
        """Calculate model confidence based on data quality"""
        # Count matches for each team
        home_matches = len([stat for stat in historical_stats if 
                           stat['home_team'] == home_team or stat['away_team'] == home_team])
        away_matches = len([stat for stat in historical_stats if 
                           stat['home_team'] == away_team or stat['away_team'] == away_team])
        
        # More matches = higher confidence
        min_matches = min(home_matches, away_matches)
        if min_matches >= 10:
            return 0.9
        elif min_matches >= 5:
            return 0.7
        elif min_matches >= 2:
            return 0.5
        else:
            return 0.3
    
    def _store_predictions(self, predictions: Dict) -> bool:
        """Store model predictions in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO model_predictions (
                    fixture_id, home_team, away_team, league_name, match_date,
                    lambda_home, lambda_away, lambda_total, home_win_prob, draw_prob,
                    away_win_prob, over_05_prob, under_05_prob, over_15_prob, under_15_prob,
                    over_25_prob, under_25_prob, btts_prob, no_btts_prob,
                    home_clean_sheet_prob, away_clean_sheet_prob, model_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                predictions['fixture_id'], predictions['home_team'], predictions['away_team'],
                predictions['league_name'], predictions['match_date'], predictions['lambda_home'],
                predictions['lambda_away'], predictions['lambda_total'], predictions['home_win_prob'],
                predictions['draw_prob'], predictions['away_win_prob'], predictions['over_05_prob'],
                predictions['under_05_prob'], predictions['over_15_prob'], predictions['under_15_prob'],
                predictions['over_25_prob'], predictions['under_25_prob'], predictions['btts_prob'],
                predictions['no_btts_prob'], predictions['home_clean_sheet_prob'],
                predictions['away_clean_sheet_prob'], predictions['model_confidence']
            ))
            
            conn.commit()
            conn.close()
            logger.info(f"Stored predictions for fixture {predictions['fixture_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store predictions: {e}")
            return False
    
    def get_predictions(self, fixture_id: int = None) -> List[Dict]:
        """Retrieve stored predictions from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if fixture_id:
                cursor.execute('SELECT * FROM model_predictions WHERE fixture_id = ?', (fixture_id,))
            else:
                cursor.execute('SELECT * FROM model_predictions ORDER BY created_at DESC LIMIT 100')
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            predictions = [dict(zip(columns, row)) for row in rows]
            conn.close()
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to retrieve predictions: {e}")
            return []

def fit_predict():
    """Convenience function for the pipeline"""
    from etl.ingest import DataIngestion
    
    # Load sample data
    ingestion = DataIngestion()
    sample_data = ingestion.load_sample_data()
    
    # Clean and store data
    if not ingestion.clean_and_store(sample_data):
        logger.error("Failed to clean and store data")
        return False
    
    # Generate predictions
    model = GoalModel()
    fixture = sample_data['fixtures'][0]
    
    predictions = model.fit_predict(fixture, sample_data['match_stats'])
    
    if predictions:
        logger.info(f"Successfully generated predictions for {fixture['home_team']} vs {fixture['away_team']}")
        return True
    else:
        logger.error("Failed to generate predictions")
        return False
