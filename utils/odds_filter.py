#!/usr/bin/env python3
"""
Centralized odds filtering utilities for FIXORA PRO
Ensures consistent odds validation across all modules
"""

import logging
import config
from typing import Dict, List, Union, Optional

logger = logging.getLogger(__name__)

class OddsFilter:
    """Centralized odds filtering and validation"""
    
    @staticmethod
    def validate_odds(odds: Union[int, float, str]) -> bool:
        """
        Validate that odds meet minimum requirements (≥1.8)
        
        Args:
            odds: Odds value to validate
            
        Returns:
            bool: True if odds are valid, False otherwise
        """
        try:
            # Convert to float if string
            if isinstance(odds, str):
                odds = float(odds)
            
            # Type check
            if not isinstance(odds, (int, float)):
                logger.warning(f"Invalid odds type: {type(odds)} for value {odds}")
                return False
            
            # Range validation
            if odds < config.MIN_ODDS:
                logger.debug(f"Odds {odds:.2f} below minimum requirement {config.MIN_ODDS}")
                return False
            
            if odds > config.MAX_ODDS:
                logger.debug(f"Odds {odds:.2f} above maximum requirement {config.MAX_ODDS}")
                return False
            
            return True
            
        except (ValueError, TypeError) as e:
            logger.debug(f"Failed to validate odds {odds}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error validating odds {odds}: {e}")
            return False
    
    @staticmethod
    def filter_odds_dict(odds_dict: Dict[str, Union[int, float, str]]) -> Dict[str, float]:
        """
        Filter odds dictionary to only include valid odds
        
        Args:
            odds_dict: Dictionary of market -> odds mappings
            
        Returns:
            Dict[str, float]: Filtered dictionary with only valid odds
        """
        filtered_odds = {}
        
        for market, odds in odds_dict.items():
            if OddsFilter.validate_odds(odds):
                # Convert to float for consistency
                filtered_odds[market] = float(odds)
                logger.debug(f"Accepted odds for {market}: {odds}")
            else:
                logger.debug(f"Rejected odds for {market}: {odds} (failed validation)")
        
        return filtered_odds
    
    @staticmethod
    def filter_value_bets(value_bets: List[Dict]) -> List[Dict]:
        """
        Filter value bets to only include those with valid odds
        
        Args:
            value_bets: List of value bet dictionaries
            
        Returns:
            List[Dict]: Filtered list with only valid odds
        """
        filtered_bets = []
        
        for bet in value_bets:
            odds = bet.get('odds')
            if OddsFilter.validate_odds(odds):
                filtered_bets.append(bet)
                logger.debug(f"Accepted value bet with odds {odds}")
            else:
                logger.debug(f"Rejected value bet with odds {odds} (failed validation)")
        
        logger.info(f"Filtered {len(value_bets)} value bets to {len(filtered_bets)} with valid odds")
        return filtered_bets
    
    @staticmethod
    def get_odds_summary(odds_dict: Dict[str, Union[int, float, str]]) -> Dict[str, Union[int, float]]:
        """
        Get summary statistics for odds
        
        Args:
            odds_dict: Dictionary of market -> odds mappings
            
        Returns:
            Dict: Summary statistics
        """
        valid_odds = []
        invalid_odds = []
        
        for market, odds in odds_dict.items():
            if OddsFilter.validate_odds(odds):
                valid_odds.append(float(odds))
            else:
                invalid_odds.append(odds)
        
        summary = {
            'total_markets': len(odds_dict),
            'valid_markets': len(valid_odds),
            'invalid_markets': len(invalid_odds),
            'min_valid_odds': min(valid_odds) if valid_odds else None,
            'max_valid_odds': max(valid_odds) if valid_odds else None,
            'rejected_odds': invalid_odds
        }
        
        return summary
    
    @staticmethod
    def log_odds_validation_summary(odds_dict: Dict[str, Union[int, float, str]], context: str = ""):
        """
        Log a summary of odds validation results
        
        Args:
            odds_dict: Dictionary of market -> odds mappings
            context: Context string for logging
        """
        summary = OddsFilter.get_odds_summary(odds_dict)
        
        context_str = f" [{context}]" if context else ""
        
        logger.info(f"Odds validation summary{context_str}:")
        logger.info(f"  Total markets: {summary['total_markets']}")
        logger.info(f"  Valid odds: {summary['valid_markets']}")
        logger.info(f"  Invalid odds: {summary['invalid_markets']}")
        
        if summary['min_valid_odds'] is not None:
            logger.info(f"  Valid odds range: {summary['min_valid_odds']:.2f} - {summary['max_valid_odds']:.2f}")
        
        if summary['rejected_odds']:
            logger.info(f"  Rejected odds: {summary['rejected_odds']}")

# Convenience functions for backward compatibility
def validate_odds(odds: Union[int, float, str]) -> bool:
    """Convenience function for odds validation"""
    return OddsFilter.validate_odds(odds)

def filter_odds_dict(odds_dict: Dict[str, Union[int, float, str]]) -> Dict[str, float]:
    """Convenience function for filtering odds dictionary"""
    return OddsFilter.filter_odds_dict(odds_dict)

def filter_value_bets(value_bets: List[Dict]) -> List[Dict]:
    """Convenience function for filtering value bets"""
    return OddsFilter.filter_value_bets(value_bets)
