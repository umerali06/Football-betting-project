#!/usr/bin/env python3
"""
Data Ingestion and ETL for FIXORA PRO
Handles match stats, fixtures, lineups, and odds data
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import config

logger = logging.getLogger(__name__)

class DataIngestion:
    """
    Handles data ingestion from various sources and ETL processing
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_FILE
        self.init_database()
    
    def init_database(self):
        """Initialize the database with ETL tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create cleaned match data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cleaned_match_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fixture_id INTEGER NOT NULL,
                    league_id INTEGER NOT NULL,
                    league_name TEXT NOT NULL,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    match_date TEXT NOT NULL,
                    home_possession REAL,
                    away_possession REAL,
                    home_pass_accuracy REAL,
                    away_pass_accuracy REAL,
                    home_crosses INTEGER,
                    away_crosses INTEGER,
                    home_clearances INTEGER,
                    away_clearances INTEGER,
                    home_tackles INTEGER,
                    away_tackles INTEGER,
                    home_fouls INTEGER,
                    away_fouls INTEGER,
                    home_long_balls INTEGER,
                    away_long_balls INTEGER,
                    home_aerials INTEGER,
                    away_aerials INTEGER,
                    referee TEXT,
                    weather TEXT,
                    home_goals INTEGER,
                    away_goals INTEGER,
                    home_shots INTEGER,
                    away_shots INTEGER,
                    home_shots_on_target INTEGER,
                    away_shots_on_target INTEGER,
                    home_corners INTEGER,
                    away_corners INTEGER,
                    home_yellow_cards INTEGER,
                    away_yellow_cards INTEGER,
                    home_red_cards INTEGER,
                    away_red_cards INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create cleaned odds data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cleaned_odds_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fixture_id INTEGER NOT NULL,
                    market_type TEXT NOT NULL,
                    selection TEXT NOT NULL,
                    odds REAL NOT NULL,
                    bookmaker TEXT NOT NULL,
                    line_moves TEXT,
                    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create cleaned fixtures table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cleaned_fixtures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fixture_id INTEGER NOT NULL,
                    league_id INTEGER NOT NULL,
                    league_name TEXT NOT NULL,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    match_date TEXT NOT NULL,
                    kickoff_time TEXT NOT NULL,
                    venue TEXT,
                    home_formation TEXT,
                    away_formation TEXT,
                    home_starting_xi TEXT,
                    away_starting_xi TEXT,
                    home_substitutes TEXT,
                    away_substitutes TEXT,
                    home_manager TEXT,
                    away_manager TEXT,
                    status TEXT DEFAULT 'scheduled',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("ETL database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ETL database: {e}")
    
    def load_sample_data(self) -> Dict:
        """Load sample data for testing (stub implementation)"""
        sample_data = {
            'match_stats': [
                {
                    'fixture_id': 1,
                    'league_id': 39,
                    'league_name': 'English Premier League',
                    'home_team': 'Manchester City',
                    'away_team': 'Arsenal',
                    'match_date': '2024-08-24',
                    'home_possession': 65.2,
                    'away_possession': 34.8,
                    'home_pass_accuracy': 89.1,
                    'away_pass_accuracy': 82.3,
                    'home_crosses': 12,
                    'away_crosses': 8,
                    'home_clearances': 15,
                    'away_clearances': 22,
                    'home_tackles': 18,
                    'away_tackles': 24,
                    'home_fouls': 8,
                    'away_fouls': 12,
                    'home_long_balls': 5,
                    'away_long_balls': 9,
                    'home_aerials': 7,
                    'away_aerials': 11,
                    'referee': 'Michael Oliver',
                    'weather': 'Clear',
                    'home_goals': 3,
                    'away_goals': 1,
                    'home_shots': 18,
                    'away_shots': 9,
                    'home_shots_on_target': 8,
                    'away_shots_on_target': 4,
                    'home_corners': 8,
                    'away_corners': 5,
                    'home_yellow_cards': 2,
                    'away_yellow_cards': 3,
                    'home_red_cards': 0,
                    'away_red_cards': 0
                }
            ],
            'odds': [
                {
                    'fixture_id': 1,
                    'market_type': 'match_result',
                    'selection': 'home_win',
                    'odds': 1.85,
                    'bookmaker': 'Bet365',
                    'line_moves': 'Opening: 1.90, Current: 1.85'
                },
                {
                    'fixture_id': 1,
                    'market_type': 'match_result',
                    'selection': 'draw',
                    'odds': 3.50,
                    'bookmaker': 'Bet365',
                    'line_moves': 'Opening: 3.60, Current: 3.50'
                },
                {
                    'fixture_id': 1,
                    'market_type': 'match_result',
                    'selection': 'away_win',
                    'odds': 4.20,
                    'bookmaker': 'Bet365',
                    'line_moves': 'Opening: 4.10, Current: 4.20'
                }
            ],
            'fixtures': [
                {
                    'fixture_id': 1,
                    'league_id': 39,
                    'league_name': 'English Premier League',
                    'home_team': 'Manchester City',
                    'away_team': 'Arsenal',
                    'match_date': '2024-08-24',
                    'kickoff_time': '15:00',
                    'venue': 'Etihad Stadium',
                    'home_formation': '4-3-3',
                    'away_formation': '4-2-3-1',
                    'home_starting_xi': 'Ederson, Walker, Dias, Stones, Ake, Rodri, De Bruyne, Silva, Foden, Haaland, Grealish',
                    'away_starting_xi': 'Raya, White, Saliba, Gabriel, Zinchenko, Partey, Rice, Saka, Odegaard, Martinelli, Jesus',
                    'home_substitutes': 'Ortega, Akanji, Laporte, Phillips, Palmer, Alvarez, Doku',
                    'away_substitutes': 'Hein, Tomiyasu, Kiwior, Jorginho, Smith Rowe, Trossard, Nketiah',
                    'home_manager': 'Pep Guardiola',
                    'away_manager': 'Mikel Arteta',
                    'status': 'scheduled'
                }
            ]
        }
        
        return sample_data
    
    def clean_and_store(self, data: Dict) -> bool:
        """
        Clean and store data in the database
        
        Args:
            data: Dictionary containing match_stats, odds, and fixtures
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store cleaned match stats
            if 'match_stats' in data:
                for stat in data['match_stats']:
                    cursor.execute('''
                        INSERT INTO cleaned_match_data (
                            fixture_id, league_id, league_name, home_team, away_team,
                            match_date, home_possession, away_possession, home_pass_accuracy,
                            away_pass_accuracy, home_crosses, away_crosses, home_clearances,
                            away_clearances, home_tackles, away_tackles, home_fouls,
                            away_fouls, home_long_balls, away_long_balls, home_aerials,
                            away_aerials, referee, weather, home_goals, away_goals,
                            home_shots, away_shots, home_shots_on_target, away_shots_on_target,
                            home_corners, away_corners, home_yellow_cards, away_yellow_cards,
                            home_red_cards, away_red_cards
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        stat['fixture_id'], stat['league_id'], stat['league_name'],
                        stat['home_team'], stat['away_team'], stat['match_date'],
                        stat['home_possession'], stat['away_possession'],
                        stat['home_pass_accuracy'], stat['away_pass_accuracy'],
                        stat['home_crosses'], stat['away_crosses'],
                        stat['home_clearances'], stat['away_clearances'],
                        stat['home_tackles'], stat['away_tackles'],
                        stat['home_fouls'], stat['away_fouls'],
                        stat['home_long_balls'], stat['away_long_balls'],
                        stat['home_aerials'], stat['away_aerials'],
                        stat['referee'], stat['weather'],
                        stat['home_goals'], stat['away_goals'],
                        stat['home_shots'], stat['away_shots'],
                        stat['home_shots_on_target'], stat['away_shots_on_target'],
                        stat['home_corners'], stat['away_corners'],
                        stat['home_yellow_cards'], stat['away_yellow_cards'],
                        stat['home_red_cards'], stat['away_red_cards']
                    ))
            
            # Store cleaned odds data
            if 'odds' in data:
                for odd in data['odds']:
                    cursor.execute('''
                        INSERT INTO cleaned_odds_data (
                            fixture_id, market_type, selection, odds, bookmaker, line_moves
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        odd['fixture_id'], odd['market_type'], odd['selection'],
                        odd['odds'], odd['bookmaker'], odd['line_moves']
                    ))
            
            # Store cleaned fixtures
            if 'fixtures' in data:
                for fixture in data['fixtures']:
                    cursor.execute('''
                        INSERT INTO cleaned_fixtures (
                            fixture_id, league_id, league_name, home_team, away_team,
                            match_date, kickoff_time, venue, home_formation, away_formation,
                            home_starting_xi, away_starting_xi, home_substitutes,
                            away_substitutes, home_manager, away_manager, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        fixture['fixture_id'], fixture['league_id'], fixture['league_name'],
                        fixture['home_team'], fixture['away_team'], fixture['match_date'],
                        fixture['kickoff_time'], fixture['venue'], fixture['home_formation'],
                        fixture['away_formation'], fixture['home_starting_xi'],
                        fixture['away_starting_xi'], fixture['home_substitutes'],
                        fixture['away_substitutes'], fixture['home_manager'],
                        fixture['away_manager'], fixture['status']
                    ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Successfully stored {len(data.get('match_stats', []))} match stats, "
                       f"{len(data.get('odds', []))} odds records, and "
                       f"{len(data.get('fixtures', []))} fixtures")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clean and store data: {e}")
            return False
    
    def get_cleaned_data(self, fixture_id: int = None) -> Dict:
        """Retrieve cleaned data from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            result = {}
            
            # Get match stats
            if fixture_id:
                cursor.execute('SELECT * FROM cleaned_match_data WHERE fixture_id = ?', (fixture_id,))
            else:
                cursor.execute('SELECT * FROM cleaned_match_data ORDER BY match_date DESC LIMIT 100')
            
            match_stats = cursor.fetchall()
            if match_stats:
                columns = [description[0] for description in cursor.description]
                result['match_stats'] = [dict(zip(columns, row)) for row in match_stats]
            
            # Get odds data
            if fixture_id:
                cursor.execute('SELECT * FROM cleaned_odds_data WHERE fixture_id = ?', (fixture_id,))
            else:
                cursor.execute('SELECT * FROM cleaned_odds_data ORDER BY last_updated DESC LIMIT 100')
            
            odds_data = cursor.fetchall()
            if odds_data:
                columns = [description[0] for description in cursor.description]
                result['odds'] = [dict(zip(columns, row)) for row in odds_data]
            
            # Get fixtures
            if fixture_id:
                cursor.execute('SELECT * FROM cleaned_fixtures WHERE fixture_id = ?', (fixture_id,))
            else:
                cursor.execute('SELECT * FROM cleaned_fixtures ORDER BY match_date DESC LIMIT 100')
            
            fixtures = cursor.fetchall()
            if fixtures:
                columns = [description[0] for description in cursor.description]
                result['fixtures'] = [dict(zip(columns, row)) for row in fixtures]
            
            conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Failed to retrieve cleaned data: {e}")
            return {}

def clean_and_store():
    """Convenience function for the pipeline"""
    ingestion = DataIngestion()
    sample_data = ingestion.load_sample_data()
    return ingestion.clean_and_store(sample_data)
