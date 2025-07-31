#!/usr/bin/env python3
"""
Test script cho User API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_user_endpoints():
    """Test các user endpoints"""
    
    print("🚀 === USER API TEST ===")
    
    # Test 1: Validate session (không có token)
    print("\n🔍 Test 1: Validate session (no token)")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/user/validate-session", 
                               json={"session_token": "invalid_token"})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Get profile (không có token)
    print("\n🔍 Test 2: Get profile (no token)")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/user/profile")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Update profile (không có token)
    print("\n🔍 Test 3: Update profile (no token)")
    try:
        response = requests.put(f"{BASE_URL}/api/v1/user/profile", 
                              json={"username": "test_user"})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Logout (không có token)
    print("\n🔍 Test 4: Logout (no token)")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/user/logout")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Get /me endpoint (alias)
    print("\n🔍 Test 5: Get /me endpoint (alias)")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/user/me")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 6: Update /me endpoint (alias)
    print("\n🔍 Test 6: Update /me endpoint (alias)")
    try:
        response = requests.put(f"{BASE_URL}/api/v1/user/me", 
                              json={"username": "test_user"})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n✅ User API test completed!")

def test_with_valid_session():
    """Test với session token hợp lệ (cần OAuth login trước)"""
    
    print("\n🔍 Test với session token hợp lệ:")
    print("Để test với session token thực, bạn cần:")
    print("1. Login qua OAuth để lấy session token")
    print("2. Sử dụng token đó để test các endpoints")
    print("3. Hoặc tạo mock session token trong database")

if __name__ == "__main__":
    test_user_endpoints()
    test_with_valid_session() 