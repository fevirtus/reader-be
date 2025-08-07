#!/usr/bin/env python3
"""
Script để kiểm tra tất cả users trong database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.supabase_service import SupabaseService

def check_users():
    """Kiểm tra tất cả users"""
    try:
        supabase_service = SupabaseService()
        
        print("🔍 Checking all users in user_profiles table...")
        response = supabase_service.supabase.table('user_profiles').select('*').execute()
        
        print(f"📊 Total users found: {len(response.data)}")
        
        if response.data:
            print("\n📋 User details:")
            for i, user in enumerate(response.data, 1):
                print(f"  {i}. ID: {user.get('id')}")
                print(f"     Username: {user.get('username', 'N/A')}")
                print(f"     Email: {user.get('email', 'N/A')}")
                print(f"     Role: {user.get('role', 'N/A')}")
                print(f"     Created: {user.get('created_at', 'N/A')}")
                print()
        else:
            print("❌ No users found in user_profiles table")
            
        # Kiểm tra auth.users table (nếu có thể)
        print("\n🔍 Checking auth.users table...")
        try:
            auth_response = supabase_service.supabase.auth.admin.list_users()
            print(f"📊 Total auth users: {len(auth_response.users)}")
            
            for i, user in enumerate(auth_response.users, 1):
                print(f"  {i}. ID: {user.id}")
                print(f"     Email: {user.email}")
                print(f"     Created: {user.created_at}")
                print()
        except Exception as e:
            print(f"❌ Cannot access auth.users: {e}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users() 