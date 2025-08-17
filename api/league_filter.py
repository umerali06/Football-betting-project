#!/usr/bin/env python3
"""
League Filter Service for FIXORA PRO
Filters matches for England League 2 and up, plus top European leagues
"""

import logging
from typing import Dict, List, Optional
import config

logger = logging.getLogger(__name__)

class LeagueFilter:
    """
    Filters football matches based on league criteria
    """
    
    def __init__(self):
        self.england_leagues = config.ENGLAND_LEAGUES
        self.top_european_leagues = config.TOP_EUROPEAN_LEAGUES
        
        # League name mappings for better identification
        self.league_name_mappings = {
            39: "England - Premier League",
            40: "England - Championship", 
            41: "England - League One",
            42: "England - League Two",
            140: "Spain - La Liga",
            135: "Italy - Serie A",
            78: "Germany - Bundesliga",
            61: "France - Ligue 1",
            88: "Netherlands - Eredivisie",
            94: "Portugal - Primeira Liga",
            203: "Turkey - Super Lig",
            119: "Poland - Ekstraklasa",
            106: "Ukraine - Premier League",
            113: "Belgium - Pro League",
            197: "Czech Republic - First League"
        }
        
        # SportMonks league mappings (by name and country)
        self.sportmonks_league_mappings = {
            # England leagues
            ("FA Cup", 462): "England - FA Cup",
            ("Premier League", 86): "England - Premier League", 
            ("Championship", 86): "England - Championship",
            ("League One", 86): "England - League One",
            ("League Two", 86): "England - League Two",
            
            # German leagues
            ("DFB Pokal", 11): "Germany - DFB Pokal",
            ("Bundesliga", 11): "Germany - Bundesliga",
            
            # Other European leagues (add more as discovered)
            ("First Division", 320): "Ireland - First Division",
            ("FNL", 227): "Russia - FNL",
            ("Super League", 5618): "Switzerland - Super League"
        }
    
    def is_target_league(self, league_id: int) -> bool:
        """
        Check if a league ID is in our target leagues
        
        Args:
            league_id: League ID to check
            
        Returns:
            True if league should be included
        """
        return league_id in self.top_european_leagues
    
    def is_england_league(self, league_id: int) -> bool:
        """
        Check if a league ID is an England league
        
        Args:
            league_id: League ID to check
            
        Returns:
            True if it's an England league
        """
        return league_id in self.england_leagues
    
    def get_league_name(self, league_id: int) -> str:
        """
        Get the human-readable name for a league ID
        
        Args:
            league_id: League ID to get name for
            
        Returns:
            League name or 'Unknown League'
        """
        return self.league_name_mappings.get(league_id, f"Unknown League ({league_id})")
    
    def filter_matches_by_league(self, matches: List[Dict]) -> List[Dict]:
        """
        Filter matches to only include target leagues
        
        Args:
            matches: List of match dictionaries
            
        Returns:
            Filtered list of matches
        """
        if not matches:
            return []
        
        filtered_matches = []
        
        for match in matches:
            try:
                # Extract league ID from match data
                league_id = self._extract_league_id(match)
                
                if league_id and self.is_target_league(league_id):
                    # Add league name to match data
                    match['league_name'] = self.get_league_name(league_id)
                    filtered_matches.append(match)
                    
            except Exception as e:
                logger.warning(f"Error processing match for league filtering: {e}")
                continue
        
        logger.info(f"Filtered {len(matches)} matches to {len(filtered_matches)} target league matches")
        return filtered_matches
    
    def _extract_league_id(self, match: Dict) -> Optional[int]:
        """
        Extract league ID from match data
        
        Args:
            match: Match dictionary
            
        Returns:
            League ID or None if not found
        """
        # Try different possible locations for league ID
        league_id = None
        
        # API-Football format
        if 'league' in match and isinstance(match['league'], dict):
            league_id = match['league'].get('id')
        
        # SportMonks format
        elif 'league_id' in match:
            league_id = match['league_id']
        
        # Direct league ID
        elif 'leagueId' in match:
            league_id = match['leagueId']
        
        # Try to convert to int if found
        if league_id is not None:
            try:
                return int(league_id)
            except (ValueError, TypeError):
                logger.warning(f"Invalid league ID format: {league_id}")
                return None
        
        return None
    
    def get_league_summary(self, matches: List[Dict]) -> Dict:
        """
        Get summary of leagues represented in matches
        
        Args:
            matches: List of filtered matches
            
        Returns:
            Dictionary with league counts
        """
        league_counts = {}
        
        for match in matches:
            league_id = self._extract_league_id(match)
            if league_id:
                league_name = self.get_league_name(league_id)
                league_counts[league_name] = league_counts.get(league_name, 0) + 1
        
        return league_counts
    
    def filter_matches_by_date_range(self, matches: List[Dict], start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        Filter matches by date range (additional filtering)
        
        Args:
            matches: List of matches to filter
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Filtered list of matches
        """
        if not start_date and not end_date:
            return matches
        
        filtered_matches = []
        
        for match in matches:
            try:
                match_date = self._extract_match_date(match)
                if match_date:
                    # Check if match date is within range
                    if self._is_date_in_range(match_date, start_date, end_date):
                        filtered_matches.append(match)
                        
            except Exception as e:
                logger.warning(f"Error processing match date: {e}")
                continue
        
        return filtered_matches
    
    def _extract_match_date(self, match: Dict) -> Optional[str]:
        """Extract match date from match data"""
        # Try different date fields
        date_fields = ['date', 'match_date', 'fixture_date', 'event_date']
        
        for field in date_fields:
            if field in match and match[field]:
                return match[field]
        
        return None
    
    def _is_date_in_range(self, match_date: str, start_date: str = None, end_date: str = None) -> bool:
        """Check if match date is within specified range"""
        try:
            from datetime import datetime
            
            match_dt = datetime.strptime(match_date, '%Y-%m-%d')
            
            if start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                if match_dt < start_dt:
                    return False
            
            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                if match_dt > end_dt:
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Error parsing date {match_date}: {e}")
            return True  # Include if we can't parse date
    
    def get_filtered_matches_summary(self, all_matches: List[Dict]) -> Dict:
        """
        Get comprehensive summary of filtering results
        
        Args:
            all_matches: All available matches
            
        Returns:
            Summary dictionary
        """
        filtered_matches = self.filter_matches_by_league(all_matches)
        league_summary = self.get_league_summary(filtered_matches)
        
        # Count England vs European matches
        england_count = 0
        european_count = 0
        
        for match in filtered_matches:
            league_id = self._extract_league_id(match)
            if league_id:
                if self.is_england_league(league_id):
                    england_count += 1
                else:
                    european_count += 1
        
        return {
            'total_matches_available': len(all_matches),
            'total_matches_filtered': len(filtered_matches),
            'england_matches': england_count,
            'european_matches': european_count,
            'league_breakdown': league_summary,
            'filtering_efficiency': f"{(len(filtered_matches) / len(all_matches) * 100):.1f}%" if all_matches else "0%"
        }
