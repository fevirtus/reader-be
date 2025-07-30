#!/usr/bin/env python3
"""
Test OAuth flow thực tế với redirect về frontend
"""

import requests
import webbrowser
import time

BASE_URL = "http://localhost:8000"

def test_oauth_real_flow():
    """Test OAuth flow thực tế với redirect"""
    print("🚀 === OAUTH REAL FLOW TEST ===\n")
    
    # Test 1: Lấy OAuth URL
    print("1. Getting OAuth URL...")
    state = f"test_real_{int(time.time())}"
    response = requests.get(f"{BASE_URL}/api/v1/oauth/google/auth?state={state}")
    
    if response.status_code != 200:
        print(f"❌ Failed to get OAuth URL: {response.status_code}")
        return False
    
    data = response.json()
    auth_url = data.get("auth_url", "")
    
    print(f"✅ OAuth URL successful")
    print(f"   URL: {auth_url[:100]}...")
    print(f"   State: {state}")
    
    # Test 2: Mở browser để test thực tế
    print(f"\n2. Opening browser for real OAuth test...")
    print(f"   This will open Google OAuth in your browser.")
    print(f"   After authentication, you'll be redirected to frontend.")
    print(f"   Please check the browser and note the final URL.")
    
    try:
        webbrowser.open(auth_url)
        print("✅ Browser opened successfully")
        print("   Please complete the OAuth flow in your browser")
        print("   You should be redirected to: http://localhost:3000/callback?session_token=...")
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print(f"   Please manually open this URL: {auth_url}")
    
    # Test 3: Hướng dẫn test thủ công
    print(f"\n3. Manual Testing Instructions:")
    print(f"   a) Complete OAuth flow in browser")
    print(f"   b) You should be redirected to: http://localhost:3000/callback?session_token=...")
    print(f"   c) Check if session_token is present in URL")
    print(f"   d) Verify frontend handles the callback correctly")
    
    # Test 4: Kiểm tra server logs
    print(f"\n4. Server Logs to Check:")
    print(f"   - OAuth callback processing")
    print(f"   - User profile creation/update")
    print(f"   - Session token generation")
    print(f"   - Redirect to frontend")
    print(f"   - Error messages (if any)")
    
    print(f"\n✅ Real OAuth flow test setup complete!")
    print(f"🎉 Please complete the OAuth flow in your browser")
    print(f"   and check if you're redirected to frontend correctly.")
    
    return True

def test_frontend_config():
    """Test frontend config"""
    print(f"\n5. Testing frontend config...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/oauth/frontend-config")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Frontend config successful")
            print(f"   Frontend redirect URI: {data.get('frontend_redirect_uri', 'N/A')}")
            print(f"   OAuth enabled: {data.get('oauth_enabled', 'N/A')}")
            print(f"   Providers: {data.get('providers', [])}")
        else:
            print(f"❌ Frontend config failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Frontend config error: {e}")

def main():
    """Main function"""
    print("🚀 === OAUTH REAL FLOW TEST ===\n")
    
    print("⚠️ Important: This test will open Google OAuth in your browser!")
    print("   Make sure your frontend is running on http://localhost:3000")
    print("   and has a /callback page to handle the redirect.\n")
    
    # Test OAuth flow
    test_oauth_real_flow()
    
    # Test frontend config
    test_frontend_config()
    
    print(f"\n✅ All tests completed!")
    print(f"\n📋 Expected Flow:")
    print(f"1. Browser opens Google OAuth")
    print(f"2. User completes authentication")
    print(f"3. Google redirects to: http://localhost:8000/api/v1/oauth/google/callback")
    print(f"4. Backend processes OAuth and redirects to: http://localhost:3000/callback")
    print(f"5. Frontend receives session_token and handles login")

if __name__ == "__main__":
    main() 