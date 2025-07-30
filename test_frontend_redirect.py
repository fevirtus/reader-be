#!/usr/bin/env python3
"""
Test frontend redirect functionality
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_frontend_config():
    """Test frontend config endpoint"""
    print("🔧 === TESTING FRONTEND CONFIG ===\n")
    
    # Test 1: Frontend config endpoint
    print("1. Testing frontend config endpoint...")
    response = requests.get(f"{BASE_URL}/api/v1/oauth/frontend-config")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Frontend config successful")
        print(f"   Frontend redirect URI: {data.get('frontend_redirect_uri', 'N/A')}")
        print(f"   OAuth enabled: {data.get('oauth_enabled', 'N/A')}")
        print(f"   Providers: {data.get('providers', [])}")
    else:
        print(f"❌ Frontend config failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    return True

def test_redirect_endpoint():
    """Test redirect endpoint"""
    print("\n2. Testing redirect endpoint...")
    
    # Test với mock code (sẽ fail nhưng test structure)
    mock_code = "mock_auth_code_123"
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/oauth/google/callback/redirect?code={mock_code}")
        
        if response.status_code == 302:  # Redirect response
            redirect_url = response.headers.get('location', '')
            print("✅ Redirect endpoint working")
            print(f"   Redirect URL: {redirect_url}")
            
            # Kiểm tra URL có chứa frontend URI không
            if "localhost:3000/callback" in redirect_url:
                print("✅ Correct frontend redirect URI")
            else:
                print("❌ Wrong frontend redirect URI")
                print(f"   Expected: localhost:3000/callback")
                print(f"   Got: {redirect_url}")
        else:
            print(f"❌ Redirect endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Redirect test error: {e}")

def test_custom_redirect_uri():
    """Test với custom redirect URI"""
    print("\n3. Testing custom redirect URI...")
    
    mock_code = "mock_auth_code_456"
    custom_redirect = "http://localhost:3000/custom-callback"
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/oauth/google/callback/redirect",
            params={
                'code': mock_code,
                'redirect_uri': custom_redirect
            }
        )
        
        if response.status_code == 302:
            redirect_url = response.headers.get('location', '')
            print("✅ Custom redirect URI working")
            print(f"   Redirect URL: {redirect_url}")
            
            if custom_redirect in redirect_url:
                print("✅ Custom redirect URI applied correctly")
            else:
                print("❌ Custom redirect URI not applied")
        else:
            print(f"❌ Custom redirect failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Custom redirect test error: {e}")

def main():
    """Main function"""
    print("🚀 === FRONTEND REDIRECT TEST ===\n")
    
    # Test 1: Frontend config
    if not test_frontend_config():
        print("\n❌ Frontend config test failed")
        return
    
    # Test 2: Redirect endpoint
    test_redirect_endpoint()
    
    # Test 3: Custom redirect URI
    test_custom_redirect_uri()
    
    print("\n✅ All frontend redirect tests completed!")
    print("\n📋 Frontend Integration:")
    print("1. Frontend có thể gọi: GET /api/v1/oauth/frontend-config")
    print("2. Frontend có thể redirect về: GET /api/v1/oauth/google/callback/redirect")
    print("3. Backend sẽ redirect về: http://localhost:3000/callback")
    print("4. URL sẽ có format: http://localhost:3000/callback?session_token=...&is_new_user=...")

if __name__ == "__main__":
    main() 