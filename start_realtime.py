#!/usr/bin/env python3
"""
Real-Time Football Betting Monitor Startup Script

This script starts the real-time betting monitor that:
- Continuously monitors for new matches
- Analyzes matches in real-time using live API data
- Posts value bets to Telegram automatically
- No mock data - only real API data

Usage:
    python start_realtime.py
"""

import asyncio
import sys
from realtime_monitor import RealTimeBettingMonitor

def main():
    print("🚀 FIXORA PRO - Real-Time Football Betting Monitor")
    print("=" * 60)
    print("📊 Features:")
    print("   • Real-time match monitoring")
    print("   • Live API data analysis")
    print("   • Automatic value bet detection")
    print("   • Instant Telegram notifications")
    print("   • No mock data - only real data")
    print("=" * 60)
    
    # Check if user wants to continue
    response = input("\nStart real-time monitor? (y/n): ").lower().strip()
    if response not in ['y', 'yes']:
        print("❌ Monitor not started")
        return
    
    print("\n🔄 Starting real-time monitor...")
    print("💡 Press Ctrl+C to stop the monitor")
    print("=" * 60)
    
    monitor = RealTimeBettingMonitor()
    
    try:
        asyncio.run(monitor.start())
    except KeyboardInterrupt:
        print("\n🛑 Real-time monitor stopped by user")
        monitor.stop()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your API key and Telegram bot setup")

if __name__ == "__main__":
    main()
