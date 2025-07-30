#!/usr/bin/env python3
"""
Test script đơn giản cho check email exists
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

def test_check_email_not_exists():
    """Test check email không tồn tại"""
    print("\n📧 Testing check email (not exists)...")
    
    # Test với email không tồn tại
    test_email = f"nonexistent{int(time.time())}@example.com"
    
    try:
        response = requests.get(f"{API_BASE}/auth/check-email?email={test_email}")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if not data['exists']:
                print("✅ Check email (not exists) successful")
                print(f"   Email: {data['email']}")
                print(f"   Exists: {data['exists']}")
                return True
            else:
                print("❌ Email should not exist but it does")
                return False
        else:
            print(f"❌ Check email failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Check email error: {e}")
        return False

def test_check_email_exists():
    """Test check email đã tồn tại"""
    print("\n📧 Testing check email (exists)...")
    
    # Test với email có thể đã tồn tại (nếu đã đăng ký trước đó)
    test_email = "test@example.com"
    
    try:
        response = requests.get(f"{API_BASE}/auth/check-email?email={test_email}")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Check email (exists) successful")
            print(f"   Email: {data['email']}")
            print(f"   Exists: {data['exists']}")
            return True
        else:
            print(f"❌ Check email failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Check email error: {e}")
        return False

def test_check_email_invalid():
    """Test check email với format không hợp lệ"""
    print("\n📧 Testing check email (invalid format)...")
    
    # Test với email không hợp lệ
    invalid_email = "invalid-email"
    
    try:
        response = requests.get(f"{API_BASE}/auth/check-email?email={invalid_email}")
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Check email (invalid) successful")
            print(f"   Email: {data['email']}")
            print(f"   Exists: {data['exists']}")
            return True
        else:
            print(f"❌ Check email failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Check email error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 === EMAIL CHECK TEST ===")
    print()
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed")
        sys.exit(1)
    
    # Test 2: Check email không tồn tại
    if not test_check_email_not_exists():
        print("\n❌ Check email (not exists) failed")
        sys.exit(1)
    
    # Test 3: Check email có thể đã tồn tại
    if not test_check_email_exists():
        print("\n❌ Check email (exists) failed")
        sys.exit(1)
    
    # Test 4: Check email format không hợp lệ
    if not test_check_email_invalid():
        print("\n❌ Check email (invalid) failed")
        sys.exit(1)
    
    print("\n✅ All email check tests passed!")
    print("🎉 Email check functionality is working correctly!")

if __name__ == "__main__":
    main() 