#!/usr/bin/env python3
"""
Test script để debug OAuth callback
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

def test_oauth_debug():
    """Test OAuth với debug logging"""
    print("🚀 === OAUTH DEBUG TEST ===")
    print()
    
    # Test 1: Get OAuth URL
    print("🔐 Getting OAuth URL...")
    try:
        response = requests.get(f"{API_BASE}/oauth/google/auth")
        if response.status_code == 200:
            data = response.json()
            auth_url = data['auth_url']
            print(f"✅ OAuth URL: {auth_url[:100]}...")
            
            # Extract state parameter
            import urllib.parse
            parsed = urllib.parse.urlparse(auth_url)
            params = urllib.parse.parse_qs(parsed.query)
            state = params.get('state', [''])[0]
            print(f"📋 State parameter: {state}")
            
            return auth_url, state
        else:
            print(f"❌ Failed to get OAuth URL: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Error getting OAuth URL: {e}")
        return None, None

def test_check_user_exists():
    """Test check user exists endpoint"""
    print("\n👤 Testing check user exists...")
    
    test_email = "test@example.com"
    
    try:
        response = requests.get(f"{API_BASE}/auth/check-email?email={test_email}")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Check email successful")
            print(f"   Email: {data['email']}")
            print(f"   Exists: {data['exists']}")
            return True
        else:
            print(f"❌ Check email failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Check email error: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🗄️ Testing database connection...")
    
    try:
        # Test novels endpoint (public)
        response = requests.get(f"{API_BASE}/novels")
        print(f"Novels endpoint status: {response.status_code}")
        
        # Test health endpoint
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health endpoint status: {response.status_code}")
        
        print("✅ Database connection working")
        return True
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 === OAUTH DEBUG TEST ===")
    print()
    
    # Test 1: Database connection
    if not test_database_connection():
        print("\n❌ Database connection failed")
        sys.exit(1)
    
    # Test 2: Check user exists
    if not test_check_user_exists():
        print("\n❌ Check user exists failed")
        sys.exit(1)
    
    # Test 3: Get OAuth URL
    auth_url, state = test_oauth_debug()
    if not auth_url:
        print("\n❌ OAuth URL failed")
        sys.exit(1)
    
    print("\n✅ All debug tests passed!")
    print("\n📋 Next steps:")
    print("1. Visit OAuth URL in browser:")
    print(f"   {auth_url}")
    print("2. Complete Google OAuth flow")
    print("3. Check server logs for debug output")
    print("4. Verify user creation/login")

if __name__ == "__main__":
    main() 