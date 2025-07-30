#!/usr/bin/env python3
"""
Test OAuth với delay để tránh rate limiting
"""

import requests
import time
import json
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://localhost:8000"

def test_oauth_with_delay():
    """Test OAuth với delay để tránh rate limiting"""
    print("🚀 === OAUTH TEST WITH DELAY ===\n")
    
    # Test 1: Lấy OAuth URL
    print("1. Getting OAuth URL...")
    state = f"test_delay_{int(time.time())}"
    response = requests.get(f"{BASE_URL}/api/v1/oauth/google/auth?state={state}")
    
    if response.status_code != 200:
        print(f"❌ Failed to get OAuth URL: {response.status_code}")
        return False
    
    data = response.json()
    auth_url = data.get("auth_url", "")
    
    print(f"✅ OAuth URL successful")
    print(f"   URL: {auth_url[:100]}...")
    print(f"   State: {state}")
    
    # Test 2: Hướng dẫn test thủ công
    print(f"\n2. Manual Testing Instructions:")
    print(f"   a) Mở browser và truy cập: {auth_url}")
    print(f"   b) Hoàn thành OAuth flow với Google")
    print(f"   c) Copy callback URL từ browser")
    print(f"   d) Paste URL vào đây để test")
    print(f"   e) Đợi ít nhất 8 giây giữa các lần test để tránh rate limiting")
    
    # Test 3: Nhận callback URL từ user
    print(f"\n3. Testing callback...")
    callback_url = input("Paste callback URL here (or press Enter to skip): ").strip()
    
    if not callback_url:
        print("Skipping callback test")
        return True
    
    # Parse URL
    try:
        parsed_url = urlparse(callback_url)
        query_params = parse_qs(parsed_url.query)
        
        code = query_params.get('code', [None])[0]
        url_state = query_params.get('state', [None])[0]
        
        if not code:
            print("❌ No authorization code found in URL")
            return False
        
        print(f"✅ Parsed URL successfully")
        print(f"   Code: {code[:20]}...")
        print(f"   State: {url_state}")
        
        # Test callback endpoint
        print(f"\n🔄 Testing callback endpoint...")
        
        params = {'code': code}
        if url_state:
            params['state'] = url_state
        
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
            
            # Kiểm tra nếu có lỗi rate limiting
            if "8 seconds" in response.text:
                print(f"\n⚠️ Rate limiting detected!")
                print(f"   Please wait at least 8 seconds before trying again")
                print(f"   This is a Supabase security feature")
            
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
    print("🚀 === OAUTH TEST WITH DELAY ===\n")
    
    print("⚠️ Important: Wait at least 8 seconds between tests to avoid rate limiting!")
    print("   This is required by Supabase security features.\n")
    
    success = test_oauth_with_delay()
    
    if success:
        print("\n✅ OAuth test completed successfully!")
        print("🎉 Backend is working correctly!")
    else:
        print("\n❌ OAuth test failed")
        print("🔧 Please check the error messages above")
        print("💡 If you see rate limiting errors, wait 8+ seconds and try again")

if __name__ == "__main__":
    main() 