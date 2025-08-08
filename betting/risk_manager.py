import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import config
from datetime import datetime, timedelta

class AdvancedRiskManager:
    """
    Advanced risk management system for football betting
    Implements Kelly Criterion, bankroll management, and sophisticated bet sizing
    """
    
    def __init__(self, initial_bankroll: float = 10000.0):
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.bet_history = []
        self.daily_bets = 0
        self.daily_date = datetime.now().date()
        self.streak_tracker = {'wins': 0, 'losses': 0, 'current_streak': 0}
        
    def calculate_kelly_stake(self, model_probability: float, odds: float, 
                            confidence: float) -> Tuple[float, float]:
        """
        Calculate optimal stake using Kelly Criterion
        
        Args:
            model_probability: Our model's predicted probability
            odds: Bookmaker odds
            confidence: Model confidence (0-1)
            
        Returns:
            Tuple of (kelly_percentage, recommended_stake)
        """
        implied_probability = 1.0 / odds
        edge = model_probability - implied_probability
        
        if edge <= 0:
            return 0.0, 0.0
        
        # Kelly Criterion formula: f = (bp - q) / b
        # where b = odds - 1, p = our probability, q = 1 - p
        b = odds - 1
        p = model_probability
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b
        
        # Apply confidence adjustment
        adjusted_kelly = kelly_fraction * confidence
        
        # Apply fractional Kelly (more conservative)
        fractional_kelly = adjusted_kelly * 0.25  # Use 25% of Kelly
        
        # Calculate stake
        stake = fractional_kelly * self.current_bankroll
        
        return fractional_kelly, stake
    
    def calculate_optimal_stake(self, bet_data: Dict) -> Dict:
        """
        Calculate optimal stake for a bet considering all risk factors
        
        Args:
            bet_data: Dictionary containing bet information
            
        Returns:
            Dictionary with stake recommendations
        """
        model_prob = bet_data['model_probability']
        odds = bet_data['odds']
        confidence = bet_data.get('confidence', 0.7)
        edge = bet_data['edge']
        
        # Kelly Criterion
        kelly_percentage, kelly_stake = self.calculate_kelly_stake(
            model_prob, odds, confidence
        )
        
        # Fixed percentage of bankroll
        fixed_percentage = config.BANKROLL_PERCENTAGE
        fixed_stake = self.current_bankroll * fixed_percentage
        
        # Edge-based stake (higher edge = higher stake)
        edge_multiplier = min(edge / 0.05, 3.0)  # Cap at 3x for high edges
        edge_stake = fixed_stake * edge_multiplier
        
        # Confidence-based adjustment
        confidence_multiplier = confidence
        confidence_stake = edge_stake * confidence_multiplier
        
        # Risk-adjusted stake (considering daily limits)
        daily_remaining = config.MAX_BETS_PER_DAY - self.daily_bets
        if daily_remaining <= 0:
            risk_stake = 0.0
        else:
            risk_stake = confidence_stake / daily_remaining
        
        # Final stake (minimum of all methods)
        final_stake = min(kelly_stake, confidence_stake, risk_stake)
        
        # Ensure minimum and maximum stakes
        min_stake = 10.0  # Minimum £10
        max_stake = self.current_bankroll * 0.05  # Maximum 5% of bankroll
        
        final_stake = max(min_stake, min(final_stake, max_stake))
        
        return {
            'kelly_stake': kelly_stake,
            'fixed_stake': fixed_stake,
            'edge_stake': edge_stake,
            'confidence_stake': confidence_stake,
            'risk_stake': risk_stake,
            'final_stake': final_stake,
            'kelly_percentage': kelly_percentage,
            'edge_multiplier': edge_multiplier,
            'confidence_multiplier': confidence_multiplier
        }
    
    def validate_bet(self, bet_data: Dict) -> Tuple[bool, str]:
        """
        Validate if a bet meets risk management criteria
        
        Args:
            bet_data: Dictionary containing bet information
            
        Returns:
            Tuple of (is_valid, reason)
        """
        # Check daily bet limit
        if self.daily_bets >= config.MAX_BETS_PER_DAY:
            return False, "Daily bet limit reached"
        
        # Check edge threshold
        if bet_data['edge'] < config.VALUE_BET_THRESHOLD:
            return False, f"Edge too low: {bet_data['edge']:.3f}"
        
        # Check odds range
        if not (config.MIN_ODDS <= bet_data['odds'] <= config.MAX_ODDS):
            return False, f"Odds outside range: {bet_data['odds']}"
        
        # Check confidence threshold
        confidence = bet_data.get('confidence', 0.5)
        if confidence < config.CONFIDENCE_THRESHOLD:
            return False, f"Confidence too low: {confidence:.3f}"
        
        # Check bankroll percentage
        stake_calc = self.calculate_optimal_stake(bet_data)
        if stake_calc['final_stake'] < 10.0:
            return False, "Stake too low"
        
        # Check Kelly Criterion
        if stake_calc['kelly_percentage'] <= 0:
            return False, "Kelly Criterion negative"
        
        return True, "Bet validated"
    
    def record_bet(self, bet_data: Dict, stake: float, result: str):
        """
        Record a bet result and update bankroll
        
        Args:
            bet_data: Original bet data
            stake: Stake amount
            result: 'win', 'loss', or 'push'
        """
        bet_record = {
            'date': datetime.now(),
            'match': f"{bet_data['match_info']['home_team']} vs {bet_data['match_info']['away_team']}",
            'market': bet_data['market'],
            'selection': bet_data['selection'],
            'odds': bet_data['odds'],
            'stake': stake,
            'edge': bet_data['edge'],
            'confidence': bet_data.get('confidence', 0.5),
            'result': result,
            'bankroll_before': self.current_bankroll
        }
        
        # Calculate profit/loss
        if result == 'win':
            profit = stake * (bet_data['odds'] - 1)
            self.current_bankroll += profit
            bet_record['profit'] = profit
            self.streak_tracker['wins'] += 1
            if self.streak_tracker['current_streak'] >= 0:
                self.streak_tracker['current_streak'] += 1
            else:
                self.streak_tracker['current_streak'] = 1
        elif result == 'loss':
            profit = -stake
            self.current_bankroll += profit
            bet_record['profit'] = profit
            self.streak_tracker['losses'] += 1
            if self.streak_tracker['current_streak'] <= 0:
                self.streak_tracker['current_streak'] -= 1
            else:
                self.streak_tracker['current_streak'] = -1
        else:  # push
            bet_record['profit'] = 0
        
        bet_record['bankroll_after'] = self.current_bankroll
        bet_record['roi'] = bet_record['profit'] / stake if stake > 0 else 0
        
        self.bet_history.append(bet_record)
        self.daily_bets += 1
        
        # Reset daily counter if new day
        if datetime.now().date() != self.daily_date:
            self.daily_bets = 0
            self.daily_date = datetime.now().date()
    
    def get_performance_metrics(self) -> Dict:
        """Get comprehensive performance metrics"""
        if not self.bet_history:
            return {}
        
        total_bets = len(self.bet_history)
        winning_bets = len([b for b in self.bet_history if b['result'] == 'win'])
        losing_bets = len([b for b in self.bet_history if b['result'] == 'loss'])
        
        win_rate = winning_bets / total_bets if total_bets > 0 else 0
        
        total_profit = sum(b['profit'] for b in self.bet_history)
        total_staked = sum(b['stake'] for b in self.bet_history)
        overall_roi = total_profit / total_staked if total_staked > 0 else 0
        
        # Calculate average edge
        avg_edge = np.mean([b['edge'] for b in self.bet_history])
        
        # Calculate average confidence
        avg_confidence = np.mean([b['confidence'] for b in self.bet_history])
        
        # Calculate bankroll growth
        bankroll_growth = (self.current_bankroll - self.initial_bankroll) / self.initial_bankroll
        
        # Calculate streak information
        current_streak = self.streak_tracker['current_streak']
        
        # Calculate Kelly efficiency
        kelly_efficiency = self._calculate_kelly_efficiency()
        
        return {
            'total_bets': total_bets,
            'winning_bets': winning_bets,
            'losing_bets': losing_bets,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'total_staked': total_staked,
            'overall_roi': overall_roi,
            'avg_edge': avg_edge,
            'avg_confidence': avg_confidence,
            'bankroll_growth': bankroll_growth,
            'current_bankroll': self.current_bankroll,
            'current_streak': current_streak,
            'kelly_efficiency': kelly_efficiency
        }
    
    def _calculate_kelly_efficiency(self) -> float:
        """Calculate how well we're following Kelly Criterion"""
        if not self.bet_history:
            return 0.0
        
        kelly_percentages = []
        for bet in self.bet_history:
            # Recalculate Kelly for historical bet
            model_prob = 1.0 / bet['odds'] + bet['edge']
            kelly_pct, _ = self.calculate_kelly_stake(
                model_prob, bet['odds'], bet['confidence']
            )
            kelly_percentages.append(kelly_pct)
        
        # Calculate average Kelly percentage used
        avg_kelly_used = np.mean(kelly_percentages)
        
        # Ideal Kelly percentage (theoretical)
        ideal_kelly = 0.25  # 25% of Kelly
        
        # Efficiency = actual / ideal
        efficiency = avg_kelly_used / ideal_kelly if ideal_kelly > 0 else 0
        
        return min(efficiency, 1.0)  # Cap at 100%
    
    def get_risk_alerts(self) -> List[str]:
        """Get risk management alerts"""
        alerts = []
        
        # Check daily bet limit
        if self.daily_bets >= config.MAX_BETS_PER_DAY * 0.8:
            alerts.append(f"Approaching daily bet limit: {self.daily_bets}/{config.MAX_BETS_PER_DAY}")
        
        # Check bankroll decline
        if self.current_bankroll < self.initial_bankroll * 0.9:
            alerts.append(f"Bankroll declined by {((self.initial_bankroll - self.current_bankroll) / self.initial_bankroll) * 100:.1f}%")
        
        # Check losing streak
        if self.streak_tracker['current_streak'] <= -config.ALERT_STREAK:
            alerts.append(f"Losing streak: {abs(self.streak_tracker['current_streak'])} consecutive losses")
        
        # Check win rate
        metrics = self.get_performance_metrics()
        if metrics.get('win_rate', 0) < 0.4:
            alerts.append(f"Low win rate: {metrics['win_rate']:.1%}")
        
        return alerts
    
    def get_bet_recommendations(self, value_bets: List[Dict]) -> List[Dict]:
        """
        Get bet recommendations with risk management applied
        
        Args:
            value_bets: List of value bets from analyzer
            
        Returns:
            List of recommended bets with stakes
        """
        recommendations = []
        
        for bet in value_bets:
            # Validate bet
            is_valid, reason = self.validate_bet(bet)
            
            if not is_valid:
                continue
            
            # Calculate optimal stake
            stake_calc = self.calculate_optimal_stake(bet)
            
            recommendation = {
                **bet,
                'stake_calculation': stake_calc,
                'recommended_stake': stake_calc['final_stake'],
                'kelly_percentage': stake_calc['kelly_percentage'],
                'risk_score': self._calculate_risk_score(bet, stake_calc)
            }
            
            recommendations.append(recommendation)
        
        # Sort by risk-adjusted return
        recommendations.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return recommendations
    
    def _calculate_risk_score(self, bet: Dict, stake_calc: Dict) -> float:
        """Calculate risk-adjusted return score"""
        edge = bet['edge']
        confidence = bet.get('confidence', 0.5)
        kelly_pct = stake_calc['kelly_percentage']
        
        # Risk score = edge * confidence * kelly_percentage
        risk_score = edge * confidence * kelly_pct
        
        return risk_score
    
    def reset_daily_counters(self):
        """Reset daily betting counters"""
        self.daily_bets = 0
        self.daily_date = datetime.now().date()
    
    def export_bet_history(self, filepath: str):
        """Export bet history to CSV"""
        df = pd.DataFrame(self.bet_history)
        df.to_csv(filepath, index=False)
        print(f"Bet history exported to {filepath}")
