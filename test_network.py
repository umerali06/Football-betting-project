#!/usr/bin/env python3
"""
Network connectivity test for FIXORA PRO system
"""

import asyncio
import aiohttp
import requests
import config

async def test_telegram_connectivity():
    """Test connectivity to Telegram Bot API"""
    print("🔍 Testing Telegram connectivity...")
    
    # Test 1: Direct HTTP request to Telegram
    try:
        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/getMe"
        print(f"   Testing: {url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('ok'):
                        print(f"   ✅ Telegram API accessible: @{data['result']['username']}")
                        return True
                    else:
                        print(f"   ❌ Telegram API error: {data}")
                        return False
                else:
                    print(f"   ❌ HTTP {resp.status}: {await resp.text()}")
                    return False
    except Exception as e:
        print(f"   ❌ Telegram test failed: {e}")
        return False

async def test_api_football_connectivity():
    """Test connectivity to API-Football"""
    print("🔍 Testing API-Football connectivity...")
    
    try:
        url = "https://v3.football.api-sports.io/status"
        print(f"   Testing: {url}")
        
        async with aiohttp.ClientSession() as session:
            headers = {"x-apisports-key": config.API_FOOTBALL_API_KEY}
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    print("   ✅ API-Football accessible")
                    return True
                else:
                    print(f"   ❌ HTTP {resp.status}: {await resp.text()}")
                    return False
    except Exception as e:
        print(f"   ❌ API-Football test failed: {e}")
        return False

async def test_sportmonks_connectivity():
    """Test connectivity to SportMonks"""
    print("🔍 Testing SportMonks connectivity...")
    
    try:
        url = f"https://api.sportmonks.com/v3/football/fixtures?api_token={config.SPORTMONKS_API_KEY}&filters=todayDate"
        print(f"   Testing: {url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    print("   ✅ SportMonks accessible")
                    return True
                else:
                    print(f"   ❌ HTTP {resp.status}: {await resp.text()}")
                    return False
    except Exception as e:
        print(f"   ❌ SportMonks test failed: {e}")
        return False

async def test_basic_connectivity():
    """Test basic internet connectivity"""
    print("🔍 Testing basic internet connectivity...")
    
    test_urls = [
        "https://www.google.com",
        "https://www.github.com",
        "https://api.telegram.org"
    ]
    
    for url in test_urls:
        try:
            print(f"   Testing: {url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        print(f"   ✅ {url} accessible")
                    else:
                        print(f"   ⚠️ {url} returned HTTP {resp.status}")
        except Exception as e:
            print(f"   ❌ {url} failed: {e}")

async def main():
    """Run all connectivity tests"""
    print("🌐 FIXORA PRO Network Connectivity Test")
    print("=" * 50)
    
    # Test basic connectivity first
    await test_basic_connectivity()
    print()
    
    # Test specific APIs
    telegram_ok = await test_telegram_connectivity()
    print()
    
    api_football_ok = await test_api_football_connectivity()
    print()
    
    sportmonks_ok = await test_sportmonks_connectivity()
    print()
    
    # Summary
    print("📊 Connectivity Summary:")
    print(f"   Telegram: {'✅' if telegram_ok else '❌'}")
    print(f"   API-Football: {'✅' if api_football_ok else '❌'}")
    print(f"   SportMonks: {'✅' if sportmonks_ok else '❌'}")
    
    if not telegram_ok:
        print("\n⚠️ Telegram connectivity issue detected!")
        print("   This will prevent the bot from working.")
        print("   Possible causes:")
        print("   - No internet connection")
        print("   - Firewall/proxy blocking Telegram")
        print("   - Invalid bot token")
        print("   - Network configuration issues")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")
