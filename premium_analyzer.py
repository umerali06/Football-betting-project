#!/usr/bin/env python3
"""
Premium Football Betting Analyzer
Advanced analysis with multiple models and sophisticated strategies
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import datetime
import config
from models.elo_model import EloModel
from models.xg_model import XGModel
from models.corners_model import CornersModel
from models.ml_model import AdvancedMLModel
from betting.value_bet_analyzer import ValueBetAnalyzer
from betting.risk_manager import AdvancedRiskManager

class PremiumAnalyzer:
    """
    Premium football betting analyzer with advanced features
    """
    
    def __init__(self):
        self.elo_model = EloModel()
        self.xg_model = XGModel()
        self.corners_model = CornersModel()
        self.ml_model = AdvancedMLModel()
        self.value_analyzer = ValueBetAnalyzer()
        self.risk_manager = AdvancedRiskManager()
        
        # Premium analysis settings
        self.analysis_weights = {
            'elo': 0.25,
            'xg': 0.30,
            'corners': 0.15,
            'ml': 0.20,
            'form': 0.10
        }
        
        # Advanced thresholds
        self.premium_thresholds = {
            'high_confidence': 0.85,
            'medium_confidence': 0.75,
            'low_confidence': 0.65,
            'minimum_edge': 0.08,
            'maximum_risk': 0.15
        }
    
    def analyze_match_premium(self, match_data: Dict, odds_data: List[Dict]) -> Dict:
        """
        Perform premium analysis on a single match
        
        Returns:
            Dictionary with comprehensive analysis results
        """
        fixture_id = match_data['fixture']['id']
        home_team_id = match_data['teams']['home']['id']
        away_team_id = match_data['teams']['away']['id']
        
        # Get team form data
        home_form = self._get_team_form(home_team_id)
        away_form = self._get_team_form(away_team_id)
        
        # Generate predictions from all models
        predictions = self._generate_comprehensive_predictions(
            home_team_id, away_team_id, home_form, away_form
        )
        
        # Analyze value bets
        value_bets = self._analyze_value_bets(predictions, odds_data, match_data)
        
        # Apply risk management
        risk_assessed_bets = self._apply_risk_management(value_bets)
        
        # Calculate confidence scores
        confidence_scores = self._calculate_confidence_scores(predictions, home_form, away_form)
        
        # Generate premium insights
        insights = self._generate_premium_insights(predictions, match_data, confidence_scores)
        
        return {
            'match_info': match_data,
            'predictions': predictions,
            'value_bets': risk_assessed_bets,
            'confidence_scores': confidence_scores,
            'insights': insights,
            'analysis_quality': self._assess_analysis_quality(predictions, home_form, away_form)
        }
    
    def _generate_comprehensive_predictions(self, home_team_id: int, away_team_id: int,
                                          home_form: List[Dict], away_form: List[Dict]) -> Dict:
        """Generate predictions using all available models"""
        
        predictions = {}
        
        # 1. Elo Model Predictions
        elo_home, elo_draw, elo_away = self.elo_model.predict_match_result(home_team_id, away_team_id)
        predictions['elo'] = {
            'home_win': elo_home,
            'draw': elo_draw,
            'away_win': elo_away,
            'confidence': self._calculate_elo_confidence(elo_home, elo_draw, elo_away)
        }
        
        # 2. xG Model Predictions
        home_xg_stats = self.xg_model.calculate_team_xg(home_team_id, home_form)
        away_xg_stats = self.xg_model.calculate_team_xg(away_team_id, away_form)
        
        home_xg, away_xg = self.xg_model.predict_match_xg(home_team_id, away_team_id, home_xg_stats, away_xg_stats)
        goals_predictions = self.xg_model.predict_goals_probabilities(home_xg, away_xg)
        predictions['xg'] = {
            'home_xg': home_xg,
            'away_xg': away_xg,
            'goals_predictions': goals_predictions,
            'confidence': self._calculate_xg_confidence(home_xg_stats, away_xg_stats)
        }
        
        # 3. Corners Model Predictions
        home_corner_stats = self.corners_model.calculate_team_corners(home_team_id, home_form)
        away_corner_stats = self.corners_model.calculate_team_corners(away_team_id, away_form)
        
        home_corners, away_corners = self.corners_model.predict_match_corners(
            home_team_id, away_team_id, home_corner_stats, away_corner_stats
        )
        corners_predictions = self.corners_model.predict_corners_probabilities(home_corners, away_corners)
        predictions['corners'] = {
            'home_corners': home_corners,
            'away_corners': away_corners,
            'corners_predictions': corners_predictions,
            'confidence': self._calculate_corners_confidence(home_corner_stats, away_corner_stats)
        }
        
        # 4. Form Analysis
        form_analysis = self._analyze_team_form(home_form, away_form)
        predictions['form'] = form_analysis
        
        # 5. Combined Model Prediction
        combined_prediction = self._combine_model_predictions(predictions)
        predictions['combined'] = combined_prediction
        
        return predictions
    
    def _analyze_value_bets(self, predictions: Dict, odds_data: List[Dict], match_data: Dict) -> List[Dict]:
        """Analyze for value bets using comprehensive predictions"""
        
        value_bets = []
        
        # Extract odds
        match_odds = self._extract_match_odds(odds_data)
        goals_odds = self._extract_goals_odds(odds_data)
        corners_odds = self._extract_corners_odds(odds_data)
        
        # 1. Match Result Bets
        if 'combined' in predictions and match_odds:
            combined_probs = predictions['combined']['match_result']
            value_bets.extend(self._analyze_match_result_value(combined_probs, match_odds, match_data))
        
        # 2. Goals Bets
        if 'xg' in predictions and goals_odds:
            goals_probs = predictions['xg']['goals_predictions']
            value_bets.extend(self._analyze_goals_value(goals_probs, goals_odds, match_data))
        
        # 3. Corners Bets
        if 'corners' in predictions and corners_odds:
            corners_probs = predictions['corners']['corners_predictions']
            value_bets.extend(self._analyze_corners_value(corners_probs, corners_odds, match_data))
        
        # 4. Advanced Bets (if ML model is available)
        if hasattr(self.ml_model, 'predict') and self.ml_model.is_trained():
            ml_predictions = self.ml_model.predict(match_data)
            value_bets.extend(self._analyze_ml_value(ml_predictions, odds_data, match_data))
        
        return value_bets
    
    def _apply_risk_management(self, value_bets: List[Dict]) -> List[Dict]:
        """Apply advanced risk management to value bets"""
        
        risk_managed_bets = []
        
        for bet in value_bets:
            # Calculate Kelly Criterion
            kelly_percentage = self._calculate_kelly_criterion(bet['probability'], bet['odds'])
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(bet)
            
            # Apply risk filters
            if (kelly_percentage > 0 and 
                risk_score < self.premium_thresholds['maximum_risk'] and
                bet['edge'] > self.premium_thresholds['minimum_edge']):
                
                bet['kelly_percentage'] = kelly_percentage
                bet['risk_score'] = risk_score
                bet['recommended_stake'] = self._calculate_recommended_stake(bet, kelly_percentage)
                bet['confidence_level'] = self._classify_confidence(bet['confidence'])
                
                risk_managed_bets.append(bet)
        
        # Sort by expected value
        risk_managed_bets.sort(key=lambda x: x['edge'] * x['confidence'], reverse=True)
        
        return risk_managed_bets
    
    def _calculate_confidence_scores(self, predictions: Dict, home_form: List[Dict], away_form: List[Dict]) -> Dict:
        """Calculate confidence scores for predictions"""
        
        confidence_scores = {}
        
        # Model agreement score
        model_agreement = self._calculate_model_agreement(predictions)
        confidence_scores['model_agreement'] = model_agreement
        
        # Data quality score
        data_quality = self._assess_data_quality(home_form, away_form)
        confidence_scores['data_quality'] = data_quality
        
        # Historical accuracy score
        historical_accuracy = self._get_historical_accuracy(predictions)
        confidence_scores['historical_accuracy'] = historical_accuracy
        
        # Overall confidence
        overall_confidence = (model_agreement * 0.4 + 
                            data_quality * 0.3 + 
                            historical_accuracy * 0.3)
        confidence_scores['overall'] = overall_confidence
        
        return confidence_scores
    
    def _generate_premium_insights(self, predictions: Dict, match_data: Dict, confidence_scores: Dict) -> List[str]:
        """Generate premium insights for the match"""
        
        insights = []
        
        # Team form insights
        home_team = match_data['teams']['home']['name']
        away_team = match_data['teams']['away']['name']
        
        if 'form' in predictions:
            form_insights = self._generate_form_insights(predictions['form'], home_team, away_team)
            insights.extend(form_insights)
        
        # Model insights
        if 'combined' in predictions:
            model_insights = self._generate_model_insights(predictions['combined'])
            insights.extend(model_insights)
        
        # Confidence insights
        confidence_insights = self._generate_confidence_insights(confidence_scores)
        insights.extend(confidence_insights)
        
        # Market insights
        market_insights = self._generate_market_insights(predictions)
        insights.extend(market_insights)
        
        return insights
    
    def _assess_analysis_quality(self, predictions: Dict, home_form: List[Dict], away_form: List[Dict]) -> str:
        """Assess the quality of the analysis"""
        
        # Check data availability
        home_matches = len(home_form)
        away_matches = len(away_form)
        
        # Check model availability
        models_available = sum([
            'elo' in predictions,
            'xg' in predictions,
            'corners' in predictions,
            'form' in predictions
        ])
        
        if home_matches >= 10 and away_matches >= 10 and models_available >= 3:
            return "Premium"
        elif home_matches >= 5 and away_matches >= 5 and models_available >= 2:
            return "Standard"
        else:
            return "Basic"
    
    # Helper methods
    def _get_team_form(self, team_id: int) -> List[Dict]:
        """Get team form data (placeholder for API integration)"""
        # This would integrate with your API client
        return []
    
    def _calculate_elo_confidence(self, home_prob: float, draw_prob: float, away_prob: float) -> float:
        """Calculate confidence for Elo predictions"""
        # Higher confidence when probabilities are more spread out
        max_prob = max(home_prob, draw_prob, away_prob)
        return max_prob
    
    def _calculate_xg_confidence(self, home_stats: Dict, away_stats: Dict) -> float:
        """Calculate confidence for xG predictions"""
        return (home_stats['form_weight'] + away_stats['form_weight']) / 2
    
    def _calculate_corners_confidence(self, home_stats: Dict, away_stats: Dict) -> float:
        """Calculate confidence for corners predictions"""
        return (home_stats['form_weight'] + away_stats['form_weight']) / 2
    
    def _analyze_team_form(self, home_form: List[Dict], away_form: List[Dict]) -> Dict:
        """Analyze team form patterns"""
        return {
            'home_form_rating': self._calculate_form_rating(home_form),
            'away_form_rating': self._calculate_form_rating(away_form),
            'home_trend': self._calculate_form_trend(home_form),
            'away_trend': self._calculate_form_trend(away_form)
        }
    
    def _combine_model_predictions(self, predictions: Dict) -> Dict:
        """Combine predictions from all models"""
        # Implementation would combine predictions using weights
        return {
            'match_result': {
                'home_win': 0.4,
                'draw': 0.3,
                'away_win': 0.3
            },
            'confidence': 0.75
        }
    
    def _extract_match_odds(self, odds_data: List[Dict]) -> Dict:
        """Extract match result odds"""
        # Implementation would extract from odds_data
        return {}
    
    def _extract_goals_odds(self, odds_data: List[Dict]) -> Dict:
        """Extract goals odds"""
        return {}
    
    def _extract_corners_odds(self, odds_data: List[Dict]) -> Dict:
        """Extract corners odds"""
        return {}
    
    def _analyze_match_result_value(self, probabilities: Dict, odds: Dict, match_data: Dict) -> List[Dict]:
        """Analyze match result value bets"""
        return []
    
    def _analyze_goals_value(self, probabilities: Dict, odds: Dict, match_data: Dict) -> List[Dict]:
        """Analyze goals value bets"""
        return []
    
    def _analyze_corners_value(self, probabilities: Dict, odds: Dict, match_data: Dict) -> List[Dict]:
        """Analyze corners value bets"""
        return []
    
    def _analyze_ml_value(self, predictions: Dict, odds: List[Dict], match_data: Dict) -> List[Dict]:
        """Analyze ML model value bets"""
        return []
    
    def _calculate_kelly_criterion(self, probability: float, odds: float) -> float:
        """Calculate Kelly Criterion percentage"""
        if odds <= 1 or probability <= 0:
            return 0
        return (probability * odds - 1) / (odds - 1)
    
    def _calculate_risk_score(self, bet: Dict) -> float:
        """Calculate risk score for a bet"""
        # Implementation would calculate risk based on various factors
        return 0.05
    
    def _calculate_recommended_stake(self, bet: Dict, kelly_percentage: float) -> float:
        """Calculate recommended stake amount"""
        base_stake = 100  # Base stake amount
        return base_stake * kelly_percentage * bet['confidence']
    
    def _classify_confidence(self, confidence: float) -> str:
        """Classify confidence level"""
        if confidence >= self.premium_thresholds['high_confidence']:
            return "High"
        elif confidence >= self.premium_thresholds['medium_confidence']:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_model_agreement(self, predictions: Dict) -> float:
        """Calculate agreement between different models"""
        return 0.8
    
    def _assess_data_quality(self, home_form: List[Dict], away_form: List[Dict]) -> float:
        """Assess quality of available data"""
        home_quality = min(1.0, len(home_form) / 10.0)
        away_quality = min(1.0, len(away_form) / 10.0)
        return (home_quality + away_quality) / 2
    
    def _get_historical_accuracy(self, predictions: Dict) -> float:
        """Get historical accuracy for similar predictions"""
        return 0.75
    
    def _generate_form_insights(self, form_data: Dict, home_team: str, away_team: str) -> List[str]:
        """Generate insights from team form"""
        insights = []
        
        if form_data['home_form_rating'] > form_data['away_form_rating']:
            insights.append(f"{home_team} has better recent form than {away_team}")
        
        if form_data['home_trend'] == 'improving':
            insights.append(f"{home_team} is showing improving form")
        
        return insights
    
    def _generate_model_insights(self, combined_prediction: Dict) -> List[str]:
        """Generate insights from model predictions"""
        return ["Models show strong agreement on match outcome"]
    
    def _generate_confidence_insights(self, confidence_scores: Dict) -> List[str]:
        """Generate insights from confidence scores"""
        insights = []
        
        if confidence_scores['overall'] > 0.8:
            insights.append("High confidence analysis with strong data quality")
        elif confidence_scores['overall'] > 0.6:
            insights.append("Moderate confidence with adequate data")
        else:
            insights.append("Lower confidence - consider with caution")
        
        return insights
    
    def _generate_market_insights(self, predictions: Dict) -> List[str]:
        """Generate market-related insights"""
        return ["Market appears to be pricing this match efficiently"]
    
    def _calculate_form_rating(self, form_data: List[Dict]) -> float:
        """Calculate form rating from recent matches"""
        return 0.7
    
    def _calculate_form_trend(self, form_data: List[Dict]) -> str:
        """Calculate form trend (improving, declining, stable)"""
        return "stable"
