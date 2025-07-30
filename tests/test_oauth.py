#!/usr/bin/env python3
"""
Test script cho OAuth functionality
"""

import os
import sys
import requests
import time
from dotenv import load_dotenv

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_oauth_providers():
    """Test get OAuth providers"""
    print("\n🔐 Testing OAuth providers...")
    
    try:
        response = requests.get(f"{API_BASE}/oauth/providers")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ OAuth providers successful")
            print(f"   Providers: {data.get('providers', [])}")
            print(f"   Enabled: {data.get('enabled', False)}")
            return True
        else:
            print(f"❌ OAuth providers failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OAuth providers error: {e}")
        return False

def test_google_auth_url():
    """Test Google OAuth URL generation"""
    print("\n🔐 Testing Google OAuth URL...")
    
    try:
        response = requests.get(f"{API_BASE}/oauth/google/auth")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Google OAuth URL successful")
            print(f"   Provider: {data.get('provider', '')}")
            print(f"   Auth URL: {data.get('auth_url', '')[:50]}...")
            return True
        else:
            print(f"❌ Google OAuth URL failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Google OAuth URL error: {e}")
        return False

def test_google_callback_invalid():
    """Test Google OAuth callback với invalid code"""
    print("\n🔐 Testing Google OAuth callback (invalid)...")
    
    try:
        response = requests.get(f"{API_BASE}/oauth/google/callback?code=invalid_code")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 400:
            print("✅ Google OAuth callback (invalid) successful")
            print("   Expected error for invalid code")
            return True
        else:
            print(f"❌ Google OAuth callback failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Google OAuth callback error: {e}")
        return False

def test_google_verify_invalid():
    """Test Google token verification với invalid token"""
    print("\n🔐 Testing Google token verification (invalid)...")
    
    try:
        response = requests.post(f"{API_BASE}/oauth/google/verify?token=invalid_token")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if not data.get('valid', True):
                print("✅ Google token verification (invalid) successful")
                print("   Expected invalid token result")
                return True
            else:
                print("❌ Expected invalid token but got valid")
                return False
        else:
            print(f"❌ Google token verification failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Google token verification error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 === OAUTH FUNCTIONALITY TEST ===")
    print()
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed")
        sys.exit(1)
    
    # Test 2: OAuth providers
    if not test_oauth_providers():
        print("\n❌ OAuth providers failed")
        sys.exit(1)
    
    # Test 3: Google OAuth URL (sẽ fail nếu chưa config Google OAuth)
    if not test_google_auth_url():
        print("\n❌ Google OAuth URL failed")
        print("Note: This is expected if Google OAuth is not configured")
        print("To configure Google OAuth:")
        print("1. Create Google OAuth credentials at https://console.developers.google.com")
        print("2. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to .env")
        sys.exit(1)
    
    # Test 4: Google OAuth callback (invalid)
    if not test_google_callback_invalid():
        print("\n❌ Google OAuth callback failed")
        sys.exit(1)
    
    # Test 5: Google token verification (invalid)
    if not test_google_verify_invalid():
        print("\n❌ Google token verification failed")
        sys.exit(1)
    
    print("\n✅ All OAuth tests passed!")
    print("🎉 OAuth functionality is working correctly!")

if __name__ == "__main__":
    main() 