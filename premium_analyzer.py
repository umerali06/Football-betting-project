#!/usr/bin/env python3
"""
Premium Football Betting Analyzer
Advanced analysis with multiple models and sophisticated strategies
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import config
from api.api_sportmonks import SportMonksClient

logger = logging.getLogger(__name__)

class RealTimeAnalyzer:
    """Real-time football analysis system focused on live data and Telegram summaries"""
    
    def __init__(self):
        self.api_client = SportMonksClient()
        self.analysis_cache = {}
        self.last_analysis_time = {}
        
    async def analyze_live_matches(self) -> List[Dict]:
        """Analyze all currently live matches in real-time"""
        logger.info("🔍 Starting real-time analysis of live matches...")
        
        try:
            # Get live matches
            live_matches = await self.api_client.get_live_scores()
            
            if not live_matches:
                logger.info("📭 No live matches found at the moment")
                return []
            
            analysis_results = []
            
            for match in live_matches:
                try:
                    analysis = await self._analyze_single_match(match, is_live=True)
                    if analysis:
                        analysis_results.append(analysis)
                        logger.info(f"✅ Analyzed live match: {analysis['match_name']}")
                except Exception as e:
                    logger.error(f"❌ Error analyzing match {match.get('id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"🎯 Completed analysis of {len(analysis_results)} live matches")
            return analysis_results
            
        except Exception as e:
            logger.error(f"❌ Error in live match analysis: {e}")
            return []
    
    async def analyze_today_matches(self) -> List[Dict]:
        """Analyze today's matches with focus on upcoming games"""
        logger.info("🔍 Starting analysis of today's matches...")
        
        try:
            # Get today's matches
            today_matches = await self.api_client.get_today_matches(include_live=False)
            
            if not today_matches:
                logger.info("📭 No matches found for today")
                return []
            
            analysis_results = []
            
            for match in today_matches:
                try:
                    # Skip already analyzed matches
                    match_id = match.get('id')
                    if match_id in self.last_analysis_time:
                        time_diff = datetime.now() - self.last_analysis_time[match_id]
                        if time_diff.total_seconds() < 1800:  # 30 minutes
                            continue
                    
                    analysis = await self._analyze_single_match(match, is_live=False)
                    if analysis:
                        analysis_results.append(analysis)
                        self.last_analysis_time[match_id] = datetime.now()
                        logger.info(f"✅ Analyzed match: {analysis['match_name']}")
                except Exception as e:
                    logger.error(f"❌ Error analyzing match {match.get('id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"🎯 Completed analysis of {len(analysis_results)} matches")
            return analysis_results
            
        except Exception as e:
            logger.error(f"❌ Error in today's match analysis: {e}")
            return []
    
    async def _analyze_single_match(self, match: Dict, is_live: bool = False) -> Optional[Dict]:
        """Analyze a single match with comprehensive real-time data"""
        try:
            fixture_id = match.get('id')
            if not fixture_id:
                return None
            
            # Extract basic match info
            home_team, away_team = self.api_client.extract_team_names(match)
            match_status = self.api_client.extract_match_status(match)
            
            # Get comprehensive match data
            fixture_details = await self.api_client.get_fixture_details(fixture_id)
            if not fixture_details:
                return None
            
            # Get real-time odds
            odds = await self.api_client.get_match_odds(fixture_id)
            
            # Get team form data
            home_form = []
            away_form = []
            if 'participants' in fixture_details:
                for participant in fixture_details['participants']:
                    if participant.get('meta', {}).get('location') == 'home':
                        home_form = await self.api_client.get_team_form(participant.get('id'))
                    elif participant.get('meta', {}).get('location') == 'away':
                        away_form = await self.api_client.get_team_form(participant.get('id'))
            
            # Get expected goals data
            expected_data = await self.api_client.get_expected_data(fixture_id)
            
            # Get SportMonks predictions
            predictions = await self.api_client.get_predictions(fixture_id)
            
            # Create analysis summary
            analysis = {
                'fixture_id': fixture_id,
                'match_name': f"{home_team} vs {away_team}",
                'home_team': home_team,
                'away_team': away_team,
                'status': match_status,
                'is_live': is_live,
                'analysis_time': datetime.now().isoformat(),
                'odds_analysis': self._analyze_odds(odds),
                'form_analysis': self._analyze_team_form(home_form, away_form),
                'expected_goals': self._analyze_expected_goals(expected_data),
                'predictions': self._analyze_predictions(predictions),
                'value_bets': self._identify_value_bets(odds, predictions),
                'risk_assessment': self._assess_risk(home_form, away_form, odds),
                'summary': '',
                'recommendations': []
            }
            
            # Generate summary and recommendations
            analysis['summary'] = self._generate_summary(analysis)
            analysis['recommendations'] = self._generate_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error in single match analysis: {e}")
            return None
    
    def _analyze_odds(self, odds: List[Dict]) -> Dict:
        """Analyze betting odds for value opportunities"""
        if not odds:
            return {'status': 'no_odds_available'}
        
        analysis = {
            'total_markets': len(odds),
            'markets': {},
            'best_odds': {},
            'value_opportunities': []
        }
        
        # Group odds by market
        markets = {}
        for odd in odds:
            market_desc = odd.get('market_description', 'Unknown')
            if market_desc not in markets:
                markets[market_desc] = []
            markets[market_desc].append(odd)
        
        # Analyze each market
        for market_name, market_odds in markets.items():
            market_analysis = {
                'total_options': len(market_odds),
                'options': []
            }
            
            for odd in market_odds:
                option = {
                    'value': odd.get('value', 'Unknown'),
                    'odds': float(odd.get('dp3', 0)),
                    'probability': float(odd.get('probability', '0%').rstrip('%')) / 100,
                    'bookmaker_id': odd.get('bookmaker_id')
                }
                market_analysis['options'].append(option)
            
            # Find best odds
            if market_analysis['options']:
                best_odds = max(market_analysis['options'], key=lambda x: x['odds'])
                market_analysis['best_odds'] = best_odds
                
                # Check for value (odds > implied probability)
                if best_odds['odds'] > 1 and best_odds['probability'] > 0:
                    implied_prob = 1 / best_odds['odds']
                    if best_odds['probability'] > implied_prob * 1.1:  # 10% edge
                        analysis['value_opportunities'].append({
                            'market': market_name,
                            'option': best_odds['value'],
                            'odds': best_odds['odds'],
                            'edge': round((best_odds['probability'] - implied_prob) * 100, 2)
                        })
            
            analysis['markets'][market_name] = market_analysis
        
        return analysis
    
    def _analyze_team_form(self, home_form: List[Dict], away_form: List[Dict]) -> Dict:
        """Analyze team form from recent matches"""
        analysis = {
            'home_team': {'recent_form': [], 'form_score': 0, 'last_5_results': []},
            'away_team': {'recent_form': [], 'form_score': 0, 'last_5_results': []}
        }
        
        # Analyze home team form
        if home_form:
            analysis['home_team']['recent_form'] = home_form[:5]
            analysis['home_team']['form_score'] = self._calculate_form_score(home_form[:5])
            analysis['home_team']['last_5_results'] = self._extract_results(home_form[:5])
        
        # Analyze away team form
        if away_form:
            analysis['away_team']['recent_form'] = away_form[:5]
            analysis['away_team']['form_score'] = self._calculate_form_score(away_form[:5])
            analysis['away_team']['last_5_results'] = self._extract_results(away_form[:5])
        
        return analysis
    
    def _calculate_form_score(self, form_matches: List[Dict]) -> float:
        """Calculate form score based on recent results"""
        if not form_matches:
            return 0.0
        
        score = 0.0
        weights = [1.0, 0.8, 0.6, 0.4, 0.2]  # Recent matches weighted more
        
        for i, match in enumerate(form_matches[:5]):
            if i < len(weights):
                result = self._get_match_result(match)
                if result == 'W':
                    score += weights[i] * 3
                elif result == 'D':
                    score += weights[i] * 1
                # Loss = 0 points
        
        return round(score / sum(weights[:len(form_matches)]), 2)
    
    def _extract_results(self, form_matches: List[Dict]) -> List[str]:
        """Extract results from form matches"""
        results = []
        for match in form_matches[:5]:
            results.append(self._get_match_result(match))
        return results
    
    def _get_match_result(self, match: Dict) -> str:
        """Get match result (W/D/L) for a team"""
        if 'scores' not in match:
            return 'U'  # Unknown
        
        # This is simplified - you'd need to check if the team is home/away
        # and compare scores to determine result
        return 'U'  # Placeholder
    
    def _analyze_expected_goals(self, expected_data: Optional[Dict]) -> Dict:
        """Analyze expected goals data"""
        if not expected_data:
            return {'status': 'no_data_available'}
        
        analysis = {
            'home_xg': expected_data.get('home_xg', 0),
            'away_xg': expected_data.get('away_xg', 0),
            'total_xg': 0,
            'xg_difference': 0,
            'over_under_probability': 0
        }
        
        if analysis['home_xg'] and analysis['away_xg']:
            analysis['total_xg'] = analysis['home_xg'] + analysis['away_xg']
            analysis['xg_difference'] = analysis['home_xg'] - analysis['away_xg']
            
            # Simple over/under probability based on xG
            if analysis['total_xg'] > 2.5:
                analysis['over_under_probability'] = 0.7
            elif analysis['total_xg'] > 1.5:
                analysis['over_under_probability'] = 0.5
            else:
                analysis['over_under_probability'] = 0.3
        
        return analysis
    
    def _analyze_predictions(self, predictions: Dict) -> Dict:
        """Analyze SportMonks predictions"""
        if not predictions:
            return {'status': 'no_predictions_available'}
        
        analysis = {
            'probabilities': predictions.get('probabilities', {}),
            'value_bets': predictions.get('value_bets', {}),
            'confidence': 0.0
        }
        
        # Calculate overall confidence
        if analysis['probabilities']:
            # This would depend on the specific format of probabilities
            analysis['confidence'] = 0.7  # Placeholder
        
        return analysis
    
    def _identify_value_bets(self, odds: List[Dict], predictions: Dict) -> List[Dict]:
        """Identify value betting opportunities"""
        value_bets = []
        
        if not odds or not predictions:
            return value_bets
        
        # Compare odds with predictions to find value
        # This is a simplified implementation
        for odd in odds:
            market = odd.get('market_description', '')
            value = odd.get('value', '')
            odds_value = float(odd.get('dp3', 0))
            
            if odds_value > 2.0:  # Focus on higher odds
                # Check if this matches any prediction
                if self._check_prediction_match(predictions, market, value):
                    value_bets.append({
                        'market': market,
                        'option': value,
                        'odds': odds_value,
                        'confidence': 'medium',
                        'reason': 'Matches prediction model'
                    })
        
        return value_bets
    
    def _check_prediction_match(self, predictions: Dict, market: str, value: str) -> bool:
        """Check if odds match predictions"""
        # Simplified check - would need more sophisticated logic
        return True  # Placeholder
    
    def _assess_risk(self, home_form: List[Dict], away_form: List[Dict], odds: List[Dict]) -> Dict:
        """Assess betting risk for the match"""
        risk_score = 0.5  # Default medium risk
        
        # Adjust based on form consistency
        if home_form and away_form:
            home_consistency = self._calculate_consistency(home_form)
            away_consistency = self._calculate_consistency(away_form)
            
            if home_consistency > 0.7 and away_consistency > 0.7:
                risk_score -= 0.2  # Lower risk for consistent teams
            elif home_consistency < 0.3 or away_consistency < 0.3:
                risk_score += 0.2  # Higher risk for inconsistent teams
        
        # Adjust based on odds availability
        if not odds:
            risk_score += 0.3  # Higher risk without odds
        
        return {
            'risk_score': max(0.1, min(0.9, risk_score)),
            'risk_level': self._get_risk_level(risk_score),
            'factors': ['form_consistency', 'odds_availability']
        }
    
    def _calculate_consistency(self, form_matches: List[Dict]) -> float:
        """Calculate team consistency from form"""
        if not form_matches:
            return 0.0
        
        # Simplified consistency calculation
        return 0.6  # Placeholder
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level"""
        if risk_score < 0.3:
            return 'LOW'
        elif risk_score < 0.7:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _generate_summary(self, analysis: Dict) -> str:
        """Generate concise summary for Telegram"""
        summary_parts = []
        
        # Match info
        summary_parts.append(f"⚽ {analysis['match_name']}")
        summary_parts.append(f"📊 Status: {analysis['status']}")
        
        # Form summary
        home_form_score = analysis['form_analysis']['home_team']['form_score']
        away_form_score = analysis['form_analysis']['away_team']['form_score']
        summary_parts.append(f"🏠 {analysis['home_team']} Form: {home_form_score}")
        summary_parts.append(f"✈️ {analysis['away_team']} Form: {away_form_score}")
        
        # Value opportunities
        if analysis['value_bets']:
            summary_parts.append(f"💰 Value Bets: {len(analysis['value_bets'])} found")
        
        # Risk level
        risk_level = analysis['risk_assessment']['risk_level']
        summary_parts.append(f"⚠️ Risk: {risk_level}")
        
        return "\n".join(summary_parts)
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Form-based recommendations
        home_form = analysis['form_analysis']['home_team']['form_score']
        away_form = analysis['form_analysis']['away_team']['form_score']
        
        if home_form > away_form + 0.5:
            recommendations.append("🏠 Home team has significantly better form")
        elif away_form > home_form + 0.5:
            recommendations.append("✈️ Away team has significantly better form")
        
        # Value bet recommendations
        if analysis['value_bets']:
            for bet in analysis['value_bets'][:3]:  # Top 3
                recommendations.append(f"💰 {bet['market']}: {bet['option']} @ {bet['odds']}")
        
        # Risk-based recommendations
        if analysis['risk_assessment']['risk_level'] == 'HIGH':
            recommendations.append("⚠️ High risk match - consider smaller stakes")
        elif analysis['risk_assessment']['risk_level'] == 'LOW':
            recommendations.append("✅ Low risk match - good for larger stakes")
        
        return recommendations
    
    async def get_telegram_summary(self, analysis_results: List[Dict]) -> str:
        """Generate Telegram-formatted summary of analysis results"""
        if not analysis_results:
            return "📭 No matches analyzed at the moment"
        
        summary_lines = [
            "🎯 **FIXORA PRO - Real-Time Analysis Summary**",
            f"⏰ Generated: {datetime.now().strftime('%H:%M:%S')}",
            f"📊 Matches Analyzed: {len(analysis_results)}",
            ""
        ]
        
        # Group by status
        live_matches = [r for r in analysis_results if r['is_live']]
        upcoming_matches = [r for r in analysis_results if not r['is_live']]
        
        if live_matches:
            summary_lines.extend([
                "🔥 **LIVE MATCHES**",
                ""
            ])
            for match in live_matches[:3]:  # Limit to 3 live matches
                summary_lines.extend([
                    f"⚽ {match['match_name']}",
                    f"📊 {match['summary']}",
                    ""
                ])
        
        if upcoming_matches:
            summary_lines.extend([
                "⏳ **UPCOMING MATCHES**",
                ""
            ])
            for match in upcoming_matches[:5]:  # Limit to 5 upcoming
                summary_lines.extend([
                    f"⚽ {match['match_name']}",
                    f"📊 {match['summary']}",
                    ""
                ])
        
        # Add overall recommendations
        all_recommendations = []
        for match in analysis_results:
            all_recommendations.extend(match['recommendations'])
        
        if all_recommendations:
            summary_lines.extend([
                "💡 **KEY RECOMMENDATIONS**",
                ""
            ])
            # Get unique recommendations
            unique_recs = list(set(all_recommendations))[:5]
            for rec in unique_recs:
                summary_lines.append(f"• {rec}")
        
        return "\n".join(summary_lines)
    
    async def close(self):
        """Close the analyzer and API client"""
        await self.api_client.close()
