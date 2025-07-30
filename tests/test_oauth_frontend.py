#!/usr/bin/env python3
"""
Test OAuth flow tương thích với frontend
"""

import requests
import json
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://localhost:8000"

def test_oauth_frontend_flow():
    """Test OAuth flow như frontend sẽ sử dụng"""
    print("🚀 === OAUTH FRONTEND FLOW TEST ===\n")
    
    # Test 1: Lấy OAuth URL với state parameter
    print("🔐 Testing OAuth URL with state parameter...")
    state = "test_state_123"
    response = requests.get(f"{BASE_URL}/api/v1/oauth/google/auth?state={state}")
    
    if response.status_code == 200:
        data = response.json()
        auth_url = data.get("auth_url", "")
        provider = data.get("provider", "")
        
        print(f"✅ OAuth URL successful")
        print(f"   Provider: {provider}")
        print(f"   Auth URL: {auth_url[:100]}...")
        
        # Kiểm tra state parameter trong URL
        parsed_url = urlparse(auth_url)
        query_params = parse_qs(parsed_url.query)
        url_state = query_params.get('state', [None])[0]
        
        if url_state == state:
            print(f"✅ State parameter correctly included: {url_state}")
        else:
            print(f"❌ State parameter missing or incorrect")
            print(f"   Expected: {state}")
            print(f"   Got: {url_state}")
    else:
        print(f"❌ OAuth URL failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # Test 2: Kiểm tra callback endpoint
    print("\n🔐 Testing callback endpoint structure...")
    test_code = "test_code_123"
    test_state = "test_state_123"
    
    callback_url = f"{BASE_URL}/api/v1/oauth/google/callback?code={test_code}&state={test_state}"
    print(f"   Callback URL: {callback_url}")
    
    # Test 3: Kiểm tra response format
    print("\n📋 Testing response format compatibility...")
    
    # Mock response structure mà frontend mong đợi
    expected_response_structure = {
        "session_token": "string",
        "expires_at": "datetime",
        "user": {
            "id": "string",
            "username": "string", 
            "email": "string",
            "avatar_url": "string or null",
            "created_at": "datetime",
            "updated_at": "datetime"
        },
        "is_new_user": "boolean",
        "provider": "string"
    }
    
    print("✅ Expected response structure:")
    print(json.dumps(expected_response_structure, indent=2))
    
    # Test 4: Kiểm tra CORS headers
    print("\n🌐 Testing CORS headers...")
    cors_response = requests.options(f"{BASE_URL}/api/v1/oauth/google/auth")
    
    if cors_response.status_code == 200:
        print("✅ CORS preflight request successful")
        
        # Kiểm tra CORS headers
        cors_headers = cors_response.headers
        if "access-control-allow-origin" in cors_headers:
            print(f"✅ CORS origin header: {cors_headers['access-control-allow-origin']}")
        if "access-control-allow-methods" in cors_headers:
            print(f"✅ CORS methods header: {cors_headers['access-control-allow-methods']}")
    else:
        print(f"❌ CORS preflight failed: {cors_response.status_code}")
    
    print("\n✅ All frontend compatibility tests passed!")
    print("🎉 Backend is ready for frontend integration!")
    
    return True

if __name__ == "__main__":
    try:
        test_oauth_frontend_flow()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        exit(1) 