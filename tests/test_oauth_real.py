#!/usr/bin/env python3
"""
Test OAuth flow thực tế với Google
"""

import requests
import json
import webbrowser
import time
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://localhost:8000"

def test_real_oauth_flow():
    """Test OAuth flow thực tế với Google"""
    print("🚀 === REAL OAUTH FLOW TEST ===\n")
    
    # Test 1: Lấy OAuth URL
    print("🔐 Getting Google OAuth URL...")
    state = "test_state_real_123"
    response = requests.get(f"{BASE_URL}/api/v1/oauth/google/auth?state={state}")
    
    if response.status_code != 200:
        print(f"❌ Failed to get OAuth URL: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    data = response.json()
    auth_url = data.get("auth_url", "")
    provider = data.get("provider", "")
    
    print(f"✅ OAuth URL successful")
    print(f"   Provider: {provider}")
    print(f"   Auth URL: {auth_url[:100]}...")
    
    # Kiểm tra state parameter
    parsed_url = urlparse(auth_url)
    query_params = parse_qs(parsed_url.query)
    url_state = query_params.get('state', [None])[0]
    
    if url_state == state:
        print(f"✅ State parameter correctly included: {url_state}")
    else:
        print(f"❌ State parameter missing or incorrect")
        print(f"   Expected: {state}")
        print(f"   Got: {url_state}")
        return False
    
    # Test 2: Mở browser để test thực tế
    print("\n🌐 Opening browser for real OAuth test...")
    print("   This will open Google OAuth in your browser.")
    print("   After authentication, you'll be redirected to a callback URL.")
    print("   Please check the browser and note the callback URL.")
    
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened successfully")
        print("   Please complete the OAuth flow in your browser")
        print("   The callback URL will show the result")
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print(f"   Please manually open this URL: {auth_url}")
    
    # Test 3: Hướng dẫn test thủ công
    print("\n📋 Manual Testing Instructions:")
    print("1. Complete OAuth flow in browser")
    print("2. Note the callback URL (should be something like):")
    print(f"   {BASE_URL}/api/v1/oauth/google/callback?code=...&state={state}")
    print("3. Check if the response contains session_token")
    print("4. Verify user profile creation")
    
    # Test 4: Kiểm tra server logs
    print("\n📊 Server Logs to Check:")
    print("- OAuth callback processing")
    print("- User profile creation/update")
    print("- Session token generation")
    print("- Error messages (if any)")
    
    print("\n✅ Real OAuth test setup complete!")
    print("🎉 Please complete the OAuth flow in your browser")
    print("   and check the server logs for results.")
    
    return True

def test_callback_manual():
    """Test callback endpoint với code thủ công"""
    print("\n🔧 Manual Callback Test:")
    print("If you have a valid authorization code, you can test it here:")
    
    code = input("Enter authorization code (or press Enter to skip): ").strip()
    
    if not code:
        print("Skipping manual callback test")
        return True
    
    print(f"Testing callback with code: {code[:20]}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/oauth/google/callback?code={code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Callback successful!")
            print(f"   Session token: {data.get('session_token', 'N/A')[:20]}...")
            print(f"   User: {data.get('user', {}).get('username', 'N/A')}")
            print(f"   Is new user: {data.get('is_new_user', 'N/A')}")
            print(f"   Provider: {data.get('provider', 'N/A')}")
        else:
            print(f"❌ Callback failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Callback test error: {e}")
    
    return True

if __name__ == "__main__":
    try:
        test_real_oauth_flow()
        test_callback_manual()
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        exit(1) 