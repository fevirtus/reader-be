#!/usr/bin/env python3
"""
Script để test admin check API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

def test_admin_check():
    """Test admin check API"""
    try:
        # Test without token
        response = requests.get('http://localhost:8000/api/v1/admin/check-admin')
        print(f"Without token: {response.status_code} - {response.json()}")
        
        # Test with invalid token
        headers = {'Authorization': 'Bearer invalid-token'}
        response = requests.get('http://localhost:8000/api/v1/admin/check-admin', headers=headers)
        print(f"With invalid token: {response.status_code} - {response.json()}")
        
        # Test with valid token (you'll need to get a real token)
        # headers = {'Authorization': 'Bearer your-real-token'}
        # response = requests.get('http://localhost:8000/api/v1/admin/check-admin', headers=headers)
        # print(f"With valid token: {response.status_code} - {response.json()}")
        
    except Exception as e:
        print(f"Error: {e}")

def test_stats():
    """Test stats API"""
    try:
        # Test without token
        response = requests.get('http://localhost:8000/api/v1/admin/stats')
        print(f"Stats without token: {response.status_code} - {response.json()}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing admin APIs...")
    test_admin_check()
    print("\nTesting stats API...")
    test_stats() 