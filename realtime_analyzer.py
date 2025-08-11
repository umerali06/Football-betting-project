import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from api.unified_api_client import UnifiedAPIClient

logger = logging.getLogger(__name__)


def _escape_markdown(text: str) -> str:
    """
    Escape Telegram MarkdownV2 special chars to avoid formatting errors.
    If you use parse_mode='MarkdownV2' in your sender, this keeps things safe.
    If you send as plain text (no parse mode), escaping is harmless.
    """
    if text is None:
        return ""
    # characters to escape in MarkdownV2
    specials = r"_*[]()~`>#+-=|{}.!"
    out = []
    for ch in str(text):
        if ch in specials:
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "".join(out)


def _truncate(s: str, max_len: int = 3900) -> str:
    """Stay well under Telegram 4096-char hard limit; leave some headroom."""
    return s if len(s) <= max_len else s[:max_len - 20] + " …"


class RealTimeAnalyzer:
    """Real-time football analysis system focused on live data and Telegram summaries"""

    def __init__(self):
        self.api_client = UnifiedAPIClient()
        self.analysis_cache: Dict = {}
        self.last_analysis_time: Dict = {}
        self.subscription_features = {
            "odds": True,            # Basic odds are usually available
            "team_form": True,       # Basic team data is usually available
            "xg_data": False,        # May require subscription
            "predictions": False,    # May require subscription
            "advanced_stats": False  # May require subscription
        }

    async def analyze_live_matches(self) -> List[Dict]:
        """Analyze live matches with graceful fallbacks"""
        logger.info("Starting real-time analysis of live matches...")
        try:
            live_matches = await self.api_client.get_live_scores()
            if not live_matches:
                logger.info("No live matches found")
                return []

            analysis_results: List[Dict] = []
            for match in live_matches:
                try:
                    analysis = await self._analyze_single_match(match, is_live=True)
                    if analysis:
                        analysis_results.append(analysis)
                except Exception as e:
                    logger.error("Error analyzing match %s: %s", match.get("id", "unknown"), e)
                    continue

            logger.info("Completed analysis of %d live matches", len(analysis_results))
            return analysis_results

        except Exception as e:
            logger.error("Error in live matches analysis: %s", e)
            return []

    async def analyze_today_matches(self) -> List[Dict]:
        """Analyze today's matches with graceful fallbacks"""
        logger.info("Starting analysis of today's matches...")
        try:
            today_matches = await self.api_client.get_today_matches()
            if not today_matches:
                logger.info("No matches found for today")
                return []

            analysis_results: List[Dict] = []
            for match in today_matches:
                try:
                    analysis = await self._analyze_single_match(match, is_live=False)
                    if analysis:
                        analysis_results.append(analysis)
                except Exception as e:
                    logger.error("Error analyzing match %s: %s", match.get("id", "unknown"), e)
                    continue

            logger.info("Completed analysis of %d matches", len(analysis_results))
            return analysis_results

        except Exception as e:
            logger.error("Error in today's matches analysis: %s", e)
            return []

    async def _analyze_single_match(self, match: Dict, is_live: bool = False) -> Optional[Dict]:
        """Analyze a single match with comprehensive data and graceful fallbacks"""
        try:
            # Use unified API client to extract fixture ID from different API formats
            fixture_id = self.api_client.extract_fixture_id(match)
            if not fixture_id:
                # Debug the fixture structure to understand why ID extraction failed
                provider = match.get("_provider", "unknown")
                debug_info = self.api_client.debug_fixture_structure(match, provider)
                logger.warning("Match missing fixture ID. Debug info: %s", debug_info)
                return None

            # Extract basic match info
            home_team, away_team = self.api_client.extract_team_names(match)
            status = self.api_client.extract_match_status(match)
            home_score, away_score = self.api_client.extract_score(match)

            # Get detailed fixture data using the correct provider
            fixture_details = await self.api_client.safe_fixture_details(match)
            if not fixture_details:
                logger.warning("Could not get detailed data for fixture %s, using basic data", fixture_id)
                fixture_details = match

            # Initialize analysis result with basic data
            analysis: Dict = {
                "fixture_id": fixture_id,
                "home_team": home_team,
                "away_team": away_team,
                "status": status,
                "home_score": home_score,
                "away_score": away_score,
                "is_live": is_live,
                "analysis_time": datetime.now().isoformat(),
                "data_availability": {
                    "odds": False,
                    "team_form": False,
                    "expected_goals": False,
                    "predictions": False,
                    "advanced_stats": False,
                },
                "analysis_quality": "basic",
            }

            # Odds
            try:
                odds = await self.api_client.safe_match_odds(match)
                if odds:
                    analysis["odds"] = odds
                    analysis["data_availability"]["odds"] = True
                    logger.debug("Odds data retrieved for fixture %s", fixture_id)
                else:
                    logger.debug("No odds data available for fixture %s", fixture_id)
            except Exception as e:
                logger.debug("Odds data failed for fixture %s: %s", fixture_id, e)

            # Team form
            try:
                home_form, away_form = await self._get_team_form_gracefully(fixture_details)
                if home_form or away_form:
                    analysis["home_form"] = home_form
                    analysis["away_form"] = away_form
                    analysis["data_availability"]["team_form"] = True
                    logger.debug("Team form data retrieved for fixture %s", fixture_id)
                else:
                    logger.debug("No team form data available for fixture %s", fixture_id)
            except Exception as e:
                logger.debug("Team form data failed for fixture %s: %s", fixture_id, e)

            # Expected goals (xG)
            try:
                xg_data = await self.api_client.get_expected_goals(fixture_id)
                if xg_data:
                    analysis["expected_goals"] = xg_data
                    analysis["data_availability"]["expected_goals"] = True
                    logger.debug("Expected goals data retrieved for fixture %s", fixture_id)
                else:
                    logger.debug("Expected goals data not accessible for fixture %s (subscription may be required)", fixture_id)
            except Exception as e:
                logger.debug("Expected goals data failed for fixture %s: %s", fixture_id, e)

            # Predictions
            try:
                predictions = await self.api_client.safe_predictions(match)
                if predictions:
                    analysis["predictions"] = predictions
                    analysis["data_availability"]["predictions"] = True
                    logger.debug("Predictions data retrieved for fixture %s", fixture_id)
                else:
                    logger.debug("Predictions not accessible for fixture %s (subscription may be required)", fixture_id)
            except Exception as e:
                logger.debug("Predictions failed for fixture %s: %s", fixture_id, e)

            # Determine analysis quality based on available data
            available_features = sum(analysis["data_availability"].values())
            if available_features >= 4:
                analysis["analysis_quality"] = "comprehensive"
            elif available_features >= 2:
                analysis["analysis_quality"] = "moderate"
            else:
                analysis["analysis_quality"] = "basic"

            # Generate derived analysis
            analysis.update(await self._generate_comprehensive_analysis(analysis))

            logger.info(
                "Match analysis completed for %s vs %s (Quality: %s)",
                home_team,
                away_team,
                analysis["analysis_quality"],
            )
            return analysis

        except Exception as e:
            logger.error("Error in single match analysis: %s", e)
            return None

    async def _get_team_form_gracefully(self, fixture_details: Dict) -> Tuple[List[Dict], List[Dict]]:
        """Get team form data with graceful fallbacks"""
        home_form: List[Dict] = []
        away_form: List[Dict] = []
        try:
            if "participants" in fixture_details and fixture_details["participants"]:
                for participant in fixture_details["participants"]:
                    team_id = participant.get("id")
                    location = participant.get("meta", {}).get("location")
                    if team_id and location in ["home", "away"]:
                        try:
                            form_data = await self.api_client.get_team_form(team_id, limit=5)
                            if form_data:
                                if location == "home":
                                    home_form = form_data
                                else:
                                    away_form = form_data
                        except Exception as e:
                            logger.debug("Could not get form for team %s: %s", team_id, e)
        except Exception as e:
            logger.debug("Error getting team form: %s", e)
        return home_form, away_form

    async def _analyze_odds_gracefully(self, fixture_id: int) -> Dict:
        """Analyze odds with graceful fallbacks"""
        try:
            odds = await self.api_client.get_match_odds(fixture_id)
            if not odds:
                return {
                    "available": False,
                    "message": "Odds data not available",
                    "recommendations": ["Consider basic match analysis only"],
                }

            analysis: Dict = {
                "available": True,
                "total_markets": len(odds),
                "markets": [],
                "best_odds": {},
                "recommendations": [],
            }

            # Extract market information
            for odd in odds:
                market_name = odd.get("market_description", "Unknown")
                market_id = odd.get("market_id")

                existing = next((m for m in analysis["markets"] if m["name"] == market_name), None)
                if existing:
                    existing["count"] += 1
                else:
                    analysis["markets"].append({"name": market_name, "id": market_id, "count": 1})

            # Generate recommendations based on available markets
            if analysis["markets"]:
                analysis["recommendations"].append(f"Available markets: {len(analysis['markets'])}")
                names_lower = [m["name"].lower() for m in analysis["markets"]]
                if any("winner" in n for n in names_lower):
                    analysis["recommendations"].append("Match winner markets available")
                if any("btts" in n for n in names_lower):
                    analysis["recommendations"].append("Both teams to score markets available")

            return analysis

        except Exception as e:
            logger.error("Error analyzing odds: %s", e)
            return {
                "available": False,
                "message": f"Odds analysis failed: {str(e)}",
                "recommendations": ["Use basic match analysis"],
            }

    async def _analyze_team_form_gracefully(self, match: Dict) -> Dict:
        """Analyze team form with graceful fallback"""
        try:
            home_team_id = None
            away_team_id = None

            if "participants" in match and match["participants"]:
                for participant in match["participants"]:
                    loc = participant.get("meta", {}).get("location")
                    if loc == "home":
                        home_team_id = participant.get("id")
                    elif loc == "away":
                        away_team_id = participant.get("id")

            if not home_team_id or not away_team_id:
                return {
                    "form_available": False,
                    "message": "Team IDs not available",
                    "recommendation": "Basic match data available, but detailed team analysis requires subscription",
                }

            home_form = await self.api_client.get_team_form(home_team_id, 5)
            away_form = await self.api_client.get_team_form(away_team_id, 5)

            if not home_form and not away_form:
                return {
                    "form_available": False,
                    "message": "Team form data not accessible",
                    "recommendation": "Upgrade subscription for detailed team performance analysis",
                }

            return {
                "form_available": True,
                "home_team_form": self._calculate_form_score(home_form),
                "away_team_form": self._calculate_form_score(away_form),
                "home_recent_results": self._format_recent_results(home_form),
                "away_recent_results": self._format_recent_results(away_form),
                "form_comparison": self._compare_team_forms(home_form, away_form),
            }

        except Exception as e:
            logger.error("Error analyzing team form: %s", e)
            return {
                "form_available": False,
                "message": f"Error analyzing team form: {str(e)}",
                "recommendation": "Check API connection and subscription status",
            }

    async def _analyze_expected_goals_gracefully(self, fixture_id: int) -> Dict:
        """Analyze expected goals with graceful fallback"""
        try:
            xg_data = await self.api_client.get_expected_goals(fixture_id)
            if not xg_data:
                return {
                    "xg_available": False,
                    "message": "Expected goals data not accessible with current subscription",
                    "recommendation": "Upgrade to Premium plan for xG analysis and advanced statistics",
                }

            return {
                "xg_available": True,
                "home_xg": xg_data.get("home_xg", 0),
                "away_xg": xg_data.get("away_xg", 0),
                "total_xg": xg_data.get("home_xg", 0) + xg_data.get("away_xg", 0),
                "xg_confidence": xg_data.get("confidence", "Low"),
                "analysis": self._analyze_xg_implications(xg_data),
            }

        except Exception as e:
            logger.error("Error analyzing expected goals: %s", e)
            return {
                "xg_available": False,
                "message": f"Error retrieving xG data: {str(e)}",
                "recommendation": "Check API connection and subscription status",
            }

    async def _analyze_predictions_gracefully(self, fixture_id: int) -> Dict:
        """Analyze predictions with graceful fallback"""
        try:
            predictions = await self.api_client.get_predictions(fixture_id)
            if not predictions:
                return {
                    "predictions_available": False,
                    "message": "Prediction data not accessible with current subscription",
                    "recommendation": "Upgrade to Premium plan for AI-powered match predictions and value bet identification",
                }

            return {
                "predictions_available": True,
                "home_win_prob": predictions.get("home_win_probability", 0),
                "draw_prob": predictions.get("draw_probability", 0),
                "away_win_prob": predictions.get("away_win_probability", 0),
                "confidence": predictions.get("confidence", "Low"),
                "recommended_bets": predictions.get("recommended_bets", []),
                "analysis": self._analyze_prediction_implications(predictions),
            }

        except Exception as e:
            logger.error("Error analyzing predictions: %s", e)
            return {
                "predictions_available": False,
                "message": f"Error retrieving predictions: {str(e)}",
                "recommendation": "Check API connection and subscription status",
            }

    async def _generate_comprehensive_analysis(self, analysis: Dict) -> Dict:
        """Generate comprehensive analysis based on available data"""
        try:
            enhanced: Dict = {}

            # Odds
            if analysis.get("data_availability", {}).get("odds", False):
                enhanced["odds_analysis"] = await self._analyze_odds_gracefully(analysis["fixture_id"])
            else:
                enhanced["odds_analysis"] = {
                    "available": False,
                    "message": "Odds data not accessible with current subscription",
                    "recommendations": ["Upgrade subscription for odds analysis", "Use basic match analysis"],
                }

            # Form
            if analysis.get("data_availability", {}).get("team_form", False):
                home_form = analysis.get("home_form", [])
                away_form = analysis.get("away_form", [])
                form_analysis = {
                    "available": True,
                    "home_form_score": self._calculate_form_score(home_form),
                    "away_form_score": self._calculate_form_score(away_form),
                    "home_recent_results": self._format_recent_results(home_form),
                    "away_recent_results": self._format_recent_results(away_form),
                    "form_comparison": self._compare_team_forms(home_form, away_form),
                    "recommendations": [],
                }
                if form_analysis["home_form_score"] > form_analysis["away_form_score"]:
                    form_analysis["recommendations"].append("Home team in better form")
                elif form_analysis["away_form_score"] > form_analysis["home_form_score"]:
                    form_analysis["recommendations"].append("Away team in better form")
                else:
                    form_analysis["recommendations"].append("Teams in similar form")
                enhanced["form_analysis"] = form_analysis
            else:
                enhanced["form_analysis"] = {
                    "available": False,
                    "message": "Team form data not accessible",
                    "recommendations": ["Use basic match information", "Consider upgrading subscription"],
                }

            # xG
            if analysis.get("data_availability", {}).get("expected_goals", False):
                xg_data = analysis.get("expected_goals", {})
                enhanced["xg_analysis"] = {
                    "available": True,
                    "data": xg_data,
                    "implications": self._analyze_xg_implications(xg_data),
                    "recommendations": ["Use xG data for goal predictions", "Combine with other analysis"],
                }
            else:
                enhanced["xg_analysis"] = {
                    "available": False,
                    "message": "Expected goals data requires premium subscription",
                    "recommendations": ["Upgrade to premium for xG analysis", "Use available form and odds data"],
                }

            # Predictions
            if analysis.get("data_availability", {}).get("predictions", False):
                predictions = analysis.get("predictions", {})
                enhanced["predictions_analysis"] = {
                    "available": True,
                    "data": predictions,
                    "implications": self._analyze_prediction_implications(predictions),
                    "recommendations": ["Use SportMonks predictions", "Compare with your own analysis"],
                }
            else:
                enhanced["predictions_analysis"] = {
                    "available": False,
                    "message": "Predictions require premium subscription",
                    "recommendations": ["Upgrade to premium for predictions", "Use available analysis methods"],
                }

            # Value bets
            if analysis.get("data_availability", {}).get("odds", False) and analysis.get("data_availability", {}).get("predictions", False):
                enhanced["value_bets"] = self._identify_value_bets(
                    analysis.get("odds", []),
                    analysis.get("predictions", {}),
                )
            else:
                enhanced["value_bets"] = {
                    "available": False,
                    "message": "Value betting requires both odds and predictions data",
                    "recommendations": ["Upgrade subscription for comprehensive analysis", "Use available data for basic analysis"],
                }

            # Risk
            enhanced["risk_assessment"] = self._assess_risk_comprehensive(analysis)

            # Overall recs
            enhanced["overall_recommendations"] = self._get_overall_recommendations([enhanced])

            # Coverage
            enhanced["data_coverage"] = self._assess_data_coverage(analysis.get("data_availability", {}))

            return enhanced

        except Exception as e:
            logger.error("Error generating comprehensive analysis: %s", e)
            return {
                "error": f"Analysis generation failed: {str(e)}",
                "recommendations": ["Use basic match information", "Check system logs for errors"],
            }

    def _assess_data_coverage(self, data_availability: Dict) -> str:
        available_count = sum(data_availability.values())
        total_count = len(data_availability)
        if available_count == total_count:
            return "Complete data coverage"
        elif available_count >= total_count * 0.7:
            return "Good data coverage"
        elif available_count >= total_count * 0.4:
            return "Limited data coverage"
        else:
            return "Minimal data coverage"

    def _calculate_form_score(self, form_data: List[Dict]) -> float:
        if not form_data:
            return 0.0
        try:
            total_score = 0.0
            weight = 1.0
            for match in form_data[:5]:
                result = self._get_match_result(match)
                if result == "W":
                    total_score += weight * 3.0
                elif result == "D":
                    total_score += weight * 1.0
                elif result == "L":
                    total_score += weight * 0.0
                weight *= 0.8
            max_possible = sum(0.8 ** i for i in range(min(5, len(form_data)))) * 3.0
            return (total_score / max_possible * 10) if max_possible > 0 else 0.0
        except Exception as e:
            logger.error("Error calculating form score: %s", e)
            return 0.0

    def _get_match_result(self, match: Dict) -> str:
        try:
            if "scores" in match and match["scores"]:
                for score in match["scores"]:
                    if score.get("description") == "FULL_TIME":
                        home_score = score.get("score", {}).get("participant_1", 0)
                        away_score = score.get("score", {}).get("participant_2", 0)
                        if home_score > away_score:
                            return "W"
                        elif home_score < away_score:
                            return "L"
                        else:
                            return "D"
            return "U"
        except Exception as e:
            logger.error("Error getting match result: %s", e)
            return "U"

    def _format_recent_results(self, form_data: List[Dict]) -> List[str]:
        try:
            results = []
            for match in form_data[:5]:
                result = self._get_match_result(match)
                opponent = match.get("opponent", {}).get("name", "Unknown")
                prefix = {"W": "Win", "D": "Draw", "L": "Loss"}.get(result, "Unknown")
                results.append(f"{prefix} vs {opponent}")
            return results
        except Exception as e:
            logger.error("Error formatting recent results: %s", e)
            return ["Error formatting results"]

    def _compare_team_forms(self, home_form: List[Dict], away_form: List[Dict]) -> str:
        try:
            home_score = self._calculate_form_score(home_form)
            away_score = self._calculate_form_score(away_form)
            if home_score > away_score + 1.0:
                return "Home team significantly better form"
            elif away_score > home_score + 1.0:
                return "Away team significantly better form"
            elif abs(home_score - away_score) <= 1.0:
                return "Teams in similar form"
            elif home_score > away_score:
                return "Home team slightly better form"
            else:
                return "Away team slightly better form"
        except Exception as e:
            logger.error("Error comparing team forms: %s", e)
            return "Form comparison unavailable"

    def _analyze_xg_implications(self, xg_data: Dict) -> str:
        try:
            if not xg_data:
                return "No xG data available"
            home_xg = xg_data.get("home_xg", 0)
            away_xg = xg_data.get("away_xg", 0)
            if home_xg > away_xg + 0.5:
                return f"Home team expected to score more (xG: {home_xg:.2f} vs {away_xg:.2f})"
            elif away_xg > home_xg + 0.5:
                return f"Away team expected to score more (xG: {away_xg:.2f} vs {home_xg:.2f})"
            else:
                return f"Evenly matched teams (xG: {home_xg:.2f} vs {away_xg:.2f})"
        except Exception as e:
            logger.error("Error analyzing xG implications: %s", e)
            return "xG analysis unavailable"

    def _analyze_prediction_implications(self, predictions: Dict) -> str:
        try:
            if not predictions:
                return "No predictions available"
            home_win = predictions.get("home_win_probability", 0)
            draw = predictions.get("draw_probability", 0)
            away_win = predictions.get("away_win_probability", 0)
            if home_win > 0.5:
                return f"Strong home win prediction ({home_win:.1%})"
            elif away_win > 0.5:
                return f"Strong away win prediction ({away_win:.1%})"
            elif draw > 0.4:
                return f"Draw likely ({draw:.1%})"
            else:
                return f"Uncertain outcome (H: {home_win:.1%}, D: {draw:.1%}, A: {away_win:.1%})"
        except Exception as e:
            logger.error("Error analyzing predictions: %s", e)
            return "Prediction analysis unavailable"

    def _identify_value_bets(self, odds: List[Dict], predictions: Dict) -> List[Dict]:
        try:
            if not odds or not predictions:
                return []
            value_bets: List[Dict] = []
            for odd in odds:
                market_name = odd.get("market_description", "")
                try:
                    odd_value = float(odd.get("value", 0))
                except (TypeError, ValueError):
                    continue
                if odd_value <= 0:
                    continue
                implied_prob = 1.0 / odd_value
                pred_prob = self._get_prediction_probability(predictions, market_name)
                if pred_prob > 0 and implied_prob < (pred_prob - 0.1):  # 10% margin
                    value_bets.append({
                        "market": market_name,
                        "odds": odd_value,
                        "implied_probability": implied_prob,
                        "predicted_probability": pred_prob,
                        "value_margin": pred_prob - implied_prob,
                        "recommendation": "Potential value bet",
                    })
            return value_bets
        except Exception as e:
            logger.error("Error identifying value bets: %s", e)
            return []

    def _get_prediction_probability(self, predictions: Dict, market_name: str) -> float:
        try:
            market_lower = (market_name or "").lower()
            if "winner" in market_lower:
                if "home" in market_lower:
                    return predictions.get("home_win_probability", 0)
                elif "away" in market_lower:
                    return predictions.get("away_win_probability", 0)
            elif "draw" in market_lower:
                return predictions.get("draw_probability", 0)
            elif "btts" in market_lower or "both teams to score" in market_lower:
                return predictions.get("both_teams_score_probability", 0)
            return 0.0
        except Exception as e:
            logger.error("Error getting prediction probability: %s", e)
            return 0.0

    def _assess_risk_comprehensive(self, analysis: Dict) -> Dict:
        try:
            risk_factors: List[str] = []
            risk_score = 0

            if analysis.get("data_availability", {}).get("team_form", False):
                home_form = analysis.get("home_form", [])
                away_form = analysis.get("away_form", [])
                if len(home_form) < 3 or len(away_form) < 3:
                    risk_factors.append("Limited recent form data")
                    risk_score += 2
                home_consistency = self._calculate_consistency(home_form)
                away_consistency = self._calculate_consistency(away_form)
                if home_consistency < 0.6 or away_consistency < 0.6:
                    risk_factors.append("Teams showing inconsistent form")
                    risk_score += 3

            if not analysis.get("data_availability", {}).get("odds", False):
                risk_factors.append("No odds data available")
                risk_score += 2

            if not analysis.get("data_availability", {}).get("predictions", False):
                risk_factors.append("No AI predictions available")
                risk_score += 1

            risk_level = self._get_risk_level(risk_score)
            return {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "recommendation": self._get_risk_recommendation(risk_level),
            }
        except Exception as e:
            logger.error("Error in risk assessment: %s", e)
            return {
                "risk_score": 5,
                "risk_level": "HIGH",
                "risk_factors": ["Risk assessment failed"],
                "recommendation": "Proceed with caution",
            }

    def _calculate_consistency(self, form_data: List[Dict]) -> float:
        try:
            if len(form_data) < 2:
                return 0.0
            results = [self._get_match_result(match) for match in form_data]
            changes = sum(1 for i in range(1, len(results)) if results[i] != results[i - 1])
            max_changes = len(results) - 1
            consistency = 1.0 - (changes / max_changes) if max_changes > 0 else 1.0
            return consistency
        except Exception as e:
            logger.error("Error calculating consistency: %s", e)
            return 0.0

    def _get_risk_level(self, risk_score: int) -> str:
        if risk_score <= 2:
            return "LOW"
        elif risk_score <= 5:
            return "MEDIUM"
        elif risk_score <= 8:
            return "HIGH"
        else:
            return "VERY_HIGH"

    def _get_risk_recommendation(self, risk_level: str) -> str:
        recommendations = {
            "LOW": "Safe to proceed with analysis",
            "MEDIUM": "Proceed with caution, verify key data points",
            "HIGH": "High risk - consider waiting for more data or upgrading subscription",
            "VERY_HIGH": "Very high risk - not recommended without additional data",
        }
        return recommendations.get(risk_level, "Risk assessment unavailable")

    def _extract_league_info(self, match: Dict) -> Dict:
        league = match.get("league", {})
        return {
            "name": league.get("name", "Unknown League"),
            "country": league.get("country", {}).get("name", "Unknown Country"),
            "season": league.get("season", {}).get("name", "Unknown Season"),
        }

    def _extract_venue_info(self, match: Dict) -> Dict:
        venue = match.get("venue", {})
        return {
            "name": venue.get("name", "Unknown Venue"),
            "city": venue.get("city", "Unknown City"),
            "capacity": venue.get("capacity", "Unknown"),
        }

    async def get_telegram_summary(self, analysis_results: List[Dict]) -> str:
        """
        Generate a concise Telegram-ready message.
        - No emojis
        - Safe for MarkdownV2 via escaping (or send as plain text)
        - Fits under Telegram 4096 char limit
        """
        try:
            if not analysis_results:
                return "No matches available for analysis\n\nPlease check back later or verify your API configuration."

            lines: List[str] = []
            lines.append("FIXORA PRO Football Analysis")
            lines.append("")
            lines.append(f"Analysis Summary: {len(analysis_results)} matches analyzed")
            lines.append(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")

            # Subscription summary
            sub_summary = self._get_subscription_summary(analysis_results)
            lines.append(sub_summary)
            lines.append("")

            # Individual match summaries (limit to 10 to stay compact)
            for i, match in enumerate(analysis_results[:10], 1):
                lines.append(f"{i}. {self._format_match_summary(match, match.get('is_live', False))}")
                lines.append("")

            # Overall recs
            if analysis_results:
                lines.append("Overall Recommendations:")
                lines.append(self._get_overall_recommendations(analysis_results))
                lines.append("")

            # Footer
            lines.extend([
                "System Status: Real-time analysis active",
                "Updates: Live and scheduled analysis running",
                "Support: Contact admin for subscription upgrades",
            ])

            # Join and escape for MarkdownV2 if you send with parse_mode='MarkdownV2'
            body = "\n".join(lines)
            body = _escape_markdown(body)

            # Truncate to be safe for Telegram length
            return _truncate(body)

        except Exception as e:
            logger.error("Error generating Telegram summary: %s", e)
            return f"Summary Generation Error: {str(e)}"

    def _format_match_summary(self, match: Dict, is_live: bool) -> str:
        """Format a single match block without emojis, safe for Telegram."""
        try:
            home_team = match.get("home_team", "Unknown")
            away_team = match.get("away_team", "Unknown")
            status = match.get("status", "Unknown")
            quality = match.get("analysis_quality", "basic")

            summary = f"{home_team} vs {away_team}"
            if is_live:
                home_score = match.get("home_score", 0)
                away_score = match.get("away_score", 0)
                summary += f" ({home_score}-{away_score})"

            data_avail = match.get("data_availability", {})
            available_features = sum(data_avail.values())
            total_features = len(data_avail)

            summary += f"\n   Status: {status}"
            summary += f"\n   Quality: {quality.title()} ({available_features}/{total_features} features)"

            insights = []
            if data_avail.get("odds", False):
                insights.append("Odds")
            if data_avail.get("team_form", False):
                insights.append("Form")
            if data_avail.get("expected_goals", False):
                insights.append("xG")
            if data_avail.get("predictions", False):
                insights.append("AI Predictions")

            if insights:
                summary += f"\n   Available: {', '.join(insights)}"

            # Optional tip
            if "overall_recommendations" in match:
                recs = match["overall_recommendations"]
                if isinstance(recs, list) and recs:
                    summary += f"\n   Tip: {recs[0]}"
                elif isinstance(recs, str) and recs:
                    summary += f"\n   Tip: {recs[:100]}..."

            return summary

        except Exception as e:
            logger.error("Error formatting match summary: %s", e)
            return "Format Error"

    def _get_subscription_summary(self, analysis_results: List[Dict]) -> str:
        """No emojis; concise and quantitative."""
        try:
            if not analysis_results:
                return "Subscription Status: No data available"

            total_matches = len(analysis_results)
            feature_counts = {"odds": 0, "team_form": 0, "expected_goals": 0, "predictions": 0}
            for match in analysis_results:
                data_avail = match.get("data_availability", {})
                for f in feature_counts:
                    if data_avail.get(f, False):
                        feature_counts[f] += 1

            def pct(x): return (x / total_matches * 100) if total_matches > 0 else 0

            lines = [
                "Subscription Features Status:",
                f"   Total Matches: {total_matches}",
                "   Feature Availability:",
                f"      • Odds: {pct(feature_counts['odds']):.1f}% ({feature_counts['odds']}/{total_matches})",
                f"      • Team Form: {pct(feature_counts['team_form']):.1f}% ({feature_counts['team_form']}/{total_matches})",
                f"      • Expected Goals: {pct(feature_counts['expected_goals']):.1f}% ({feature_counts['expected_goals']}/{total_matches})",
                f"      • AI Predictions: {pct(feature_counts['predictions']):.1f}% ({feature_counts['predictions']}/{total_matches})",
                "   Recommendations:",
            ]

            if pct(feature_counts["odds"]) < 50:
                lines.append("      • Consider upgrading for comprehensive odds analysis")
            if pct(feature_counts["expected_goals"]) < 50:
                lines.append("      • Upgrade to Premium for xG and advanced statistics")
            if pct(feature_counts["predictions"]) < 50:
                lines.append("      • Upgrade to Premium for AI-powered predictions")
            if all(pct(feature_counts[k]) >= 80 for k in feature_counts):
                lines.append("      • Excellent data coverage - Premium features active")

            return "\n".join(lines)

        except Exception as e:
            logger.error("Error generating subscription summary: %s", e)
            return f"Subscription Summary Error: {str(e)}"

    def _get_overall_recommendations(self, analysis_results: List[Dict]) -> str:
        try:
            if not analysis_results:
                return "No analysis results available for recommendations"

            recommendations: List[str] = []

            quality_counts: Dict[str, int] = {}
            for res in analysis_results:
                q = res.get("analysis_quality", "basic")
                quality_counts[q] = quality_counts.get(q, 0) + 1

            if quality_counts.get("comprehensive", 0) > 0:
                recommendations.append("Some matches have comprehensive data - use those for detailed analysis")

            if quality_counts.get("basic", 0) > len(analysis_results) * 0.5:
                recommendations.append("Many matches have limited data - consider upgrading subscription")

            total_matches = len(analysis_results)
            feature_availability = {
                "odds": sum(1 for r in analysis_results if r.get("data_availability", {}).get("odds", False)),
                "team_form": sum(1 for r in analysis_results if r.get("data_availability", {}).get("team_form", False)),
                "expected_goals": sum(1 for r in analysis_results if r.get("data_availability", {}).get("expected_goals", False)),
                "predictions": sum(1 for r in analysis_results if r.get("data_availability", {}).get("predictions", False)),
            }

            if feature_availability["odds"] < total_matches * 0.3:
                recommendations.append("Limited odds data - upgrade for better betting analysis")
            if feature_availability["team_form"] < total_matches * 0.5:
                recommendations.append("Limited team form data - upgrade for performance analysis")
            if feature_availability["expected_goals"] < total_matches * 0.2:
                recommendations.append("Expected goals data limited - upgrade to Premium for advanced stats")
            if feature_availability["predictions"] < total_matches * 0.2:
                recommendations.append("AI predictions limited - upgrade to Premium for machine learning insights")

            if not recommendations:
                recommendations.append("Good data coverage - proceed with confidence")

            recommendations.append("System will continue monitoring and updating analysis")

            return "\n".join(recommendations)

        except Exception as e:
            logger.error("Error generating overall recommendations: %s", e)
            return "Recommendations unavailable due to error"

    async def close(self):
        try:
            await self.api_client.close()
            logger.info("RealTimeAnalyzer closed successfully")
        except Exception as e:
            logger.error("Error closing RealTimeAnalyzer: %s", e)
