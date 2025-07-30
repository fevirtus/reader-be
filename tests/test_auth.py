#!/usr/bin/env python3
"""
Test script cho authentication và reading features
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

def test_register():
    """Test user registration"""
    print("\n👤 Testing user registration...")
    
    register_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "username": "testuser"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/register", json=register_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ User registration successful")
            print(f"   Session token: {data['session_token'][:20]}...")
            return data['session_token']
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_login():
    """Test user login"""
    print("\n🔐 Testing user login...")
    
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ User login successful")
            print(f"   Session token: {data['session_token'][:20]}...")
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

def test_create_novel(session_token):
    """Test create novel"""
    print("\n📚 Testing create novel...")
    
    headers = {"session-token": session_token}
    novel_data = {
        "title": "Test Novel",
        "author": "Test Author",
        "description": "A test novel for authentication testing",
        "status": "ongoing"
    }
    
    try:
        response = requests.post(f"{API_BASE}/novels", json=novel_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Create novel successful")
            print(f"   Novel ID: {data['id']}")
            return data['id']
        else:
            print(f"❌ Create novel failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Create novel error: {e}")
        return None

def test_add_to_bookshelf(session_token, novel_id):
    """Test add to bookshelf"""
    print("\n📖 Testing add to bookshelf...")
    
    headers = {"session-token": session_token}
    bookshelf_data = {"novel_id": novel_id}
    
    try:
        response = requests.post(f"{API_BASE}/reading/bookshelf", json=bookshelf_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Add to bookshelf successful")
            print(f"   Bookshelf ID: {data['id']}")
            return True
        else:
            print(f"❌ Add to bookshelf failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Add to bookshelf error: {e}")
        return False

def test_get_bookshelf(session_token):
    """Test get bookshelf"""
    print("\n📚 Testing get bookshelf...")
    
    headers = {"session-token": session_token}
    
    try:
        response = requests.get(f"{API_BASE}/reading/bookshelf", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Get bookshelf successful")
            print(f"   Bookshelf items: {len(data)}")
            return True
        else:
            print(f"❌ Get bookshelf failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get bookshelf error: {e}")
        return False

def test_reading_stats(session_token):
    """Test reading stats"""
    print("\n📊 Testing reading stats...")
    
    headers = {"session-token": session_token}
    
    try:
        response = requests.get(f"{API_BASE}/reading/stats", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Get reading stats successful")
            print(f"   Novels read: {data['novels_read']}")
            print(f"   Chapters read: {data['chapters_read']}")
            print(f"   Bookshelf count: {data['bookshelf_count']}")
            return True
        else:
            print(f"❌ Get reading stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get reading stats error: {e}")
        return False

def test_logout(session_token):
    """Test logout"""
    print("\n🚪 Testing logout...")
    
    headers = {"session-token": session_token}
    
    try:
        response = requests.post(f"{API_BASE}/auth/logout", headers=headers)
        if response.status_code == 200:
            print("✅ Logout successful")
            return True
        else:
            print(f"❌ Logout failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Logout error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 === AUTHENTICATION & READING FEATURES TEST ===")
    print()
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed")
        sys.exit(1)
    
    # Test 2: Register user
    session_token = test_register()
    if not session_token:
        print("\n❌ User registration failed")
        sys.exit(1)
    
    # Test 3: Get profile
    if not test_get_profile(session_token):
        print("\n❌ Get profile failed")
        sys.exit(1)
    
    # Test 4: Create novel
    novel_id = test_create_novel(session_token)
    if not novel_id:
        print("\n❌ Create novel failed")
        sys.exit(1)
    
    # Test 5: Add to bookshelf
    if not test_add_to_bookshelf(session_token, novel_id):
        print("\n❌ Add to bookshelf failed")
        sys.exit(1)
    
    # Test 6: Get bookshelf
    if not test_get_bookshelf(session_token):
        print("\n❌ Get bookshelf failed")
        sys.exit(1)
    
    # Test 7: Get reading stats
    if not test_reading_stats(session_token):
        print("\n❌ Get reading stats failed")
        sys.exit(1)
    
    # Test 8: Logout
    if not test_logout(session_token):
        print("\n❌ Logout failed")
        sys.exit(1)
    
    print("\n✅ All authentication and reading tests passed!")
    print("🎉 Authentication and reading features are working correctly!")

if __name__ == "__main__":
    main() 