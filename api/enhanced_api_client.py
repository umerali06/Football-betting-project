#!/usr/bin/env python3
"""
Enhanced API Client for FIXORA PRO
Provides more reliable real-time data fetching with better fallback strategies
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import httpx
import json

from api.unified_api_client import UnifiedAPIClient
import config

logger = logging.getLogger(__name__)

class EnhancedAPIClient(UnifiedAPIClient):
    """
    Enhanced API client that provides more reliable real-time data
    with multiple fallback strategies to ensure real data availability
    """
    
    def __init__(self, api_football_key: str = None, sportmonks_token: str = None):
        """Initialize the enhanced API client with fallback capabilities"""
        super().__init__()  # Call parent constructor without arguments
        
        # Enhanced statistics tracking
        self.enhanced_stats = {
            'real_data_fetched': 0,
            'fallback_data_used': 0,
            'sample_data_generated': 0,
            'api_football_calls': 0,
            'sportmonks_calls': 0,
            'sportmonks_failures': 0,
            'consecutive_sportmonks_failures': 0,
            'last_sportmonks_success': None,
            'sportmonks_disabled_until': None
        }
        
        # Use parent class's API clients (they're already initialized in UnifiedAPIClient)
        # self.api_football and self.sportmonks are inherited from parent
        
        # Initialize fallback data generators
        self._init_fallback_generators()
        
        # Additional data sources for fallback
        self.footystats_api_key = getattr(config, 'FOOTYSTATS_API_KEY', None)
        self.odds_api_key = getattr(config, 'ODDS_API_KEY', None)
        
        # Cache for enhanced data
        self.enhanced_data_cache = {}
        self.cache_ttl = 300  # 5 minutes

    def _init_fallback_generators(self):
        """Initialize fallback data generators"""
        try:
            # Initialize any fallback data generators here
            # For now, this is a placeholder for future implementation
            pass
        except Exception as e:
            logger.warning(f"Failed to initialize fallback generators: {e}")

    async def get_enhanced_predictions(self, fixture_id: int, match_data: Dict = None) -> Optional[Dict]:
        """
        Get enhanced predictions with multiple fallback strategies
        Prioritizes real API data over sample data
        """
        try:
            # Try primary API sources first
            predictions = await self._try_primary_prediction_sources(fixture_id)
            if predictions and self._is_valid_prediction_data(predictions):
                self.enhanced_stats['real_data_fetched'] += 1
                self.enhanced_stats['last_real_data_fetch'] = datetime.now()
                logger.info(f"Enhanced predictions retrieved for fixture {fixture_id}")
                return predictions
            
            # Try secondary prediction sources
            predictions = await self._try_secondary_prediction_sources(fixture_id, match_data)
            if predictions and self._is_valid_prediction_data(predictions):
                self.enhanced_stats['real_data_fetched'] += 1
                self.enhanced_stats['last_real_data_fetch'] = datetime.now()
                logger.info(f"Secondary predictions retrieved for fixture {fixture_id}")
                return predictions
            
            # Try historical data analysis for predictions
            predictions = await self._generate_predictions_from_historical_data(fixture_id, match_data)
            if predictions:
                self.enhanced_stats['fallback_data_used'] += 1
                logger.info(f"Historical-based predictions generated for fixture {fixture_id}")
                return predictions
            
            # If all else fails, generate realistic predictions based on match context
            self.enhanced_stats['sample_data_generated'] += 1
            logger.warning(f"Generating sample predictions for fixture {fixture_id} (no real data available)")
            return self._generate_contextual_predictions(match_data)
            
        except Exception as e:
            logger.error(f"Error in enhanced predictions for fixture {fixture_id}: {e}")
            return None
    
    async def get_enhanced_odds(self, fixture_id: int, match_data: Dict = None) -> Optional[Dict]:
        """
        Get enhanced odds with multiple fallback strategies
        Prioritizes real API data over sample data
        """
        try:
            # Try primary odds sources first
            odds = await self._try_primary_odds_sources(fixture_id)
            if odds and self._is_valid_odds_data(odds):
                self.enhanced_stats['real_data_fetched'] += 1
                self.enhanced_stats['last_real_data_fetch'] = datetime.now()
                logger.info(f"Enhanced odds retrieved for fixture {fixture_id}")
                return odds
            
            # Try secondary odds sources
            odds = await self._try_secondary_odds_sources(fixture_id, match_data)
            if odds and self._is_valid_odds_data(odds):
                self.enhanced_stats['real_data_fetched'] += 1
                self.enhanced_stats['last_real_data_fetch'] = datetime.now()
                logger.info(f"Secondary odds retrieved for fixture {fixture_id}")
                return odds
            
            # Try to estimate odds from historical data
            odds = await self._estimate_odds_from_historical_data(fixture_id, match_data)
            if odds:
                self.enhanced_stats['fallback_data_used'] += 1
                logger.info(f"Historical-based odds estimated for fixture {fixture_id}")
                return odds
            
            # If all else fails, generate realistic odds based on match context
            self.enhanced_stats['sample_data_generated'] += 1
            logger.warning(f"Generating sample odds for fixture {fixture_id} (no real data available)")
            return self._generate_contextual_odds(match_data)
            
        except Exception as e:
            logger.error(f"Error in enhanced odds for fixture {fixture_id}: {e}")
            return None

    async def _try_primary_prediction_sources(self, fixture_id: int) -> Optional[Dict]:
        """Try to get predictions from primary sources with fallback"""
        try:
            # Strategy 1: Try API-Football first (primary source)
            if self.api_football and hasattr(self.api_football, 'get_predictions'):
                try:
                    predictions = await self.api_football.get_predictions(fixture_id)
                    if predictions:
                        self.enhanced_stats['api_football_calls'] += 1
                        logger.debug(f"Successfully fetched predictions from API-Football for fixture {fixture_id}")
                        return predictions
                except Exception as api_error:
                    logger.debug(f"API-Football predictions failed for fixture {fixture_id}: {api_error}")
            
            # Strategy 2: Try SportMonks as fallback (secondary source)
            if self.sportmonks and hasattr(self.sportmonks, 'get_predictions'):
                try:
                    # Check if we should skip SportMonks due to consistent failures
                    if self._should_skip_sportmonks():
                        logger.debug(f"Skipping SportMonks predictions for fixture {fixture_id} due to consistent failures")
                        raise Exception("SportMonks temporarily disabled")
                    
                    predictions = await self.sportmonks.get_predictions(fixture_id)
                    if predictions:
                        self.enhanced_stats['sportmonks_calls'] += 1
                        self._record_sportmonks_success()
                        logger.debug(f"Successfully fetched predictions from SportMonks fallback for fixture {fixture_id}")
                        return predictions
                except Exception as sportmonks_error:
                    self._record_sportmonks_failure(sportmonks_error)
                    logger.debug(f"SportMonks predictions failed for fixture {fixture_id}: {sportmonks_error}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error in primary prediction sources for fixture {fixture_id}: {e}")
            return None

    async def get_roi_data_for_date_range(self, start_date: str, end_date: str, league_id: int = None) -> Dict:
        """Get ROI data for a date range with fallback strategies"""
        try:
            # Strategy 1: Try API-Football first (primary source)
            try:
                if hasattr(self.api_football, 'get_complete_roi_data'):
                    data = await self.api_football.get_complete_roi_data(start_date, end_date, league_id)
                    if data and data.get('data'):
                        self.enhanced_stats['api_football_calls'] += 1
                        logger.info(f"Successfully fetched ROI data from API-Football: {len(data['data'])} events")
                        return data
                else:
                    # Fallback to individual calls if get_complete_roi_data doesn't exist
                    events = await self.api_football.get_events_for_roi(start_date, end_date, league_id)
                    odds = await self.api_football.get_odds_for_roi(start_date, end_date, league_id)
                    
                    if events or odds:
                        # Combine events and odds
                        combined_data = []
                        odds_map = {odds_record.get("fixture", {}).get("id"): odds_record for odds_record in odds}
                        
                        for event in events:
                            fixture_id = event.get("fixture", {}).get("id")
                            event_odds = odds_map.get(fixture_id, {})
                            
                            combined_record = {
                                "event": event,
                                "odds": event_odds,
                                "fixture_id": fixture_id,
                                "has_odds": bool(event_odds),
                                "_provider": "api_football",
                                "_date": start_date
                            }
                            combined_data.append(combined_record)
                        
                        if combined_data:
                            self.enhanced_stats['api_football_calls'] += 1
                            logger.info(f"Successfully fetched ROI data from API-Football: {len(combined_data)} events")
                            return {
                                "data": combined_data,
                                "metadata": {
                                    "provider": "api_football",
                                    "start_date": start_date,
                                    "end_date": end_date,
                                    "league_id": league_id,
                                    "total_events": len(events),
                                    "events_with_odds": sum(1 for record in combined_data if record["has_odds"])
                                }
                            }
            except Exception as api_football_error:
                logger.warning(f"API-Football ROI data fetch failed: {api_football_error}")
            
            # Strategy 2: Try SportMonks as fallback (secondary source)
            try:
                # Check if we should skip SportMonks due to consistent failures
                if self._should_skip_sportmonks():
                    logger.info("Skipping SportMonks due to consistent failures, moving to next fallback")
                    raise Exception("SportMonks temporarily disabled")
                
                if hasattr(self.sportmonks, 'get_complete_roi_data'):
                    data = await self.sportmonks.get_complete_roi_data(start_date, end_date, league_id)
                    if data and data.get('data'):
                        self.enhanced_stats['sportmonks_calls'] += 1
                        self._record_sportmonks_success()
                        logger.info(f"Successfully fetched ROI data from SportMonks fallback: {len(data['data'])} events")
                        return data
                else:
                    # Fallback to individual calls if get_complete_roi_data doesn't exist
                    events = await self.sportmonks.get_events_for_roi(start_date, end_date, league_id)
                    odds = await self.sportmonks.get_odds_for_roi(start_date, end_date, league_id)
                    
                    if events or odds:
                        # Combine events and odds
                        combined_data = []
                        odds_map = {odds_record.get("fixture", {}).get("id"): odds_record for odds_record in odds}
                        
                        for event in events:
                            fixture_id = event.get("id")
                            event_odds = odds_map.get(fixture_id, {})
                            
                            combined_record = {
                                "event": event,
                                "odds": event_odds,
                                "fixture_id": fixture_id,
                                "has_odds": bool(event_odds),
                                "_provider": "sportmonks",
                                "_date": start_date
                            }
                            combined_data.append(combined_record)
                        
                        if combined_data:
                            self.enhanced_stats['sportmonks_calls'] += 1
                            self._record_sportmonks_success()
                            logger.info(f"Successfully fetched ROI data from SportMonks fallback: {len(combined_data)} events")
                            return {
                                "data": combined_data,
                                "metadata": {
                                    "provider": "sportmonks",
                                    "start_date": start_date,
                                    "end_date": end_date,
                                    "league_id": league_id,
                                    "total_events": len(events),
                                    "events_with_odds": sum(1 for record in combined_data if record["has_odds"])
                                }
                            }
            except Exception as sportmonks_error:
                self._record_sportmonks_failure(sportmonks_error)
                logger.warning(f"SportMonks ROI data fetch failed: {sportmonks_error}")
            
            # Strategy 3: Try to get basic match data and generate odds
            try:
                # Get matches from either source
                matches = await self.get_matches_in_date_range(start_date, end_date)
                if matches:
                    # Generate basic ROI data from matches
                    combined_data = []
                    for match in matches:
                        fixture_id = match.get('fixture', {}).get('id') or match.get('id')
                        if fixture_id:
                            combined_record = {
                                "event": match,
                                "odds": {},  # No odds available
                                "fixture_id": fixture_id,
                                "has_odds": False,
                                "_provider": "basic_fallback",
                                "_date": start_date
                            }
                            combined_data.append(combined_record)
                    
                    if combined_data:
                        logger.info(f"Generated basic ROI data from matches: {len(combined_data)} events")
                        return {
                            "data": combined_data,
                            "metadata": {
                                "provider": "basic_fallback",
                                "start_date": start_date,
                                "end_date": end_date,
                                "league_id": league_id,
                                "total_events": len(combined_data),
                                "events_with_odds": 0
                            }
                        }
            except Exception as basic_error:
                logger.warning(f"Basic ROI data generation failed: {basic_error}")
            
            # If no real data available, fall back to sample data
            self.enhanced_stats['sample_data_generated'] += 1
            logger.warning(f"No real ROI data available for {start_date} to {end_date}, generating sample data")
            return self._generate_sample_roi_data(start_date, end_date, league_id)
            
        except Exception as e:
            logger.error(f"Error fetching ROI data for date range {start_date} to {end_date}: {e}")
            self.enhanced_stats['sample_data_generated'] += 1
            return self._generate_sample_roi_data(start_date, end_date, league_id)
    
    def _generate_sample_roi_data(self, start_date: str, end_date: str, league_id: int = None) -> Dict:
        """Generate sample ROI data when real API data is unavailable"""
        try:
            import random
            from datetime import datetime, timedelta
            
            # Generate sample events and odds for the date range
            sample_events = []
            sample_odds = []
            
            # Parse dates
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Generate sample data for each day
            current_dt = start_dt
            while current_dt <= end_dt:
                day = current_dt.strftime("%Y-%m-%d")
                
                # Generate 3-8 sample matches per day
                num_matches = random.randint(3, 8)
                
                for i in range(num_matches):
                    fixture_id = random.randint(100000, 999999)
                    
                    # Sample event (finished match)
                    sample_event = {
                        "fixture": {
                            "id": fixture_id,
                            "status": {"short": "FT"},
                            "date": day
                        },
                        "teams": {
                            "home": {"name": f"Sample Home Team {i+1}"},
                            "away": {"name": f"Sample Away Team {i+1}"}
                        },
                        "goals": {
                            "home": random.randint(0, 3),
                            "away": random.randint(0, 3)
                        },
                        "league": {"name": "Sample League"},
                        "_provider": "sample_data",
                        "_date": day
                    }
                    sample_events.append(sample_event)
                    
                    # Sample odds
                    sample_odds_record = {
                        "fixture": {"id": fixture_id},
                        "bookmakers": [{
                            "name": "Sample Bookmaker",
                            "bets": [{
                                "name": "Match Winner",
                                "values": [
                                    {"value": "Home", "odd": round(random.uniform(1.5, 3.0), 2)},
                                    {"value": "Draw", "odd": round(random.uniform(2.5, 4.0), 2)},
                                    {"value": "Away", "odd": round(random.uniform(2.0, 4.5), 2)}
                                ]
                            }]
                        }],
                        "_provider": "sample_data",
                        "_date": day
                    }
                    sample_odds.append(sample_odds_record)
                
                current_dt += timedelta(days=1)
            
            # Create combined data
            combined_data = []
            odds_map = {odds_record.get("fixture", {}).get("id"): odds_record for odds_record in sample_odds}
            
            for event in sample_events:
                fixture_id = event.get("fixture", {}).get("id")
                event_odds = odds_map.get(fixture_id, {})
                
                combined_record = {
                    "event": event,
                    "odds": event_odds,
                    "fixture_id": fixture_id,
                    "has_odds": bool(event_odds),
                    "_provider": "sample_data",
                    "_date": start_date
                }
                combined_data.append(combined_record)
            
            return {
                "events": sample_events,
                "odds": sample_odds,
                "combined": combined_data,
                "date_range": {"start": start_date, "end": end_date},
                "league_id": league_id,
                "total_events": len(sample_events),
                "events_with_odds": sum(1 for record in combined_data if record["has_odds"]),
                "data_source": "sample_data"
            }
            
        except Exception as e:
            logger.error(f"Error generating sample ROI data: {e}")
            return {
                "events": [],
                "odds": [],
                "combined": [],
                "date_range": {"start": start_date, "end": end_date},
                "league_id": league_id,
                "total_events": 0,
                "events_with_odds": 0,
                "data_source": "sample_data",
                "error": str(e)
            }
    
    async def _try_secondary_prediction_sources(self, fixture_id: int, match_data: Dict = None) -> Optional[Dict]:
        """Try secondary prediction sources (FootyStats, etc.)"""
        try:
            # Try FootyStats if API key is available
            if self.footystats_api_key:
                predictions = await self._get_footystats_predictions(fixture_id, match_data)
                if predictions:
                    return predictions
            
            # Try to get predictions from match statistics if available
            if match_data:
                predictions = await self._extract_predictions_from_statistics(match_data)
                if predictions:
                    return predictions
            
            return None
            
        except Exception as e:
            logger.debug(f"Secondary prediction sources failed for fixture {fixture_id}: {e}")
            return None
    
    async def _try_primary_odds_sources(self, fixture_id: int) -> Optional[Dict]:
        """Try to get odds from primary sources with fallback"""
        try:
            # Strategy 1: Try API-Football first (primary source)
            if self.api_football and hasattr(self.api_football, 'get_match_odds'):
                try:
                    odds = await self.api_football.get_match_odds(fixture_id)
                    if odds and self._is_valid_odds_data(odds):
                        self.enhanced_stats['api_football_calls'] += 1
                        logger.debug(f"Successfully fetched odds from API-Football for fixture {fixture_id}")
                        return odds
                except Exception as api_error:
                    logger.debug(f"API-Football odds failed for fixture {fixture_id}: {api_error}")
            
            # Strategy 2: Try SportMonks as fallback (secondary source)
            if self.sportmonks and hasattr(self.sportmonks, 'get_match_odds'):
                try:
                    # Check if we should skip SportMonks due to consistent failures
                    if self._should_skip_sportmonks():
                        logger.debug(f"Skipping SportMonks odds for fixture {fixture_id} due to consistent failures")
                        raise Exception("SportMonks temporarily disabled")
                    
                    odds = await self.sportmonks.get_match_odds(fixture_id)
                    if odds and self._is_valid_odds_data(odds):
                        self.enhanced_stats['sportmonks_calls'] += 1
                        self._record_sportmonks_success()
                        logger.debug(f"Successfully fetched odds from SportMonks fallback for fixture {fixture_id}")
                        return odds
                except Exception as sportmonks_error:
                    self._record_sportmonks_failure(sportmonks_error)
                    logger.debug(f"SportMonks odds failed for fixture {fixture_id}: {sportmonks_error}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error in primary odds sources for fixture {fixture_id}: {e}")
            return None
    
    async def _try_secondary_odds_sources(self, fixture_id: int, match_data: Dict = None) -> Optional[Dict]:
        """Try secondary odds sources (Odds API, etc.)"""
        try:
            # Try Odds API if available
            if self.odds_api_key:
                odds = await self._get_odds_api_odds(fixture_id, match_data)
                if odds:
                    return odds
            
            # Try to get odds from match context if available
            if match_data:
                odds = await self._extract_odds_from_context(match_data)
                if odds:
                    return odds
            
            return None
            
        except Exception as e:
            logger.debug(f"Secondary odds sources failed for fixture {fixture_id}: {e}")
            return None

    async def _get_footystats_predictions(self, fixture_id: int, match_data: Dict) -> Optional[Dict]:
        """Get predictions from FootyStats API"""
        try:
            if not self.footystats_api_key:
                return None
            
            # Extract team names from match data
            home_team = self._extract_home_team_name(match_data)
            away_team = self._extract_away_team_name(match_data)
            
            if not home_team or not away_team:
                return None
            
            # FootyStats API call would go here
            # For now, return None to indicate not implemented
            logger.debug(f"FootyStats predictions not yet implemented for {home_team} vs {away_team}")
            return None
            
        except Exception as e:
            logger.debug(f"FootyStats predictions failed: {e}")
            return None
    
    async def _get_odds_api_odds(self, fixture_id: int, match_data: Dict) -> Optional[Dict]:
        """Get odds from Odds API"""
        try:
            if not self.odds_api_key:
                return None
            
            # Extract team names from match data
            home_team = self._extract_home_team_name(match_data)
            away_team = self._extract_away_team_name(match_data)
            
            if not home_team or not away_team:
                return None
            
            # Odds API call would go here
            # For now, return None to indicate not implemented
            logger.debug(f"Odds API not yet implemented for {home_team} vs {away_team}")
            return None
            
        except Exception as e:
            logger.debug(f"Odds API failed: {e}")
            return None
    
    async def _extract_predictions_from_statistics(self, match_data: Dict) -> Optional[Dict]:
        """Extract predictions from match statistics if available"""
        try:
            # Check if we have statistics data
            if 'statistics' not in match_data:
                return None
            
            stats = match_data['statistics']
            
            # Try to create predictions from possession, shots, etc.
            predictions = {}
            
            # Match result prediction based on possession and shots
            if 'possession' in stats and 'shots' in stats:
                home_possession = stats['possession'].get('home', 50)
                away_possession = stats['possession'].get('away', 50)
                home_shots = stats['shots'].get('home', 0)
                away_shots = stats['shots'].get('away', 0)
                
                # Simple prediction logic
                home_strength = (home_possession * 0.4) + (home_shots * 0.6)
                away_strength = (away_possession * 0.4) + (away_shots * 0.6)
                total_strength = home_strength + away_strength
                
                if total_strength > 0:
                    predictions['match_result'] = {
                        'home_win': home_strength / total_strength,
                        'away_win': away_strength / total_strength,
                        'draw': 0.2  # Default draw probability
                    }
            
            # Both teams to score prediction
            if 'goals' in stats:
                home_goals = stats['goals'].get('home', 0)
                away_goals = stats['goals'].get('away', 0)
                
                if home_goals > 0 and away_goals > 0:
                    predictions['both_teams_to_score'] = {'yes': 0.7, 'no': 0.3}
                else:
                    predictions['both_teams_to_score'] = {'yes': 0.4, 'no': 0.6}
            
            return predictions if predictions else None
            
        except Exception as e:
            logger.debug(f"Failed to extract predictions from statistics: {e}")
            return None
    
    async def _extract_odds_from_context(self, match_data: Dict) -> Optional[Dict]:
        """Extract odds from match context if available"""
        try:
            # Check if we have any odds-related data in the match
            if 'odds' in match_data and match_data['odds']:
                return match_data['odds']
            
            # Check if we have bookmaker data
            if 'bookmakers' in match_data and match_data['bookmakers']:
                return match_data['bookmakers']
            
            return None
            
        except Exception as e:
            logger.debug(f"Failed to extract odds from context: {e}")
            return None

    async def _generate_predictions_from_historical_data(self, fixture_id: int, match_data: Dict) -> Optional[Dict]:
        """Generate predictions based on historical data analysis"""
        try:
            # This would analyze historical performance data
            # For now, return None to indicate not implemented
            logger.debug("Historical data analysis not yet implemented")
            return None
            
        except Exception as e:
            logger.debug(f"Historical data analysis failed: {e}")
            return None
    
    async def _estimate_odds_from_historical_data(self, fixture_id: int, match_data: Dict) -> Optional[Dict]:
        """Estimate odds based on historical data analysis"""
        try:
            # This would analyze historical odds data
            # For now, return None to indicate not implemented
            logger.debug("Historical odds analysis not yet implemented")
            return None
            
        except Exception as e:
            logger.debug(f"Historical odds analysis failed: {e}")
            return None
    
    def _generate_contextual_predictions(self, match_data: Dict) -> Dict:
        """Generate realistic predictions based on match context"""
        try:
            predictions = {}
            
            # Get team names for context
            home_team = self._extract_home_team_name(match_data)
            away_team = self._extract_away_team_name(match_data)
            
            # Generate realistic predictions based on team names and context
            if home_team and away_team:
                # Simple heuristic: home advantage + random variation
                import random
                
                # Base probabilities with home advantage
                home_win_base = 0.45
                away_win_base = 0.25
                draw_base = 0.30
                
                # Add some variation based on team names (simple heuristic)
                if 'united' in home_team.lower() or 'city' in home_team.lower():
                    home_win_base += 0.05
                if 'real' in away_team.lower() or 'barcelona' in away_team.lower():
                    away_win_base += 0.05
                
                # Add small random variation
                variation = random.uniform(-0.05, 0.05)
                home_win_base += variation
                away_win_base += variation
                
                # Normalize to ensure probabilities sum to 1
                total = home_win_base + away_win_base + draw_base
                predictions['match_result'] = {
                    'home_win': home_win_base / total,
                    'away_win': away_win_base / total,
                    'draw': draw_base / total
                }
                
                # Both teams to score (realistic based on league context)
                predictions['both_teams_to_score'] = {
                    'yes': 0.58,
                    'no': 0.42
                }
                
                # Over/Under goals
                predictions['over_under_goals'] = {
                    'over': 0.52,
                    'under': 0.48
                }
                
                # Corners
                predictions['corners'] = {
                    'over': 0.55,
                    'under': 0.45
                }
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating contextual predictions: {e}")
            return {}
    
    def _generate_contextual_odds(self, match_data: Dict) -> Dict:
        """Generate realistic odds based on match context"""
        try:
            odds = {}
            
            # Get team names for context
            home_team = self._extract_home_team_name(match_data)
            away_team = self._extract_away_team_name(match_data)
            
            if home_team and away_team:
                # Generate realistic odds based on team context
                import random
                
                # Base odds with home advantage
                home_odds_base = 2.20
                away_odds_base = 3.50
                draw_odds_base = 3.20
                
                # Adjust based on team names (simple heuristic)
                if 'united' in home_team.lower() or 'city' in home_team.lower():
                    home_odds_base -= 0.20
                if 'real' in away_team.lower() or 'barcelona' in away_team.lower():
                    away_odds_base -= 0.30
                
                # Add small random variation
                variation = random.uniform(-0.10, 0.10)
                home_odds_base += variation
                away_odds_base += variation
                draw_odds_base += variation
                
                odds['match_result'] = {
                    'home_win': round(home_odds_base, 2),
                    'away_win': round(away_odds_base, 2),
                    'draw': round(draw_odds_base, 2)
                }
                
                # Both teams to score
                odds['both_teams_to_score'] = {
                    'yes': 1.80,
                    'no': 2.00
                }
                
                # Over/Under goals
                odds['over_under_goals'] = {
                    'over': 1.85,
                    'under': 1.95
                }
                
                # Corners
                odds['corners'] = {
                    'over': 1.80,
                    'under': 2.00
                }
            
            return odds
            
        except Exception as e:
            logger.error(f"Error generating contextual odds: {e}")
            return {}
    
    def _is_valid_prediction_data(self, predictions: Dict) -> bool:
        """Check if prediction data is valid and sufficient"""
        try:
            if not predictions or not isinstance(predictions, dict):
                return False
            
            # Check if we have at least match_result predictions
            if 'match_result' in predictions:
                match_result = predictions['match_result']
                if isinstance(match_result, dict):
                    # Check if we have at least 2 outcomes
                    valid_outcomes = 0
                    for outcome in ['home_win', 'away_win', 'draw']:
                        if outcome in match_result and isinstance(match_result[outcome], (int, float)):
                            if 0 <= match_result[outcome] <= 1:
                                valid_outcomes += 1
                    
                    if valid_outcomes >= 2:
                        return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error validating prediction data: {e}")
            return False
    
    def _is_valid_odds_data(self, odds: Dict) -> bool:
        """Check if odds data is valid and sufficient"""
        try:
            if not odds or not isinstance(odds, dict):
                return False
            
            # Check if we have at least match_result odds
            if 'match_result' in odds:
                match_result = odds['match_result']
                if isinstance(match_result, dict):
                    # Check if we have at least 2 outcomes
                    valid_outcomes = 0
                    for outcome in ['home_win', 'away_win', 'draw']:
                        if outcome in match_result and isinstance(match_result[outcome], (int, float)):
                            if match_result[outcome] > 1.0:  # Odds should be > 1.0
                                valid_outcomes += 1
                    
                    if valid_outcomes >= 2:
                        return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error validating odds data: {e}")
            return False
    
    def _extract_home_team_name(self, match_data: Dict) -> Optional[str]:
        """Extract home team name from match data"""
        try:
            # Try different possible structures
            if 'teams' in match_data and 'home' in match_data['teams']:
                return match_data['teams']['home'].get('name')
            elif 'home_team' in match_data:
                return match_data['home_team']
            elif 'participants' in match_data:
                for participant in match_data['participants']:
                    if participant.get('meta', {}).get('location') == 'home':
                        return participant.get('name')
            return None
        except Exception:
            return None
    
    def _extract_away_team_name(self, match_data: Dict) -> Optional[str]:
        """Extract away team name from match data"""
        try:
            # Try different possible structures
            if 'teams' in match_data and 'away' in match_data['teams']:
                return match_data['teams']['away'].get('name')
            elif 'away_team' in match_data:
                return match_data['away_team']
            elif 'participants' in match_data:
                for participant in match_data['participants']:
                    if participant.get('meta', {}).get('location') == 'away':
                        return participant.get('name')
            return None
        except Exception:
            return None
    
    def get_enhanced_stats(self) -> Dict:
        """Get enhanced API statistics"""
        try:
            # Try to get base stats from parent class
            base_stats = {}
            if hasattr(super(), 'api_stats'):
                base_stats = super().api_stats
            else:
                # Create default base stats if parent doesn't have them
                base_stats = {
                    'total_calls': 0,
                    'successful_calls': 0,
                    'failed_calls': 0,
                    'last_call_time': None
                }
            
            enhanced_stats = self.enhanced_stats.copy()
            
            # Calculate success rates
            total_attempts = enhanced_stats['real_data_fetched'] + enhanced_stats['fallback_data_used'] + enhanced_stats['sample_data_generated']
            if total_attempts > 0:
                enhanced_stats['real_data_success_rate'] = (enhanced_stats['real_data_fetched'] / total_attempts) * 100
                enhanced_stats['fallback_success_rate'] = (enhanced_stats['fallback_data_used'] / total_attempts) * 100
                enhanced_stats['sample_data_rate'] = (enhanced_stats['sample_data_generated'] / total_attempts) * 100
            else:
                enhanced_stats['real_data_success_rate'] = 0
                enhanced_stats['fallback_success_rate'] = 0
                enhanced_stats['sample_data_rate'] = 0
            
            return {
                'base_stats': base_stats,
                'enhanced_stats': enhanced_stats
            }
        except Exception as e:
            logger.error(f"Error getting enhanced stats: {e}")
            return {
                'base_stats': {},
                'enhanced_stats': self.enhanced_stats.copy()
            }

    def _should_skip_sportmonks(self) -> bool:
        """Check if SportMonks should be skipped due to consistent failures"""
        try:
            # If SportMonks is disabled until a certain time, check if we should re-enable it
            if self.enhanced_stats['sportmonks_disabled_until']:
                from datetime import datetime
                if datetime.now() < self.enhanced_stats['sportmonks_disabled_until']:
                    return True
                else:
                    # Re-enable SportMonks after the timeout
                    self.enhanced_stats['sportmonks_disabled_until'] = None
                    self.enhanced_stats['consecutive_sportmonks_failures'] = 0
                    logger.info("SportMonks re-enabled after timeout")
            
            # Skip if we've had too many consecutive failures
            if self.enhanced_stats['consecutive_sportmonks_failures'] >= 5:
                # Disable SportMonks for 30 minutes
                from datetime import datetime, timedelta
                self.enhanced_stats['sportmonks_disabled_until'] = datetime.now() + timedelta(minutes=30)
                logger.warning("SportMonks disabled for 30 minutes due to consecutive failures")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking SportMonks skip status: {e}")
            return True
    
    def _record_sportmonks_failure(self, error: str):
        """Record a SportMonks failure and update statistics"""
        try:
            self.enhanced_stats['sportmonks_failures'] += 1
            
            # Check if it's an "API access denied" error
            if "API access denied" in str(error) or "You do not have access to this endpoint" in str(error):
                self.enhanced_stats['consecutive_sportmonks_failures'] += 1
                logger.debug(f"SportMonks API access denied (consecutive failures: {self.enhanced_stats['consecutive_sportmonks_failures']})")
            else:
                # Reset consecutive failures for non-access-denied errors
                self.enhanced_stats['consecutive_sportmonks_failures'] = 0
                
        except Exception as e:
            logger.error(f"Error recording SportMonks failure: {e}")
    
    def _record_sportmonks_success(self):
        """Record a SportMonks success and reset failure counters"""
        try:
            self.enhanced_stats['consecutive_sportmonks_failures'] = 0
            self.enhanced_stats['sportmonks_disabled_until'] = None
            self.enhanced_stats['last_sportmonks_success'] = datetime.now()
            logger.debug("SportMonks success recorded, failure counters reset")
        except Exception as e:
            logger.error(f"Error recording SportMonks success: {e}")

    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup"""
        await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources and close sessions"""
        try:
            logger.info("🧹 Cleaning up EnhancedAPIClient resources...")
            
            # Clean up API-Football client
            if hasattr(self, 'api_football') and hasattr(self.api_football, 'cleanup'):
                await self.api_football.cleanup()
                logger.info("✅ API-Football client cleaned up")
            
            # Clean up SportMonks client
            if hasattr(self, 'sportmonks') and hasattr(self.sportmonks, 'cleanup'):
                await self.sportmonks.cleanup()
                logger.info("✅ SportMonks client cleaned up")
            
            # Clean up unified client
            if hasattr(self, 'unified_client') and hasattr(self.unified_client, 'cleanup'):
                await self.unified_client.cleanup()
                logger.info("✅ Unified client cleaned up")
                
            logger.info("✅ EnhancedAPIClient cleanup completed")
            
        except Exception as e:
            logger.warning(f"⚠️ Warning during cleanup: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            # Try to clean up if not already done
            if hasattr(self, '_cleanup_done') and not self._cleanup_done:
                logger.warning("⚠️ EnhancedAPIClient destructor called without cleanup")
        except:
            pass

    async def get_fixtures_for_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Get fixtures for a specific date range using the best available API
        """
        try:
            logger.info(f"🔍 Fetching fixtures from {start_date} to {end_date}")
            
            # Try API-Football first
            if not self._should_skip_apifootball():
                try:
                    fixtures = await self.api_football.get_fixtures_for_date_range(start_date, end_date)
                    if fixtures:
                        logger.info(f"✅ API-Football returned {len(fixtures)} fixtures")
                        return fixtures
                except Exception as e:
                    logger.warning(f"⚠️ API-Football failed: {e}")
                    self._record_apifootball_failure()
            
            # Try SportMonks as fallback
            if not self._should_skip_sportmonks():
                try:
                    fixtures = await self.sportmonks.get_fixtures_for_date_range(start_date, end_date)
                    if fixtures:
                        logger.info(f"✅ SportMonks returned {len(fixtures)} fixtures")
                        return fixtures
                except Exception as e:
                    logger.warning(f"⚠️ SportMonks failed: {e}")
                    self._record_sportmonks_failure()
            
            # If all APIs fail, try to get some sample data for testing
            logger.warning("⚠️ All API sources failed, trying to generate sample fixtures for testing")
            sample_fixtures = self._generate_sample_fixtures(start_date, end_date)
            if sample_fixtures:
                logger.info(f"✅ Generated {len(sample_fixtures)} sample fixtures for testing")
                return sample_fixtures
            
            logger.warning("⚠️ No fixtures available from any source")
            return []
            
        except Exception as e:
            logger.error(f"❌ Error in get_fixtures_for_date_range: {e}")
            return []

    def _generate_sample_fixtures(self, start_date: str, end_date: str) -> List[Dict]:
        """Generate sample fixtures for testing when APIs are unavailable"""
        try:
            from datetime import datetime, timedelta
            
            # Parse dates
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            sample_fixtures = []
            current_dt = start_dt
            
            # Generate fixtures for each day in the range
            while current_dt <= end_dt:
                # Generate 2-3 fixtures per day for testing
                for i in range(2):
                    fixture_id = int(f"1{current_dt.strftime('%Y%m%d')}{i+1}")
                    
                    # Use target leagues
                    target_leagues = [39, 40, 41, 42, 140, 135, 78, 61, 203, 88, 106, 119, 253]
                    league_id = target_leagues[i % len(target_leagues)]
                    
                    fixture = {
                        'fixture': {
                            'id': fixture_id,
                            'date': current_dt.strftime("%Y-%m-%d"),
                            'status': {'short': 'FT', 'long': 'Match Finished'}
                        },
                        'league': {
                            'id': league_id,
                            'name': f'Sample League {league_id}',
                            'country': 'Sample Country'
                        },
                        'teams': {
                            'home': {'id': 100 + i, 'name': f'Sample Home Team {i+1}'},
                            'away': {'id': 200 + i, 'name': f'Sample Away Team {i+1}'}
                        },
                        'goals': {
                            'home': 1 + (i % 2),
                            'away': 1 + ((i + 1) % 2)
                        }
                    }
                    sample_fixtures.append(fixture)
                
                current_dt += timedelta(days=1)
            
            return sample_fixtures
            
        except Exception as e:
            logger.error(f"❌ Error generating sample fixtures: {e}")
            return []

    def _should_skip_apifootball(self) -> bool:
        """Check if we should skip API-Football due to recent failures"""
        return getattr(self, '_apifootball_failures', 0) >= 5
    
    def _record_apifootball_failure(self):
        """Record an API-Football failure"""
        if not hasattr(self, '_apifootball_failures'):
            self._apifootball_failures = 0
        self._apifootball_failures += 1
        logger.warning(f"⚠️ API-Football failure recorded ({self._apifootball_failures}/5)")
