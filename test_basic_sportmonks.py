#!/usr/bin/env python3
"""
Basic Sportmonks API Test
Simple test to check if the API key works
"""

import requests
import json
import config

def test_basic_connection():
    """Test basic API connection"""
    print("🧪 Testing Basic Sportmonks API Connection")
    print("=" * 50)
    
    api_key = config.SPORTMONKS_API_KEY
    print(f"API Key: {api_key[:15]}...")
    
    # Test different endpoints
    endpoints_to_test = [
        "livescores",
        "fixtures",
        "leagues"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n📡 Testing {endpoint} endpoint...")
        
        # Method 1: Query parameter
        url = f"https://api.sportmonks.com/v3/football/{endpoint}"
        params = {'api_token': api_key}
        headers = {'Accept': 'application/json'}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS! Response keys: {list(data.keys())}")
                
                # Print full response for debugging
                print(f"   📄 Full Response:")
                print(json.dumps(data, indent=2))
                
                if 'data' in data and isinstance(data['data'], list):
                    print(f"   📊 Found {len(data['data'])} items")
                    
                return True
            else:
                print(f"   ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    return False

if __name__ == "__main__":
    test_basic_connection()