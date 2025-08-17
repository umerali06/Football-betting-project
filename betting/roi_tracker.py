#!/usr/bin/env python3
"""
ROI Tracker for FIXORA PRO
Tracks betting performance by market and generates weekly reports
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

class ROITracker:
    """
    Tracks Return on Investment (ROI) for different betting markets
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_FILE
        self.init_database()
    
    def init_database(self):
        """Initialize the database with ROI tracking tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create ROI tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS roi_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fixture_id INTEGER NOT NULL,
                    league_id INTEGER NOT NULL,
                    league_name TEXT NOT NULL,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    market_type TEXT NOT NULL,
                    selection TEXT NOT NULL,
                    odds REAL NOT NULL,
                    stake REAL NOT NULL,
                    potential_return REAL NOT NULL,
                    bet_date TEXT NOT NULL,
                    match_date TEXT NOT NULL,
                    result TEXT,
                    actual_return REAL,
                    profit_loss REAL,
                    roi_percentage REAL,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create market performance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    market_type TEXT NOT NULL,
                    total_bets INTEGER DEFAULT 0,
                    winning_bets INTEGER DEFAULT 0,
                    total_stake REAL DEFAULT 0.0,
                    total_return REAL DEFAULT 0.0,
                    total_profit_loss REAL DEFAULT 0.0,
                    overall_roi REAL DEFAULT 0.0,
                    weekly_roi REAL DEFAULT 0.0,
                    monthly_roi REAL DEFAULT 0.0,
                    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create league performance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS league_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    league_id INTEGER NOT NULL,
                    league_name TEXT NOT NULL,
                    total_bets INTEGER DEFAULT 0,
                    winning_bets INTEGER DEFAULT 0,
                    total_stake REAL DEFAULT 0.0,
                    total_return REAL DEFAULT 0.0,
                    total_profit_loss REAL DEFAULT 0.0,
                    overall_roi REAL DEFAULT 0.0,
                    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("ROI tracking database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ROI tracking database: {e}")
    
    def record_bet(self, bet_data: Dict) -> Tuple[bool, int]:
        """
        Record a new bet for ROI tracking
        
        Args:
            bet_data: Dictionary containing bet information
                - fixture_id, league_id, league_name, home_team, away_team
                - market_type, selection, odds, stake
                - bet_date, match_date
        
        Returns:
            Tuple of (success, bet_id) where success is boolean and bet_id is the ID of the recorded bet
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO roi_tracking (
                    fixture_id, league_id, league_name, home_team, away_team,
                    market_type, selection, odds, stake, potential_return,
                    bet_date, match_date, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                bet_data['fixture_id'],
                bet_data['league_id'],
                bet_data['league_name'],
                bet_data['home_team'],
                bet_data['away_team'],
                bet_data['market_type'],
                bet_data['selection'],
                bet_data['odds'],
                bet_data['stake'],
                bet_data['stake'] * bet_data['odds'],
                bet_data['bet_date'],
                bet_data['match_date'],
                'pending'
            ))
            
            bet_id = cursor.lastrowid
            conn.commit()
            conn.close()
            logger.info(f"Bet recorded for {bet_data['home_team']} vs {bet_data['away_team']}")
            return True, bet_id
            
        except Exception as e:
            logger.error(f"Failed to record bet: {e}")
            return False, 0
    
    def update_bet_result(self, fixture_id: int, result: str, actual_return: float = 0.0):
        """
        Update bet result after match completion
        
        Args:
            fixture_id: ID of the fixture
            result: 'win', 'loss', or 'void'
            actual_return: Actual return from the bet
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get the bet details
            cursor.execute('''
                SELECT stake, odds FROM roi_tracking 
                WHERE fixture_id = ? AND status = 'pending'
            ''', (fixture_id,))
            
            bet = cursor.fetchone()
            if not bet:
                logger.warning(f"No pending bet found for fixture {fixture_id}")
                return False
            
            stake, odds = bet
            
            # Calculate profit/loss and ROI
            if result == 'win':
                profit_loss = actual_return - stake
                roi_percentage = (profit_loss / stake) * 100
                status = 'won'
            elif result == 'loss':
                profit_loss = -stake
                roi_percentage = -100
                status = 'lost'
            else:  # void
                profit_loss = 0
                roi_percentage = 0
                status = 'void'
            
            # Update the bet
            cursor.execute('''
                UPDATE roi_tracking SET
                    result = ?, actual_return = ?, profit_loss = ?,
                    roi_percentage = ?, status = ?
                WHERE fixture_id = ? AND status = 'pending'
            ''', (result, actual_return, profit_loss, roi_percentage, status, fixture_id))
            
            conn.commit()
            conn.close()
            
            # Update market and league performance
            self._update_performance_tables(fixture_id)
            
            logger.info(f"Bet result updated for fixture {fixture_id}: {result}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update bet result: {e}")
            return False
    
    def update_specific_bet_result(self, bet_id: int, result: str, actual_return: float = 0.0):
        """
        Update a specific bet by ID
        
        Args:
            bet_id: ID of the specific bet
            result: 'win', 'loss', or 'void'
            actual_return: Actual return from the bet
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get the bet details
            cursor.execute('''
                SELECT fixture_id, stake, odds FROM roi_tracking 
                WHERE id = ? AND status = 'pending'
            ''', (bet_id,))
            
            bet = cursor.fetchone()
            if not bet:
                logger.warning(f"No pending bet found with ID {bet_id}")
                return False
            
            fixture_id, stake, odds = bet
            
            # Calculate profit/loss and ROI
            if result == 'win':
                profit_loss = actual_return - stake
                roi_percentage = (profit_loss / stake) * 100
                status = 'won'
            elif result == 'loss':
                profit_loss = -stake
                roi_percentage = -100
                status = 'lost'
            else:  # void
                profit_loss = 0
                roi_percentage = 0
                status = 'void'
            
            # Update the specific bet
            cursor.execute('''
                UPDATE roi_tracking SET
                    result = ?, actual_return = ?, profit_loss = ?,
                    roi_percentage = ?, status = ?
                WHERE id = ?
            ''', (result, actual_return, profit_loss, roi_percentage, status, bet_id))
            
            conn.commit()
            conn.close()
            
            # Update market and league performance
            self._update_performance_tables(fixture_id)
            
            logger.debug(f"Bet {bet_id} result updated: {result}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update bet {bet_id} result: {e}")
            return False
    
    def _update_performance_tables(self, fixture_id: int):
        """Update market and league performance tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get bet details
            cursor.execute('''
                SELECT market_type, league_id, league_name, stake, profit_loss, status
                FROM roi_tracking WHERE fixture_id = ?
            ''', (fixture_id,))
            
            bet = cursor.fetchone()
            if not bet:
                return
            
            market_type, league_id, league_name, stake, profit_loss, status = bet
            
            # Update market performance
            self._update_market_performance(cursor, market_type, stake, profit_loss, status)
            
            # Update league performance
            self._update_league_performance(cursor, league_id, league_name, stake, profit_loss, status)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update performance tables: {e}")
    
    def _update_market_performance(self, cursor, market_type: str, stake: float, profit_loss: float, status: str):
        """Update market performance statistics"""
        # Get current market performance
        cursor.execute('''
            SELECT total_bets, winning_bets, total_stake, total_return, total_profit_loss
            FROM market_performance WHERE market_type = ?
        ''', (market_type,))
        
        result = cursor.fetchone()
        if result:
            total_bets, winning_bets, total_stake, total_return, total_profit_loss = result
            
            # Update values
            new_total_bets = total_bets + 1
            new_winning_bets = winning_bets + (1 if status == 'won' else 0)
            new_total_stake = total_stake + stake
            new_total_return = total_return + (stake + profit_loss if status == 'won' else 0)
            new_total_profit_loss = total_profit_loss + profit_loss
            
            # Calculate ROI
            new_overall_roi = (new_total_profit_loss / new_total_stake) * 100 if new_total_stake > 0 else 0
            
            cursor.execute('''
                UPDATE market_performance SET
                    total_bets = ?, winning_bets = ?, total_stake = ?,
                    total_return = ?, total_profit_loss = ?, overall_roi = ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE market_type = ?
            ''', (new_total_bets, new_winning_bets, new_total_stake,
                  new_total_return, new_total_profit_loss, new_overall_roi, market_type))
        else:
            # Create new market performance record
            total_return = stake + profit_loss if status == 'won' else 0
            overall_roi = (profit_loss / stake) * 100 if stake > 0 else 0
            
            cursor.execute('''
                INSERT INTO market_performance (
                    market_type, total_bets, winning_bets, total_stake,
                    total_return, total_profit_loss, overall_roi
                ) VALUES (?, 1, ?, ?, ?, ?, ?)
            ''', (market_type, 1 if status == 'won' else 0, stake, total_return, profit_loss, overall_roi))
    
    def _update_league_performance(self, cursor, league_id: int, league_name: str, stake: float, profit_loss: float, status: str):
        """Update league performance statistics"""
        # Get current league performance
        cursor.execute('''
            SELECT total_bets, winning_bets, total_stake, total_return, total_profit_loss
            FROM league_performance WHERE league_id = ?
        ''', (league_id,))
        
        result = cursor.fetchone()
        if result:
            total_bets, winning_bets, total_stake, total_return, total_profit_loss = result
            
            # Update values
            new_total_bets = total_bets + 1
            new_winning_bets = winning_bets + (1 if status == 'won' else 0)
            new_total_stake = total_stake + stake
            new_total_return = total_return + (stake + profit_loss if status == 'won' else 0)
            new_total_profit_loss = total_profit_loss + profit_loss
            
            # Calculate ROI
            new_overall_roi = (new_total_profit_loss / new_total_stake) * 100 if new_total_stake > 0 else 0
            
            cursor.execute('''
                UPDATE league_performance SET
                    total_bets = ?, winning_bets = ?, total_stake = ?,
                    total_return = ?, total_profit_loss = ?, overall_roi = ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE league_id = ?
            ''', (new_total_bets, new_winning_bets, new_total_stake,
                  new_total_return, new_total_profit_loss, new_overall_roi, league_id))
        else:
            # Create new league performance record
            total_return = stake + profit_loss if status == 'won' else 0
            overall_roi = (profit_loss / stake) * 100 if stake > 0 else 0
            
            cursor.execute('''
                INSERT INTO league_performance (
                    league_id, league_name, total_bets, winning_bets, total_stake,
                    total_return, total_profit_loss, overall_roi
                ) VALUES (?, ?, 1, ?, ?, ?, ?, ?)
            ''', (league_id, league_name, 1 if status == 'won' else 0, stake, total_return, profit_loss, overall_roi))
    
    def get_market_performance(self, market_type: str = None) -> List[Dict]:
        """Get performance statistics for markets"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if market_type:
                cursor.execute('''
                    SELECT * FROM market_performance WHERE market_type = ?
                ''', (market_type,))
            else:
                cursor.execute('SELECT * FROM market_performance ORDER BY overall_roi DESC')
            
            columns = [description[0] for description in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Failed to get market performance: {e}")
            return []
    
    def get_league_performance(self, league_id: int = None) -> List[Dict]:
        """Get performance statistics for leagues"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if league_id:
                cursor.execute('''
                    SELECT * FROM league_performance WHERE league_id = ?
                ''', (league_id,))
            else:
                cursor.execute('SELECT * FROM league_performance ORDER BY overall_roi DESC')
            
            columns = [description[0] for description in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Failed to get league performance: {e}")
            return []
    
    def get_weekly_performance(self, days: int = 7) -> Dict:
        """Get performance statistics for the last N days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            cursor.execute('''
                SELECT 
                    market_type,
                    COUNT(*) as total_bets,
                    SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as winning_bets,
                    SUM(COALESCE(stake, 0)) as total_stake,
                    SUM(COALESCE(actual_return, 0)) as total_return,
                    SUM(COALESCE(profit_loss, 0)) as total_profit_loss
                FROM roi_tracking 
                WHERE bet_date >= ? AND bet_date <= ?
                GROUP BY market_type
            ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            results = {}
            for row in cursor.fetchall():
                market_type, total_bets, winning_bets, total_stake, total_return, total_profit_loss = row
                
                # Ensure all values are numbers, not None
                total_bets = total_bets or 0
                winning_bets = winning_bets or 0
                total_stake = total_stake or 0
                total_return = total_return or 0
                total_profit_loss = total_profit_loss or 0
                
                if total_stake > 0:
                    roi = (total_profit_loss / total_stake) * 100
                    win_rate = (winning_bets / total_bets) * 100 if total_bets > 0 else 0
                else:
                    roi = 0
                    win_rate = 0
                
                results[market_type] = {
                    'total_bets': total_bets,
                    'winning_bets': winning_bets,
                    'win_rate': win_rate,
                    'total_stake': total_stake,
                    'total_return': total_return,
                    'total_profit_loss': total_profit_loss,
                    'roi': roi
                }
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Failed to get weekly performance: {e}")
            return {}
    
    def get_overall_performance(self) -> Dict:
        """Get overall performance statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_bets,
                    SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as winning_bets,
                    SUM(COALESCE(stake, 0)) as total_stake,
                    SUM(COALESCE(actual_return, 0)) as total_return,
                    SUM(COALESCE(profit_loss, 0)) as total_profit_loss
                FROM roi_tracking
            ''')
            
            row = cursor.fetchone()
            if row:
                total_bets, winning_bets, total_stake, total_return, total_profit_loss = row
                
                # Ensure all values are numbers, not None
                total_bets = total_bets or 0
                winning_bets = winning_bets or 0
                total_stake = total_stake or 0
                total_return = total_return or 0
                total_profit_loss = total_profit_loss or 0
                
                if total_stake > 0:
                    roi = (total_profit_loss / total_stake) * 100
                    win_rate = (winning_bets / total_bets) * 100 if total_bets > 0 else 0
                else:
                    roi = 0
                    win_rate = 0
                
                result = {
                    'total_bets': total_bets,
                    'winning_bets': winning_bets,
                    'win_rate': win_rate,
                    'total_stake': total_stake,
                    'total_return': total_return,
                    'total_profit_loss': total_profit_loss,
                    'overall_roi': roi
                }
            else:
                result = {
                    'total_bets': 0,
                    'winning_bets': 0,
                    'win_rate': 0,
                    'total_stake': 0,
                    'total_return': 0,
                    'total_profit_loss': 0,
                    'overall_roi': 0
                }
            
            conn.close()
            return result
            
        except Exception as e:
            logger.error(f"Failed to get overall performance: {e}")
            return {}
    
    def get_all_bets(self) -> List[Dict]:
        """Get all bets from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    id,
                    fixture_id,
                    league_id,
                    league_name,
                    home_team,
                    away_team,
                    market_type,
                    selection,
                    odds,
                    stake,
                    potential_return,
                    bet_date,
                    match_date,
                    result,
                    actual_return,
                    profit_loss,
                    roi_percentage,
                    status,
                    created_at
                FROM roi_tracking
                ORDER BY bet_date DESC
            ''')
            
            columns = [description[0] for description in cursor.description]
            bets = []
            
            for row in cursor.fetchall():
                bet = dict(zip(columns, row))
                bets.append(bet)
            
            conn.close()
            logger.info(f"Retrieved {len(bets)} bets from database")
            return bets
            
        except Exception as e:
            logger.error(f"Failed to get all bets: {e}")
            return []
