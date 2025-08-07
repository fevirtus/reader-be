#!/usr/bin/env python3
"""
Script để test UserService trực tiếp với service key
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client
from app.core.config import settings

def test_user_service_direct():
    """Test UserService methods với service key"""
    try:
        # Sử dụng service key để bypass RLS
        supabase = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )
        
        user_id = "ce8e6da9-c07a-44cd-b058-ec8360b7a783"
        
        print(f"Testing với service key, user ID: {user_id}")
        
        # Test get_user_profile
        print("\n1. Testing get_user_profile với service key...")
        response = supabase.table('user_profiles').select('*').eq('id', user_id).execute()
        print(f"Response data: {response.data}")
        
        if response.data:
            profile = response.data[0]
            print(f"✅ Found profile: {profile}")
            
            # Test is_admin
            print("\n2. Testing is_admin...")
            role = profile.get('role')
            print(f"User role: {role}")
            is_admin = role == 'admin'
            print(f"Is admin: {is_admin}")
            
            # Test get_all_users
            print("\n3. Testing get_all_users...")
            all_users_response = supabase.table('user_profiles').select('*').execute()
            print(f"All users count: {len(all_users_response.data)}")
            for user in all_users_response.data:
                print(f"  - {user.get('username', 'Unknown')} ({user.get('email', 'No email')}) - Role: {user.get('role', 'No role')}")
        else:
            print("❌ No profile found")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_user_service_direct() 