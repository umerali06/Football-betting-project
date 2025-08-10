#!/usr/bin/env python3
"""
Sportmonks API Test Script
This script tests the Sportmonks API integration
"""

import asyncio
import sys
from api.sportmonks_client import SportmonksClient
from api.unified_client import UnifiedAPIClient
import config

async def test_sportmonks_direct():
    """Test Sportmonks API directly"""
    print("🧪 Testing Sportmonks API Direct Connection")
    print("=" * 50)
    
    client = SportmonksClient()
    
    print(f"API Key: {client.api_key[:15]}...")
    print(f"Base URL: {client.base_url}")
    print()
    
    # Test basic API call
    print("📡 Testing API connection...")
    try:
        matches = client.get_today_matches()
        if matches:
            print(f"✅ API connection successful! Found {len(matches)} matches")
            
            # Show first few matches
            for i, match in enumerate(matches[:3], 1):
                home_team = match['teams']['home']['name']
                away_team = match['teams']['away']['name']
                match_time = match['fixture']['date']
                print(f"   {i}. {home_team} vs {away_team} at {match_time}")
        else:
            print("⚠️ API connection successful but no matches found for today")
            
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False
    
    return True

def test_unified_client():
    """Test the unified client with Sportmonks"""
    print("\n🔄 Testing Unified API Client")
    print("=" * 50)
    
    client = UnifiedAPIClient()
    
    # Get API status
    status = client.get_api_status()
    print(f"Primary API: {status['primary_api']}")
    print(f"Fallback API: {status['fallback_api']}")
    print(f"Sportmonks Enabled: {status['sportmonks_enabled']}")
    print(f"Primary Working: {status['primary_working']}")
    print(f"Fallback Working: {status['fallback_working']}")
    print()
    
    # Test getting matches
    try:
        matches = client.get_today_matches()
        if matches:
            print(f"✅ Unified client successful! Found {len(matches)} matches")
            return True
        else:
            print("⚠️ Unified client working but no matches found")
            return True
    except Exception as e:
        print(f"❌ Unified client failed: {e}")
        return False

def show_config():
    """Show current configuration"""
    print("🔧 Current Configuration")
    print("=" * 50)
    print(f"Primary API: {config.PRIMARY_API}")
    print(f"Fallback API: {config.FALLBACK_API}")
    print(f"Sportmonks Enabled: {config.SPORTMONKS_ENABLED}")
    print(f"Sportmonks API Key: {config.SPORTMONKS_API_KEY[:15]}...")
    print(f"Sportmonks Base URL: {config.SPORTMONKS_BASE_URL}")
    print()

async def main():
    """Main test function"""
    print("🤖 Sportmonks API Integration Test")
    print("=" * 60)
    
    # Show configuration
    show_config()
    
    # Test Sportmonks directly
    sportmonks_success = await test_sportmonks_direct()
    
    # Test unified client
    unified_success = test_unified_client()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    print(f"Sportmonks Direct: {'✅ PASS' if sportmonks_success else '❌ FAIL'}")
    print(f"Unified Client: {'✅ PASS' if unified_success else '❌ FAIL'}")
    
    if sportmonks_success and unified_success:
        print("\n🎉 All tests passed! Sportmonks integration is working correctly.")
        print("\n💡 You can now run your betting system with Sportmonks as the primary API:")
        print("   python main.py")
    else:
        print("\n⚠️ Some tests failed. Please check your API configuration:")
        print("   1. Verify your Sportmonks API key is correct")
        print("   2. Check your internet connection")
        print("   3. Ensure your Sportmonks subscription is active")
        print(f"   4. Visit {config.SPORTMONKS_BASE_URL} to verify the endpoint")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python test_sportmonks.py")
        print("Tests the Sportmonks API integration")
        sys.exit(0)
    
    asyncio.run(main())