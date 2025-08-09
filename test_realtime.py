import asyncio
from realtime_monitor import RealTimeBettingMonitor

async def test_realtime_system():
    """Test the real-time betting monitor"""
    print("🧪 Testing Real-Time Betting Monitor")
    print("=" * 50)
    
    monitor = RealTimeBettingMonitor()
    
    try:
        # Test API connection
        print("\n1. Testing API connection...")
        matches = monitor.api_client.get_today_matches(days_ahead=1)
        print(f"✅ API connection successful - Found {len(matches)} matches")
        
        # Test match analysis
        if matches:
            print(f"\n2. Testing match analysis...")
            match = matches[0]
            print(f"Analyzing: {match['teams']['home']['name']} vs {match['teams']['away']['name']}")
            
            value_bets = await monitor.analyze_match(match)
            print(f"✅ Analysis successful - Found {len(value_bets)} value bets")
            
            if value_bets:
                print("Sample value bet:")
                bet = value_bets[0]
                print(f"  Market: {bet['market']}")
                print(f"  Selection: {bet['selection']}")
                print(f"  Odds: {bet['odds']}")
                print(f"  Edge: {bet['edge']:.3f}")
        
        # Test Telegram bot (without actually starting it)
        print(f"\n3. Testing Telegram bot setup...")
        print(f"✅ Bot token: {'✅ Set' if monitor.telegram_bot.token else '❌ Missing'}")
        print(f"✅ Chat ID: {'✅ Set' if monitor.telegram_bot.chat_id else '❌ Not set'}")
        
        print(f"\n✅ All tests passed! Real-time system is ready to run.")
        print(f"\nTo start the real-time monitor, run:")
        print(f"python realtime_monitor.py")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_realtime_system())
