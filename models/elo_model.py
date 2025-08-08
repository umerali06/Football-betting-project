import numpy as np
import pandas as pd
from typing import Dict, Tuple
import config

class EloModel:
    """
    Elo rating system for football teams
    """
    
    def __init__(self, k_factor: int = None, initial_rating: int = None):
        self.k_factor = k_factor or config.ELO_K_FACTOR
        self.initial_rating = initial_rating or config.ELO_INITIAL_RATING
        self.team_ratings = {}
        
    def get_team_rating(self, team_id: int) -> float:
        """Get current Elo rating for a team"""
        return self.team_ratings.get(team_id, self.initial_rating)
    
    def update_ratings(self, home_team_id: int, away_team_id: int, 
                      home_score: int, away_score: int, home_advantage: float = 100):
        """
        Update Elo ratings based on match result
        
        Args:
            home_team_id: ID of home team
            away_team_id: ID of away team  
            home_score: Goals scored by home team
            away_score: Goals scored by away team
            home_advantage: Home field advantage in Elo points
        """
        home_rating = self.get_team_rating(home_team_id)
        away_rating = self.get_team_rating(away_team_id)
        
        # Add home advantage
        home_rating_adjusted = home_rating + home_advantage
        
        # Calculate expected scores
        expected_home = 1 / (1 + 10**((away_rating - home_rating_adjusted) / 400))
        expected_away = 1 - expected_home
        
        # Determine actual result
        if home_score > away_score:
            actual_home = 1.0
            actual_away = 0.0
        elif home_score < away_score:
            actual_home = 0.0
            actual_away = 1.0
        else:
            actual_home = 0.5
            actual_away = 0.5
        
        # Update ratings
        self.team_ratings[home_team_id] = home_rating + self.k_factor * (actual_home - expected_home)
        self.team_ratings[away_team_id] = away_rating + self.k_factor * (actual_away - expected_away)
    
    def predict_match_result(self, home_team_id: int, away_team_id: int, 
                           home_advantage: float = 100) -> Tuple[float, float, float]:
        """
        Predict match result probabilities (Home Win, Draw, Away Win)
        
        Returns:
            Tuple of (home_win_prob, draw_prob, away_win_prob)
        """
        home_rating = self.get_team_rating(home_team_id)
        away_rating = self.get_team_rating(away_team_id)
        
        # Add home advantage
        home_rating_adjusted = home_rating + home_advantage
        
        # Calculate win probabilities
        home_win_prob = 1 / (1 + 10**((away_rating - home_rating_adjusted) / 400))
        away_win_prob = 1 / (1 + 10**((home_rating_adjusted - away_rating) / 400))
        draw_prob = 1 - home_win_prob - away_win_prob
        
        # Ensure all probabilities are non-negative
        home_win_prob = max(0, home_win_prob)
        away_win_prob = max(0, away_win_prob)
        draw_prob = max(0, draw_prob)
        
        # Normalize to ensure probabilities sum to 1
        total = home_win_prob + draw_prob + away_win_prob
        if total > 0:
            home_win_prob /= total
            draw_prob /= total
            away_win_prob /= total
        else:
            # Fallback to equal probabilities if all are zero
            home_win_prob = draw_prob = away_win_prob = 1/3
        
        return home_win_prob, draw_prob, away_win_prob
    
    def get_team_strength(self, team_id: int) -> float:
        """Get normalized team strength (0-1 scale)"""
        rating = self.get_team_rating(team_id)
        # Normalize to 0-1 scale (assuming ratings range from 1000-2000)
        return (rating - 1000) / 1000
