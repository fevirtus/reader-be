#!/usr/bin/env python3
"""
Test callback với code thực tế từ Google OAuth
"""

import requests
import json
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://localhost:8000"

def test_callback_with_real_code():
    """Test callback với code thực tế"""
    print("🔧 === TESTING CALLBACK WITH REAL CODE ===\n")
    
    # Hướng dẫn người dùng
    print("📋 Instructions:")
    print("1. Mở browser và truy cập: http://localhost:8000/api/v1/oauth/google/auth")
    print("2. Hoàn thành OAuth flow với Google")
    print("3. Copy callback URL từ browser")
    print("4. Paste URL vào đây để test\n")
    
    # Nhận callback URL từ user
    callback_url = input("Paste callback URL here: ").strip()
    
    if not callback_url:
        print("❌ No URL provided")
        return False
    
    # Parse URL để lấy code và state
    try:
        parsed_url = urlparse(callback_url)
        query_params = parse_qs(parsed_url.query)
        
        code = query_params.get('code', [None])[0]
        state = query_params.get('state', [None])[0]
        
        if not code:
            print("❌ No authorization code found in URL")
            return False
        
        print(f"✅ Parsed URL successfully")
        print(f"   Code: {code[:20]}...")
        print(f"   State: {state}")
        
        # Test callback endpoint
        print(f"\n🔄 Testing callback endpoint...")
        
        params = {'code': code}
        if state:
            params['state'] = state
        
        response = requests.get(f"{BASE_URL}/api/v1/oauth/google/callback", params=params)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Callback successful!")
            print(f"   Session token: {data.get('session_token', 'N/A')[:20]}...")
            print(f"   User: {data.get('user', {}).get('username', 'N/A')}")
            print(f"   Email: {data.get('user', {}).get('email', 'N/A')}")
            print(f"   Is new user: {data.get('is_new_user', 'N/A')}")
            print(f"   Provider: {data.get('provider', 'N/A')}")
            
            # Test session token
            print(f"\n🔐 Testing session token...")
            test_session_endpoint(data.get('session_token', ''))
            
            return True
        else:
            print(f"❌ Callback failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error parsing URL: {e}")
        return False

def test_session_endpoint(session_token):
    """Test session token với user profile endpoint"""
    if not session_token:
        print("❌ No session token to test")
        return
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/user/profile",
            headers={'Authorization': f'Bearer {session_token}'}
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Session token valid!")
            print(f"   User profile: {user_data.get('username', 'N/A')}")
        else:
            print(f"❌ Session token invalid: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Session test error: {e}")

def main():
    """Main function"""
    print("🚀 === OAUTH CALLBACK TESTER ===\n")
    
    success = test_callback_with_real_code()
    
    if success:
        print("\n✅ OAuth flow test completed successfully!")
        print("🎉 Backend is working correctly with Google OAuth!")
    else:
        print("\n❌ OAuth flow test failed")
        print("🔧 Please check the error messages above")

if __name__ == "__main__":
    main() 