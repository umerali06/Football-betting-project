#!/usr/bin/env python3
"""
Test timezone utilities for FIXORA PRO
"""

import unittest
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.time import (
    now_london, 
    now_utc, 
    to_utc, 
    to_london, 
    is_future_match, 
    format_london_time, 
    get_next_8am_london
)

class TestTimezoneUtilities(unittest.TestCase):
    """Test timezone utility functions"""
    
    def test_now_london(self):
        """Test getting current London time"""
        london_time = now_london()
        self.assertIsNotNone(london_time)
        self.assertIsNotNone(london_time.tzinfo)
        self.assertEqual(str(london_time.tzinfo), 'Europe/London')
    
    def test_now_utc(self):
        """Test getting current UTC time"""
        utc_time = now_utc()
        self.assertIsNotNone(utc_time)
        self.assertIsNotNone(utc_time.tzinfo)
        self.assertEqual(str(utc_time.tzinfo), 'UTC')
    
    def test_to_utc(self):
        """Test converting to UTC"""
        # Test with London time
        london_time = now_london()
        utc_time = to_utc(london_time)
        self.assertEqual(str(utc_time.tzinfo), 'UTC')
        
        # Test with naive datetime (should assume London)
        naive_time = datetime.now()
        utc_from_naive = to_utc(naive_time)
        self.assertEqual(str(utc_from_naive.tzinfo), 'UTC')
    
    def test_to_london(self):
        """Test converting to London time"""
        # Test with UTC time
        utc_time = now_utc()
        london_time = to_london(utc_time)
        self.assertEqual(str(london_time.tzinfo), 'Europe/London')
        
        # Test with naive datetime (should assume UTC)
        naive_time = datetime.now()
        london_from_naive = to_london(naive_time)
        self.assertEqual(str(london_from_naive.tzinfo), 'Europe/London')
    
    def test_is_future_match(self):
        """Test future match detection"""
        # Test future match
        future_time = now_london() + timedelta(hours=2)
        self.assertTrue(is_future_match(future_time))
        
        # Test past match
        past_time = now_london() - timedelta(hours=2)
        self.assertFalse(is_future_match(past_time))
        
        # Test with cutoff
        near_future = now_london() + timedelta(minutes=30)
        self.assertTrue(is_future_match(near_future, cutoff_minutes=15))
        self.assertFalse(is_future_match(near_future, cutoff_minutes=45))
    
    def test_format_london_time(self):
        """Test London time formatting"""
        # Test with UTC time
        utc_time = now_utc()
        formatted = format_london_time(utc_time)
        self.assertIsInstance(formatted, str)
        self.assertIn(':', formatted)  # Should contain time separator
        
        # Test with naive datetime
        naive_time = datetime.now()
        formatted_naive = format_london_time(naive_time)
        self.assertIsInstance(formatted_naive, str)
    
    def test_get_next_8am_london(self):
        """Test getting next 8:00 AM London time"""
        next_8am = get_next_8am_london()
        self.assertIsNotNone(next_8am)
        self.assertEqual(str(next_8am.tzinfo), 'Europe/London')
        self.assertEqual(next_8am.hour, 8)
        self.assertEqual(next_8am.minute, 0)
        self.assertEqual(next_8am.second, 0)
        self.assertEqual(next_8am.microsecond, 0)
        
        # Should be in the future
        self.assertGreater(next_8am, now_london())
    
    def test_timezone_consistency(self):
        """Test timezone consistency across functions"""
        london_now = now_london()
        utc_now = now_utc()
        
        # Convert London to UTC and back should be consistent
        london_to_utc = to_utc(london_now)
        utc_to_london = to_london(london_to_utc)
        
        # Allow for small time differences due to processing
        time_diff = abs((london_now - utc_to_london).total_seconds())
        self.assertLess(time_diff, 1)  # Should be within 1 second

if __name__ == '__main__':
    unittest.main()
