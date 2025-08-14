#!/usr/bin/env python3
"""
Comprehensive Telegram Bot Test Script
This script tests all bot functionality and provides detailed feedback
"""

import os
import sys
import asyncio
import logging
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

async def test_bot_imports():
    """Test all bot imports"""
    print("🔍 Testing Bot Imports...")
    print("=" * 40)
    
    try:
        # Test config import
        import config
        print("✅ Config imported successfully")
        print(f"   Bot token: {'✅ Set' if config.TELEGRAM_BOT_TOKEN else '❌ Missing'}")
        print(f"   API-Football key: {'✅ Set' if config.API_FOOTBALL_API_KEY else '❌ Missing'}")
        print(f"   SportMonks key: {'✅ Set' if config.SPORTMONKS_API_KEY else '❌ Missing'}")
        
        # Test realtime_analyzer import
        from realtime_analyzer import RealTimeAnalyzer
        print("✅ RealTimeAnalyzer imported successfully")
        
        # Test API clients
        from api.unified_api_client import UnifiedAPIClient
        print("✅ UnifiedAPIClient imported successfully")
        
        # Test bot creation
        from bot_interface.telegram_bot import TelegramBetBot
        print("✅ TelegramBetBot imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

async def test_network_connectivity():
    """Test network connectivity to various services"""
    print("\n🌐 Testing Network Connectivity...")
    print("=" * 40)
    
    import aiohttp
    
    test_urls = [
        ("Google", "https://www.google.com"),
        ("GitHub", "https://www.github.com"),
        ("API-Football", "https://v3.football.api-sports.io"),
        ("SportMonks", "https://api.sportmonks.com"),
        ("Telegram", "https://api.telegram.org")
    ]
    
    results = {}
    
    async with aiohttp.ClientSession() as session:
        for name, url in test_urls:
            try:
                print(f"   Testing {name}...")
                async with session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        print(f"      ✅ {name}: Accessible")
                        results[name] = True
                    else:
                        print(f"      ⚠️ {name}: HTTP {resp.status}")
                        results[name] = False
            except Exception as e:
                print(f"      ❌ {name}: {e}")
                results[name] = False
    
    return results

async def test_telegram_connectivity():
    """Test Telegram bot connectivity specifically"""
    print("\n🤖 Testing Telegram Connectivity...")
    print("=" * 40)
    
    try:
        import config
        from bot_interface.telegram_bot import TelegramBetBot
        
        bot = TelegramBetBot()
        
        # Test bot token
        print("   Testing bot token...")
        try:
            bot_info = await bot.bot.get_me()
            print(f"      ✅ Bot connected: @{bot_info.username}")
            print(f"      ✅ Bot ID: {bot_info.id}")
            print(f"      ✅ Bot name: {bot_info.first_name}")
            return True
        except Exception as e:
            print(f"      ❌ Bot connection failed: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ Telegram test failed: {e}")
        return False

async def test_api_functionality():
    """Test the core API functionality"""
    print("\n🔌 Testing API Functionality...")
    print("=" * 40)
    
    try:
        from api.unified_api_client import UnifiedAPIClient
        
        api_client = UnifiedAPIClient()
        
        # Test today's matches
        print("   Testing today's matches...")
        today_matches = await api_client.get_today_matches()
        print(f"      ✅ Found {len(today_matches)} matches")
        
        # Test live matches
        print("   Testing live matches...")
        live_matches = await api_client.get_live_scores()
        print(f"      ✅ Found {len(live_matches)} live matches")
        
        # Test analyzer
        print("   Testing analyzer...")
        from realtime_analyzer import RealTimeAnalyzer
        analyzer = RealTimeAnalyzer()
        
        # Analyze a few matches
        sample_matches = today_matches[:3] if today_matches else []
        if sample_matches:
            print(f"      Analyzing {len(sample_matches)} sample matches...")
            for match in sample_matches:
                try:
                    analysis = await analyzer._analyze_single_match(match, is_live=False)
                    if analysis:
                        home_team = analysis.get('home_team', 'Unknown')
                        away_team = analysis.get('away_team', 'Unknown')
                        quality = analysis.get('analysis_quality', 'unknown')
                        print(f"         ✅ {home_team} vs {away_team} ({quality})")
                    else:
                        print(f"         ❌ Analysis failed for match")
                except Exception as e:
                    print(f"         ❌ Analysis error: {e}")
        
        await api_client.close()
        return True
        
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        return False

async def test_bot_commands():
    """Test bot command handling"""
    print("\n📱 Testing Bot Commands...")
    print("=" * 40)
    
    try:
        from bot_interface.telegram_bot import TelegramBetBot
        
        bot = TelegramBetBot()
        
        # Test command methods exist
        required_methods = [
            'start_command', 'help_command', 'status_command',
            'setchat_command', 'analyze_command', 'live_command',
            'network_command'
        ]
        
        for method_name in required_methods:
            if hasattr(bot, method_name):
                print(f"   ✅ {method_name}: Available")
            else:
                print(f"   ❌ {method_name}: Missing")
        
        # Test status method
        status = bot.get_bot_status()
        print(f"   ✅ Bot status: {status}")
        
        # Test troubleshooting tips
        tips = bot.get_network_troubleshooting_tips()
        print(f"   ✅ Troubleshooting tips: {len(tips)} characters")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Bot command test failed: {e}")
        return False

async def run_comprehensive_test():
    """Run all tests"""
    print("🤖 FIXORA PRO Comprehensive Bot Test")
    print("=" * 60)
    print("This test will verify all bot functionality and provide")
    print("detailed feedback on any issues found.")
    print()
    
    start_time = time.time()
    
    # Run all tests
    tests = [
        ("Bot Imports", test_bot_imports),
        ("Network Connectivity", test_network_connectivity),
        ("Telegram Connectivity", test_telegram_connectivity),
        ("API Functionality", test_api_functionality),
        ("Bot Commands", test_bot_commands)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("="*60)
    
    total_tests = len(tests)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n   Overall: {passed_tests}/{total_tests} tests passed")
    
    # Recommendations
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Your bot is ready to run.")
        print("   Run: python bot_interface/telegram_bot.py")
    else:
        print("\n⚠️ Some tests failed. Here are the recommendations:")
        
        if not results.get("Bot Imports", False):
            print("   • Fix import issues first")
        
        if not results.get("Network Connectivity", False):
            print("   • Check your internet connection")
            print("   • Try a different network (mobile hotspot)")
        
        if not results.get("Telegram Connectivity", False):
            print("   • Telegram connectivity issue detected")
            print("   • Check firewall/proxy settings")
            print("   • Verify bot token is correct")
            print("   • Try using a VPN")
        
        if not results.get("API Functionality", False):
            print("   • Core API functionality issue")
            print("   • Check API keys and configuration")
        
        if not results.get("Bot Commands", False):
            print("   • Bot command structure issue")
            print("   • Check bot implementation")
    
    # Time taken
    elapsed_time = time.time() - start_time
    print(f"\n⏱️  Total test time: {elapsed_time:.2f} seconds")
    
    return passed_tests == total_tests

async def main():
    """Main function"""
    try:
        success = await run_comprehensive_test()
        
        if success:
            print("\n🚀 Ready to start the bot!")
            print("   Run: python bot_interface/telegram_bot.py")
        else:
            print("\n🔧 Please fix the issues above before running the bot.")
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Failed to run test: {e}")
        import traceback
        traceback.print_exc()
