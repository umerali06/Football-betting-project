import numpy as np
from typing import Dict, List, Tuple, Optional
import config

class ValueBetAnalyzer:
    """
    Analyzes betting odds to find value bets based on model predictions
    """
    
    def __init__(self, threshold: float = None):
        self.threshold = threshold or config.VALUE_BET_THRESHOLD
        self.min_odds = config.MIN_ODDS
        self.max_odds = config.MAX_ODDS
        self.confidence_threshold = config.CONFIDENCE_THRESHOLD
        self.market_thresholds = {
            'match_result': config.MATCH_RESULT_THRESHOLD,
            'both_teams_to_score': config.BTTS_THRESHOLD,
            'over_under_goals': config.OVER_UNDER_THRESHOLD,
            'corners': config.CORNERS_THRESHOLD
        }
    
    def calculate_implied_probability(self, odds: float) -> float:
        """Convert decimal odds to implied probability"""
        if odds <= 1.0:
            return 0.0
        return 1.0 / odds
    
    def calculate_value_edge(self, model_probability: float, odds: float) -> float:
        """Calculate the value edge (difference between model and implied probability)"""
        implied_prob = self.calculate_implied_probability(odds)
        return model_probability - implied_prob
    
    def is_value_bet(self, model_probability: float, odds: float, market_type: str = 'match_result', confidence: float = 0.7) -> bool:
        """Check if a bet offers value with advanced criteria"""
        edge = self.calculate_value_edge(model_probability, odds)
        
        # Get market-specific threshold
        market_threshold = self.market_thresholds.get(market_type, self.threshold)
        
        # Advanced value bet criteria
        basic_criteria = (edge >= market_threshold and 
                         self.min_odds <= odds <= self.max_odds)
        
        # Confidence criteria
        confidence_criteria = confidence >= self.confidence_threshold
        
        # Kelly Criterion check
        kelly_criteria = self._check_kelly_criterion(model_probability, odds)
        
        return basic_criteria and confidence_criteria and kelly_criteria
    
    def _check_kelly_criterion(self, model_probability: float, odds: float) -> bool:
        """Check if bet meets Kelly Criterion"""
        implied_probability = 1.0 / odds
        edge = model_probability - implied_probability
        
        if edge <= 0:
            return False
        
        # Kelly Criterion: f = (bp - q) / b
        b = odds - 1
        p = model_probability
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b
        
        # Must be positive Kelly fraction
        return kelly_fraction > 0
    
    def analyze_match_result_bets(self, predictions: Dict, odds: Dict) -> List[Dict]:
        """
        Analyze match result (H2H) bets for value
        
        Args:
            predictions: Model predictions (home_win, draw, away_win)
            odds: Available odds for each outcome
            
        Returns:
            List of value bets found
        """
        value_bets = []
        
        # Home win
        if 'home_win' in odds and 'home_win' in predictions:
            home_odds = odds['home_win']
            home_prob = predictions['home_win']
            
            if self.is_value_bet(home_prob, home_odds):
                value_bets.append({
                    'market': 'match_result',
                    'selection': 'home_win',
                    'odds': home_odds,
                    'model_probability': home_prob,
                    'implied_probability': self.calculate_implied_probability(home_odds),
                    'edge': self.calculate_value_edge(home_prob, home_odds),
                    'confidence': self._calculate_confidence(home_prob, home_odds)
                })
        
        # Draw
        if 'draw' in odds and 'draw' in predictions:
            draw_odds = odds['draw']
            draw_prob = predictions['draw']
            
            if self.is_value_bet(draw_prob, draw_odds):
                value_bets.append({
                    'market': 'match_result',
                    'selection': 'draw',
                    'odds': draw_odds,
                    'model_probability': draw_prob,
                    'implied_probability': self.calculate_implied_probability(draw_odds),
                    'edge': self.calculate_value_edge(draw_prob, draw_odds),
                    'confidence': self._calculate_confidence(draw_prob, draw_odds)
                })
        
        # Away win
        if 'away_win' in odds and 'away_win' in predictions:
            away_odds = odds['away_win']
            away_prob = predictions['away_win']
            
            if self.is_value_bet(away_prob, away_odds):
                value_bets.append({
                    'market': 'match_result',
                    'selection': 'away_win',
                    'odds': away_odds,
                    'model_probability': away_prob,
                    'implied_probability': self.calculate_implied_probability(away_odds),
                    'edge': self.calculate_value_edge(away_prob, away_odds),
                    'confidence': self._calculate_confidence(away_prob, away_odds)
                })
        
        return value_bets
    
    def analyze_goals_bets(self, predictions: Dict, odds: Dict) -> List[Dict]:
        """
        Analyze goals-related bets (BTTS, Over/Under) for value
        
        Args:
            predictions: Model predictions for goals markets
            odds: Available odds for goals markets
            
        Returns:
            List of value bets found
        """
        value_bets = []
        
        # Both Teams to Score
        if 'btts_yes' in odds and 'btts' in predictions:
            btts_odds = odds['btts_yes']
            btts_prob = predictions['btts']
            
            if self.is_value_bet(btts_prob, btts_odds):
                value_bets.append({
                    'market': 'both_teams_to_score',
                    'selection': 'yes',
                    'odds': btts_odds,
                    'model_probability': btts_prob,
                    'implied_probability': self.calculate_implied_probability(btts_odds),
                    'edge': self.calculate_value_edge(btts_prob, btts_odds),
                    'confidence': self._calculate_confidence(btts_prob, btts_odds)
                })
        
        # Over/Under Goals
        for over_line in ['05', '15', '25']:
            over_key = f'over_{over_line}'
            under_key = f'under_{over_line}'
            
            if over_key in odds and over_key in predictions:
                over_odds = odds[over_key]
                over_prob = predictions[over_key]
                
                if self.is_value_bet(over_prob, over_odds):
                    value_bets.append({
                        'market': f'over_under_{over_line}_goals',
                        'selection': f'over_{over_line}',
                        'odds': over_odds,
                        'model_probability': over_prob,
                        'implied_probability': self.calculate_implied_probability(over_odds),
                        'edge': self.calculate_value_edge(over_prob, over_odds),
                        'confidence': self._calculate_confidence(over_prob, over_odds)
                    })
            
            if under_key in odds and over_key in predictions:
                under_odds = odds[under_key]
                under_prob = 1 - predictions[over_key]  # Under is opposite of over
                
                if self.is_value_bet(under_prob, under_odds):
                    value_bets.append({
                        'market': f'over_under_{over_line}_goals',
                        'selection': f'under_{over_line}',
                        'odds': under_odds,
                        'model_probability': under_prob,
                        'implied_probability': self.calculate_implied_probability(under_odds),
                        'edge': self.calculate_value_edge(under_prob, under_odds),
                        'confidence': self._calculate_confidence(under_prob, under_odds)
                    })
        
        return value_bets
    
    def analyze_corners_bets(self, predictions: Dict, odds: Dict) -> List[Dict]:
        """
        Analyze corners bets for value
        
        Args:
            predictions: Model predictions for corners markets
            odds: Available odds for corners markets
            
        Returns:
            List of value bets found
        """
        value_bets = []
        
        # Over/Under Corners
        for over_line in ['85', '95', '105']:
            over_key = f'over_{over_line}'
            under_key = f'under_{over_line}'
            
            if over_key in odds and over_key in predictions:
                over_odds = odds[over_key]
                over_prob = predictions[over_key]
                
                if self.is_value_bet(over_prob, over_odds):
                    value_bets.append({
                        'market': f'over_under_{over_line}_corners',
                        'selection': f'over_{over_line}',
                        'odds': over_odds,
                        'model_probability': over_prob,
                        'implied_probability': self.calculate_implied_probability(over_odds),
                        'edge': self.calculate_value_edge(over_prob, over_odds),
                        'confidence': self._calculate_confidence(over_prob, over_odds)
                    })
            
            if under_key in odds and over_key in predictions:
                under_odds = odds[under_key]
                under_prob = 1 - predictions[over_key]
                
                if self.is_value_bet(under_prob, under_odds):
                    value_bets.append({
                        'market': f'over_under_{over_line}_corners',
                        'selection': f'under_{over_line}',
                        'odds': under_odds,
                        'model_probability': under_prob,
                        'implied_probability': self.calculate_implied_probability(under_odds),
                        'edge': self.calculate_value_edge(under_prob, under_odds),
                        'confidence': self._calculate_confidence(under_prob, under_odds)
                    })
        
        # Team Corners
        for team in ['home', 'away']:
            over_key = f'{team}_over_45'
            under_key = f'{team}_under_45'
            
            if over_key in odds and over_key in predictions:
                over_odds = odds[over_key]
                over_prob = predictions[over_key]
                
                if self.is_value_bet(over_prob, over_odds):
                    value_bets.append({
                        'market': f'{team}_team_corners',
                        'selection': f'{team}_over_45',
                        'odds': over_odds,
                        'model_probability': over_prob,
                        'implied_probability': self.calculate_implied_probability(over_odds),
                        'edge': self.calculate_value_edge(over_prob, over_odds),
                        'confidence': self._calculate_confidence(over_prob, over_odds)
                    })
            
            if under_key in odds and over_key in predictions:
                under_odds = odds[under_key]
                under_prob = 1 - predictions[over_key]
                
                if self.is_value_bet(under_prob, under_odds):
                    value_bets.append({
                        'market': f'{team}_team_corners',
                        'selection': f'{team}_under_45',
                        'odds': under_odds,
                        'model_probability': under_prob,
                        'implied_probability': self.calculate_implied_probability(under_odds),
                        'edge': self.calculate_value_edge(under_prob, under_odds),
                        'confidence': self._calculate_confidence(under_prob, under_odds)
                    })
        
        return value_bets
    
    def _calculate_confidence(self, model_prob: float, odds: float) -> float:
        """Calculate confidence level for a bet (0-1 scale)"""
        edge = self.calculate_value_edge(model_prob, odds)
        # Higher edge = higher confidence, but cap at 0.95
        confidence = min(0.95, 0.5 + edge * 2)
        return confidence
    
    def sort_value_bets(self, value_bets: List[Dict]) -> List[Dict]:
        """Sort value bets by edge (highest first)"""
        return sorted(value_bets, key=lambda x: x['edge'], reverse=True)
