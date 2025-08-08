import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import os
from typing import Dict, List, Tuple, Optional
import config
from datetime import datetime, timedelta

class AdvancedMLModel:
    """
    Advanced Machine Learning model for football predictions
    Uses ensemble methods and sophisticated feature engineering
    """
    
    def __init__(self):
        self.models = {
            'match_result': None,
            'btts': None,
            'over_under': None,
            'corners': None
        }
        self.scalers = {}
        self.feature_importance = {}
        self.model_performance = {}
        self.is_trained = False
        
    def extract_advanced_features(self, match_data: Dict, home_form: List[Dict], 
                                away_form: List[Dict]) -> Dict[str, float]:
        """Extract sophisticated features for ML model"""
        features = {}
        
        # Basic team features
        features['home_elo'] = self._get_team_elo(match_data['teams']['home']['id'])
        features['away_elo'] = self._get_team_elo(match_data['teams']['away']['id'])
        features['elo_difference'] = features['home_elo'] - features['away_elo']
        
        # Form-based features
        home_recent_form = self._calculate_weighted_form(home_form, 5)
        away_recent_form = self._calculate_weighted_form(away_form, 5)
        features['home_form'] = home_recent_form
        features['away_form'] = away_recent_form
        features['form_difference'] = home_recent_form - away_recent_form
        
        # Advanced statistical features
        home_stats = self._extract_team_stats(home_form)
        away_stats = self._extract_team_stats(away_form)
        
        features.update({
            'home_goals_scored_avg': home_stats['goals_scored_avg'],
            'home_goals_conceded_avg': home_stats['goals_conceded_avg'],
            'away_goals_scored_avg': away_stats['goals_scored_avg'],
            'away_goals_conceded_avg': away_stats['goals_conceded_avg'],
            'home_shots_avg': home_stats['shots_avg'],
            'away_shots_avg': away_stats['shots_avg'],
            'home_possession_avg': home_stats['possession_avg'],
            'away_possession_avg': away_stats['possession_avg'],
            'home_corners_avg': home_stats['corners_avg'],
            'away_corners_avg': away_stats['corners_avg'],
            'home_cards_avg': home_stats['cards_avg'],
            'away_cards_avg': away_stats['cards_avg']
        })
        
        # Derived features
        features['total_goals_expected'] = (home_stats['goals_scored_avg'] + 
                                          away_stats['goals_scored_avg'])
        features['goals_difference'] = (home_stats['goals_scored_avg'] - 
                                      home_stats['goals_conceded_avg']) - \
                                     (away_stats['goals_scored_avg'] - 
                                      away_stats['goals_conceded_avg'])
        
        # Home advantage features
        features['home_advantage'] = config.HOME_ADVANTAGE_BOOST
        features['away_penalty'] = config.AWAY_PENALTY
        
        # League quality features
        features['league_quality'] = self._get_league_quality(match_data)
        
        # Weather and external factors (if available)
        features['weather_factor'] = self._get_weather_factor(match_data)
        features['referee_factor'] = self._get_referee_factor(match_data)
        
        return features
    
    def _get_team_elo(self, team_id: int) -> float:
        """Get team Elo rating (placeholder - would integrate with Elo model)"""
        # This would integrate with the actual Elo model
        return 1500.0  # Default rating
    
    def _calculate_weighted_form(self, form_data: List[Dict], matches: int) -> float:
        """Calculate weighted form based on recent performance"""
        if not form_data:
            return 0.0
        
        recent_matches = form_data[:matches]
        weights = np.array([config.FORM_WEIGHT_RECENT, config.FORM_WEIGHT_MEDIUM, 
                           config.FORM_WEIGHT_OLD])
        
        form_scores = []
        for match in recent_matches:
            if match.get('result') == 'W':
                form_scores.append(3)
            elif match.get('result') == 'D':
                form_scores.append(1)
            else:
                form_scores.append(0)
        
        if form_scores:
            return np.average(form_scores, weights=weights[:len(form_scores)])
        return 0.0
    
    def _extract_team_stats(self, form_data: List[Dict]) -> Dict[str, float]:
        """Extract comprehensive team statistics"""
        stats = {
            'goals_scored_avg': 0.0,
            'goals_conceded_avg': 0.0,
            'shots_avg': 0.0,
            'possession_avg': 50.0,
            'corners_avg': 0.0,
            'cards_avg': 0.0
        }
        
        if not form_data:
            return stats
        
        total_matches = len(form_data)
        
        for match in form_data:
            # Goals
            stats['goals_scored_avg'] += match.get('goals_scored', 0)
            stats['goals_conceded_avg'] += match.get('goals_conceded', 0)
            
            # Shots
            stats['shots_avg'] += match.get('shots', 0)
            
            # Possession
            stats['possession_avg'] += match.get('possession', 50)
            
            # Corners
            stats['corners_avg'] += match.get('corners', 0)
            
            # Cards
            stats['cards_avg'] += match.get('cards', 0)
        
        # Calculate averages
        for key in stats:
            if key != 'possession_avg':
                stats[key] = stats[key] / total_matches if total_matches > 0 else 0.0
            else:
                stats[key] = stats[key] / total_matches if total_matches > 0 else 50.0
        
        return stats
    
    def _get_league_quality(self, match_data: Dict) -> float:
        """Get league quality score"""
        league_id = match_data.get('league', {}).get('id', 0)
        # This would be based on league rankings, team strengths, etc.
        return 0.7  # Default quality score
    
    def _get_weather_factor(self, match_data: Dict) -> float:
        """Get weather impact factor"""
        # This would integrate with weather API
        return 1.0  # Neutral weather
    
    def _get_referee_factor(self, match_data: Dict) -> float:
        """Get referee impact factor"""
        # This would be based on referee statistics
        return 1.0  # Neutral referee
    
    def train_model(self, training_data: List[Dict], market_type: str):
        """Train ML model for specific market type"""
        if len(training_data) < config.ML_MIN_TRAINING_MATCHES:
            print(f"Insufficient training data for {market_type}. Need at least {config.ML_MIN_TRAINING_MATCHES} matches.")
            return False
        
        # Prepare features and labels
        X = []
        y = []
        
        for match in training_data:
            features = self.extract_advanced_features(
                match['match_data'], 
                match['home_form'], 
                match['away_form']
            )
            
            # Convert features to array
            feature_array = list(features.values())
            X.append(feature_array)
            
            # Prepare label based on market type
            if market_type == 'match_result':
                y.append(match['result'])  # 'H', 'D', 'A'
            elif market_type == 'btts':
                y.append(1 if match['btts'] else 0)
            elif market_type == 'over_under':
                y.append(1 if match['over_under'] else 0)
            elif market_type == 'corners':
                y.append(1 if match['corners_over'] else 0)
        
        X = np.array(X)
        y = np.array(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train ensemble model
        model = self._create_ensemble_model()
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        # Store model and performance
        self.models[market_type] = model
        self.scalers[market_type] = scaler
        self.model_performance[market_type] = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }
        
        # Feature importance
        if hasattr(model, 'feature_importances_'):
            self.feature_importance[market_type] = model.feature_importances_
        
        print(f"Model trained for {market_type}:")
        print(f"  Accuracy: {accuracy:.3f}")
        print(f"  Precision: {precision:.3f}")
        print(f"  Recall: {recall:.3f}")
        print(f"  F1-Score: {f1:.3f}")
        
        return True
    
    def _create_ensemble_model(self):
        """Create ensemble model with multiple algorithms"""
        models = [
            RandomForestClassifier(n_estimators=100, random_state=42),
            GradientBoostingClassifier(n_estimators=100, random_state=42),
            LogisticRegression(random_state=42, max_iter=1000)
        ]
        
        # For now, return the best performing model
        # In production, you'd use voting or stacking
        return RandomForestClassifier(n_estimators=100, random_state=42)
    
    def predict(self, match_data: Dict, home_form: List[Dict], 
                away_form: List[Dict], market_type: str) -> Tuple[float, float]:
        """Make prediction with confidence score"""
        if not self.models.get(market_type):
            return 0.5, 0.5  # Default prediction
        
        # Extract features
        features = self.extract_advanced_features(match_data, home_form, away_form)
        feature_array = np.array(list(features.values())).reshape(1, -1)
        
        # Scale features
        scaler = self.scalers[market_type]
        feature_scaled = scaler.transform(feature_array)
        
        # Make prediction
        model = self.models[market_type]
        prediction = model.predict_proba(feature_scaled)[0]
        
        # Calculate confidence based on model certainty
        confidence = np.max(prediction)
        
        return prediction[1], confidence  # Return positive class probability and confidence
    
    def save_models(self, filepath: str):
        """Save trained models to disk"""
        model_data = {
            'models': self.models,
            'scalers': self.scalers,
            'performance': self.model_performance,
            'feature_importance': self.feature_importance
        }
        joblib.dump(model_data, filepath)
        print(f"Models saved to {filepath}")
    
    def load_models(self, filepath: str):
        """Load trained models from disk"""
        if os.path.exists(filepath):
            model_data = joblib.load(filepath)
            self.models = model_data['models']
            self.scalers = model_data['scalers']
            self.model_performance = model_data['performance']
            self.feature_importance = model_data['feature_importance']
            self.is_trained = True
            print(f"Models loaded from {filepath}")
            return True
        return False
    
    def get_model_performance(self) -> Dict:
        """Get performance metrics for all models"""
        return self.model_performance
    
    def get_feature_importance(self, market_type: str) -> List[Tuple[str, float]]:
        """Get feature importance for specific market"""
        if market_type in self.feature_importance:
            importance = self.feature_importance[market_type]
            feature_names = [
                'home_elo', 'away_elo', 'elo_difference', 'home_form', 'away_form',
                'form_difference', 'home_goals_scored_avg', 'home_goals_conceded_avg',
                'away_goals_scored_avg', 'away_goals_conceded_avg', 'home_shots_avg',
                'away_shots_avg', 'home_possession_avg', 'away_possession_avg',
                'home_corners_avg', 'away_corners_avg', 'home_cards_avg', 'away_cards_avg',
                'total_goals_expected', 'goals_difference', 'home_advantage',
                'away_penalty', 'league_quality', 'weather_factor', 'referee_factor'
            ]
            return list(zip(feature_names, importance))
        return []
