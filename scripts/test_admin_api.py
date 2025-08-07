#!/usr/bin/env python3
"""
Script để test admin API với token thực
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

def test_admin_api():
    """Test admin API với token thực"""
    try:
        # Token từ localStorage của frontend (cần copy từ browser)
        token = input("Nhập session token từ browser: ").strip()
        
        if not token:
            print("❌ Không có token!")
            return
        
        headers = {'Authorization': f'Bearer {token}'}
        
        print("🔍 Testing admin APIs...")
        
        # Test check-admin
        print("\n1. Testing /api/v1/admin/check-admin...")
        response = requests.get('http://localhost:8000/api/v1/admin/check-admin', headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test stats
        print("\n2. Testing /api/v1/admin/stats...")
        response = requests.get('http://localhost:8000/api/v1/admin/stats', headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test activities
        print("\n3. Testing /api/v1/admin/activities...")
        response = requests.get('http://localhost:8000/api/v1/admin/activities', headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test users
        print("\n4. Testing /api/v1/admin/users...")
        response = requests.get('http://localhost:8000/api/v1/admin/users', headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_admin_api() 