import numpy as np
import pandas as pd
from typing import Dict, Tuple, List
import config

class CornersModel:
    """
    Corners prediction model for football matches
    """
    
    def __init__(self):
        self.team_corner_stats = {}  # Store team corner statistics
        self.league_averages = {}  # Store league average corners
        
    def calculate_team_corners(self, team_id: int, recent_matches: List[Dict]) -> Dict:
        """
        Calculate team's corner statistics based on recent performance
        
        Args:
            team_id: Team ID
            recent_matches: List of recent match data
            
        Returns:
            Dictionary with corner statistics
        """
        if not recent_matches:
            return {'corners_for': 5.0, 'corners_against': 5.0, 'form_weight': 0.5}
        
        # Calculate corners for and against
        corners_for = []
        corners_against = []
        
        for match in recent_matches:
            # Check if this team is home or away in the match
            home_team_id = match.get('teams', {}).get('home', {}).get('id')
            away_team_id = match.get('teams', {}).get('away', {}).get('id')
            
            if home_team_id == team_id or away_team_id == team_id:
                # Use default corner values if not available
                home_corners = match.get('corners_for', 5.0)
                away_corners = match.get('corners_against', 5.0)
                
                if home_team_id == team_id:
                    corners_for.append(home_corners)
                    corners_against.append(away_corners)
                else:
                    corners_for.append(away_corners)
                    corners_against.append(home_corners)
        
        # Calculate averages with recent form weighting
        if corners_for:
            recent_corners_for = np.mean(corners_for[-5:]) if len(corners_for) >= 5 else np.mean(corners_for)
            overall_corners_for = np.mean(corners_for)
            corners_for_final = 0.7 * recent_corners_for + 0.3 * overall_corners_for
        else:
            corners_for_final = 5.0
            
        if corners_against:
            recent_corners_against = np.mean(corners_against[-5:]) if len(corners_against) >= 5 else np.mean(corners_against)
            overall_corners_against = np.mean(corners_against)
            corners_against_final = 0.7 * recent_corners_against + 0.3 * overall_corners_against
        else:
            corners_against_final = 5.0
        
        # Calculate form weight based on recent performance
        form_weight = min(1.0, len(recent_matches) / 10.0)
        
        return {
            'corners_for': corners_for_final,
            'corners_against': corners_against_final,
            'form_weight': form_weight
        }
    
    def predict_match_corners(self, home_team_id: int, away_team_id: int,
                            home_stats: Dict, away_stats: Dict) -> Tuple[float, float]:
        """
        Predict expected corners for home and away teams
        
        Args:
            home_team_id: Home team ID
            away_team_id: Away team ID
            home_stats: Home team corner statistics
            away_stats: Away team corner statistics
            
        Returns:
            Tuple of (home_corners, away_corners)
        """
        home_corners = home_stats['corners_for']
        home_defense = home_stats['corners_against']
        away_corners = away_stats['corners_for']
        away_defense = away_stats['corners_against']
        
        # Home advantage factor for corners (typically 0.5-1.0 corner boost)
        home_advantage = 0.75
        
        # Calculate predicted corners
        predicted_home_corners = (home_corners + away_defense) / 2 + home_advantage
        predicted_away_corners = (away_corners + home_defense) / 2
        
        # Apply form weighting
        home_form = home_stats['form_weight']
        away_form = away_stats['form_weight']
        
        predicted_home_corners = predicted_home_corners * (0.8 + 0.4 * home_form)
        predicted_away_corners = predicted_away_corners * (0.8 + 0.4 * away_form)
        
        return predicted_home_corners, predicted_away_corners
    
    def predict_corners_probabilities(self, home_corners: float, away_corners: float) -> Dict:
        """
        Calculate probability distributions for different corner outcomes
        
        Args:
            home_corners: Predicted home team corners
            away_corners: Predicted away team corners
            
        Returns:
            Dictionary with various corner probability predictions
        """
        total_corners = home_corners + away_corners
        
        # Over/Under corner probabilities (using Poisson distribution)
        over_45_prob = 1 - self._poisson_cdf(total_corners, 4.5)
        over_55_prob = 1 - self._poisson_cdf(total_corners, 5.5)
        over_65_prob = 1 - self._poisson_cdf(total_corners, 6.5)
        over_75_prob = 1 - self._poisson_cdf(total_corners, 7.5)
        over_85_prob = 1 - self._poisson_cdf(total_corners, 8.5)
        over_95_prob = 1 - self._poisson_cdf(total_corners, 9.5)
        
        # Under probabilities (complement of over)
        under_45_prob = 1 - over_45_prob
        under_55_prob = 1 - over_55_prob
        under_65_prob = 1 - over_65_prob
        under_75_prob = 1 - over_75_prob
        under_85_prob = 1 - over_85_prob
        under_95_prob = 1 - over_95_prob
        
        # Team corner predictions
        home_over_45_prob = 1 - self._poisson_cdf(home_corners, 4.5)
        away_over_45_prob = 1 - self._poisson_cdf(away_corners, 4.5)
        
        return {
            'over_45': over_45_prob,
            'over_55': over_55_prob,
            'over_65': over_65_prob,
            'over_75': over_75_prob,
            'over_85': over_85_prob,
            'over_95': over_95_prob,
            'under_45': under_45_prob,
            'under_55': under_55_prob,
            'under_65': under_65_prob,
            'under_75': under_75_prob,
            'under_85': under_85_prob,
            'under_95': under_95_prob,
            'home_over_45': home_over_45_prob,
            'away_over_45': away_over_45_prob,
            'total_corners': total_corners,
            'home_corners': home_corners,
            'away_corners': away_corners
        }
    
    def _poisson_cdf(self, lambda_param: float, k: float) -> float:
        """Calculate Poisson CDF for given lambda and k"""
        if lambda_param <= 0:
            return 1.0 if k >= 0 else 0.0
        
        cdf = 0.0
        for i in range(int(k) + 1):
            cdf += (lambda_param ** i) * np.exp(-lambda_param) / np.math.factorial(i)
        return cdf
    
    def update_team_stats(self, team_id: int, match_data: Dict):
        """Update team corner statistics with new match data"""
        if team_id not in self.team_corner_stats:
            self.team_corner_stats[team_id] = []
        
        self.team_corner_stats[team_id].append(match_data)
        
        # Keep only last 20 matches
        if len(self.team_corner_stats[team_id]) > 20:
            self.team_corner_stats[team_id] = self.team_corner_stats[team_id][-20:]


