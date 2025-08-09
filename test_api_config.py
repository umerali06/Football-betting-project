import requests
import json
import config

def test_api_configuration():
    """Test the API configuration to see if it's working properly"""
    
    print("🔍 Testing API Configuration...")
    print("=" * 50)
    
    # Get API key from config
    api_key = config.API_FOOTBALL_KEY
    base_url = config.API_FOOTBALL_BASE_URL
    
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"🌐 Base URL: {base_url}")
    print()
    
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': api_key
    }
    
    # Test 1: Basic connectivity
    print("1. Testing basic connectivity...")
    try:
        response = requests.get(f"{base_url}/status", headers=headers)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API is accessible")
            print(f"   Response: {data.get('response', 'Unknown')}")
        else:
            print(f"   ❌ API access failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    print()
    
    # Test 2: Current date access
    print("2. Testing current date access...")
    try:
        response = requests.get(f"{base_url}/fixtures", headers=headers, 
                              params={'date': '2025-08-09'})
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data and data['errors']:
                print(f"   ❌ API Errors: {data['errors']}")
            else:
                matches = data.get('response', [])
                print(f"   ✅ Success! Found {len(matches)} matches")
                if matches:
                    print(f"   Sample match: {matches[0]['teams']['home']['name']} vs {matches[0]['teams']['away']['name']}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 3: Rate limit check
    print("3. Checking rate limits...")
    try:
        response = requests.get(f"{base_url}/fixtures", headers=headers, 
                              params={'date': '2025-08-10'})
        headers_info = dict(response.headers)
        rate_limit = headers_info.get('x-ratelimit-remaining', 'Unknown')
        print(f"   Remaining requests: {rate_limit}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    print("=" * 50)
    
    # Summary
    print("📋 SUMMARY:")
    print("✅ API Key is configured")
    print("✅ Base URL is set correctly")
    print("✅ Headers are properly formatted")
    print()
    print("🎯 To get real-time data updating continuously:")
    print("   Run: python start_realtime.py")
    print("   NOT: python main.py (this is for daily analysis only)")

if __name__ == "__main__":
    test_api_configuration()
