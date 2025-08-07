#!/usr/bin/env python3
"""
Script để test UserService trực tiếp
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.user_service import UserService

def test_user_service():
    """Test UserService methods"""
    try:
        user_service = UserService()
        
        # Test user ID từ log
        user_id = "ce8e6da9-c07a-44cd-b058-ec8360b7a783"
        
        print(f"Testing UserService with user ID: {user_id}")
        
        # Test get_user_profile
        print("\n1. Testing get_user_profile...")
        profile = user_service.get_user_profile(user_id)
        print(f"Profile result: {profile}")
        
        # Test is_admin
        print("\n2. Testing is_admin...")
        is_admin = user_service.is_admin(user_id)
        print(f"Is admin result: {is_admin}")
        
        # Test get_all_users để xem tất cả users
        print("\n3. Testing get_all_users...")
        all_users = user_service.get_all_users(user_id)
        print(f"All users count: {len(all_users)}")
        for user in all_users:
            print(f"  - {user.get('username', 'Unknown')} ({user.get('email', 'No email')}) - Role: {user.get('role', 'No role')}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_user_service() 