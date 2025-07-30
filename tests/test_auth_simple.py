#!/usr/bin/env python3
"""
Test script đơn giản cho authentication
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

def test_check_email_exists():
    """Test check email exists"""
    print("\n📧 Testing check email exists...")
    
    # Test với email không tồn tại
    test_email = f"nonexistent{int(time.time())}@example.com"
    
    try:
        response = requests.get(f"{API_BASE}/auth/check-email?email={test_email}")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Check email successful")
            print(f"   Email: {data['email']}")
            print(f"   Exists: {data['exists']}")
            return True
        else:
            print(f"❌ Check email failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Check email error: {e}")
        return False

def test_register_with_unique_email():
    """Test user registration với email unique"""
    print("\n👤 Testing user registration...")
    
    # Tạo email unique dựa trên timestamp
    import time
    timestamp = int(time.time())
    unique_email = f"test{timestamp}@example.com"
    
    register_data = {
        "email": unique_email,
        "password": "testpassword123",
        "username": f"testuser{timestamp}"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/register", json=register_data)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ User registration successful")
            print(f"   Session token: {data['session_token'][:20]}...")
            print(f"   Expires at: {data['expires_at']}")
            print(f"   User: {data['user']['username']}")
            return data['session_token']
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_register_duplicate_email():
    """Test user registration với email đã tồn tại"""
    print("\n👤 Testing duplicate email registration...")
    
    # Sử dụng email đã tồn tại
    duplicate_email = "test@example.com"
    
    register_data = {
        "email": duplicate_email,
        "password": "testpassword123",
        "username": "testuser_duplicate"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/register", json=register_data)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 400:
            data = response.json()
            if "already exists" in data.get('detail', '').lower():
                print("✅ Duplicate email check working")
                print(f"   Error: {data['detail']}")
                return True
            else:
                print(f"❌ Unexpected error: {data['detail']}")
                return False
        else:
            print(f"❌ Expected 400 but got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Duplicate email test error: {e}")
        return False

def test_login():
    """Test user login"""
    print("\n🔐 Testing user login...")
    
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ User login successful")
            print(f"   Session token: {data['session_token'][:20]}...")
            print(f"   Expires at: {data['expires_at']}")
            return data['session_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_get_profile(session_token):
    """Test get user profile"""
    print("\n👤 Testing get user profile...")
    
    headers = {"session-token": session_token}
    
    try:
        response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Get profile successful")
            print(f"   Username: {data['username']}")
            print(f"   Email: {data['email']}")
            return True
        else:
            print(f"❌ Get profile failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get profile error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 === SIMPLE AUTHENTICATION TEST ===")
    print()
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed")
        sys.exit(1)
    
    # Test 2: Check email exists
    if not test_check_email_exists():
        print("\n❌ Check email failed")
        sys.exit(1)
    
    # Test 3: Register user với email unique
    session_token = test_register_with_unique_email()
    if not session_token:
        print("\n❌ User registration failed")
        print("Note: This might be due to email confirmation requirement in Supabase")
        print("You can either:")
        print("1. Disable email confirmation in Supabase Auth settings")
        print("2. Use a real email address and confirm it")
        sys.exit(1)
    
    # Test 4: Test duplicate email registration
    if not test_register_duplicate_email():
        print("\n❌ Duplicate email test failed")
        sys.exit(1)
    
    # Test 5: Get profile
    if not test_get_profile(session_token):
        print("\n❌ Get profile failed")
        sys.exit(1)
    
    print("\n✅ All authentication tests passed!")
    print("🎉 Authentication is working correctly!")

if __name__ == "__main__":
    main() 