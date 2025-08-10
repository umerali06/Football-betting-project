import numpy as np
import pandas as pd
from typing import Dict, Tuple, List
import config

class XGModel:
    """
    Expected Goals (xG) model for football predictions
    """
    
    def __init__(self):
        self.team_xg_stats = {}  # Store team xG statistics
        self.league_averages = {}  # Store league average xG
        
    def calculate_team_xg(self, team_id: int, recent_matches: List[Dict]) -> Dict:
        """
        Calculate team's expected goals based on recent performance
        
        Args:
            team_id: Team ID
            recent_matches: List of recent match data
            
        Returns:
            Dictionary with xG statistics
        """
        if not recent_matches:
            return {'xg_for': 1.0, 'xg_against': 1.0, 'form_weight': 0.5}
        
        # Calculate xG for and against
        xg_for = []
        xg_against = []
        
        for match in recent_matches:
            # Check if this team is home or away in the match
            home_team_id = match.get('teams', {}).get('home', {}).get('id')
            away_team_id = match.get('teams', {}).get('away', {}).get('id')
            
            if home_team_id == team_id or away_team_id == team_id:
                # Use goals as proxy for xG if not available
                home_goals = match.get('goals', {}).get('home', 1)
                away_goals = match.get('goals', {}).get('away', 1)
                
                if home_team_id == team_id:
                    xg_for.append(match.get('xg_for', home_goals))
                    xg_against.append(match.get('xg_against', away_goals))
                else:
                    xg_for.append(match.get('xg_for', away_goals))
                    xg_against.append(match.get('xg_against', home_goals))
        
        # Calculate averages with recent form weighting
        if xg_for:
            recent_xg_for = np.mean(xg_for[-5:]) if len(xg_for) >= 5 else np.mean(xg_for)
            overall_xg_for = np.mean(xg_for)
            xg_for_final = 0.7 * recent_xg_for + 0.3 * overall_xg_for
        else:
            xg_for_final = 1.0
            
        if xg_against:
            recent_xg_against = np.mean(xg_against[-5:]) if len(xg_against) >= 5 else np.mean(xg_against)
            overall_xg_against = np.mean(xg_against)
            xg_against_final = 0.7 * recent_xg_against + 0.3 * overall_xg_against
        else:
            xg_against_final = 1.0
        
        # Calculate form weight based on recent performance
        form_weight = min(1.0, len(recent_matches) / 10.0)
        
        return {
            'xg_for': xg_for_final,
            'xg_against': xg_against_final,
            'form_weight': form_weight
        }
    
    def predict_match_xg(self, home_team_id: int, away_team_id: int,
                        home_stats: Dict, away_stats: Dict) -> Tuple[float, float]:
        """
        Predict expected goals for home and away teams
        
        Returns:
            Tuple of (home_xg, away_xg)
        """
        home_xg = home_stats['xg_for']
        home_defense = home_stats['xg_against']
        away_xg = away_stats['xg_for']
        away_defense = away_stats['xg_against']
        
        # Home advantage factor (typically 0.2-0.3 xG boost)
        home_advantage = 0.25
        
        # Calculate predicted xG
        predicted_home_xg = (home_xg + away_defense) / 2 + home_advantage
        predicted_away_xg = (away_xg + home_defense) / 2
        
        # Apply form weighting
        home_form = home_stats['form_weight']
        away_form = away_stats['form_weight']
        
        predicted_home_xg = predicted_home_xg * (0.8 + 0.4 * home_form)
        predicted_away_xg = predicted_away_xg * (0.8 + 0.4 * away_form)
        
        return predicted_home_xg, predicted_away_xg
    
    def predict_goals_probabilities(self, home_xg: float, away_xg: float) -> Dict:
        """
        Calculate probability distributions for different goal outcomes
        
        Returns:
            Dictionary with various goal probability predictions
        """
        total_xg = home_xg + away_xg
        
        # Over/Under probabilities
        over_05_prob = 1 - np.exp(-total_xg)
        over_15_prob = 1 - (np.exp(-total_xg) + total_xg * np.exp(-total_xg))
        over_25_prob = 1 - (np.exp(-total_xg) + total_xg * np.exp(-total_xg) + 
                            (total_xg**2 / 2) * np.exp(-total_xg))
        
        # Under probabilities (complement of over)
        under_05_prob = 1 - over_05_prob
        under_15_prob = 1 - over_15_prob
        under_25_prob = 1 - over_25_prob
        
        # Both teams to score probability
        btts_prob = (1 - np.exp(-home_xg)) * (1 - np.exp(-away_xg))
        
        return {
            'over_05': over_05_prob,
            'over_15': over_15_prob,
            'over_25': over_25_prob,
            'under_05': under_05_prob,
            'under_15': under_15_prob,
            'under_25': under_25_prob,
            'btts': btts_prob,
            'total_xg': total_xg,
            'home_xg': home_xg,
            'away_xg': away_xg
        }
    
    def update_team_stats(self, team_id: int, match_data: Dict):
        """Update team xG statistics with new match data"""
        if team_id not in self.team_xg_stats:
            self.team_xg_stats[team_id] = []
        
        self.team_xg_stats[team_id].append(match_data)
        
        # Keep only last 20 matches
        if len(self.team_xg_stats[team_id]) > 20:
            self.team_xg_stats[team_id] = self.team_xg_stats[team_id][-20:]
