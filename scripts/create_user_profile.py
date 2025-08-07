#!/usr/bin/env python3
"""
Script để tạo user profile cho user hiện tại
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client
from app.core.config import settings

def create_user_profile(user_id: str, email: str, username: str = None, role: str = 'user'):
    """Tạo user profile"""
    try:
        # Sử dụng service role key để bypass RLS
        supabase = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )
        
        # Kiểm tra user đã tồn tại chưa
        existing_user = supabase.table('user_profiles').select('*').eq('id', user_id).execute()
        
        if existing_user.data:
            print(f"User profile với ID {user_id} đã tồn tại!")
            user = existing_user.data[0]
            print(f"Username: {user.get('username')}")
            print(f"Email: {user.get('email')}")
            print(f"Role: {user.get('role')}")
            return user
        
        # Tạo user profile mới
        user_data = {
            'id': user_id,
            'email': email,
            'username': username or email.split('@')[0],
            'role': role
        }
        
        response = supabase.table('user_profiles').insert(user_data).execute()
        
        if response.data:
            print(f"✅ Đã tạo user profile thành công!")
            user = response.data[0]
            print(f"ID: {user['id']}")
            print(f"Username: {user['username']}")
            print(f"Email: {user['email']}")
            print(f"Role: {user['role']}")
            return user
        else:
            print("❌ Lỗi khi tạo user profile!")
            return None
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return None

def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("Usage: python create_user_profile.py <user_id> <email> [username] [role]")
        print("Example: python create_user_profile.py ce8e6da9-c07a-44cd-b058-ec8360b7a783 test@example.com 'Test User' admin")
        sys.exit(1)
    
    user_id = sys.argv[1]
    email = sys.argv[2]
    username = sys.argv[3] if len(sys.argv) > 3 else None
    role = sys.argv[4] if len(sys.argv) > 4 else 'user'
    
    print(f"Tạo user profile với:")
    print(f"  User ID: {user_id}")
    print(f"  Email: {email}")
    print(f"  Username: {username or email.split('@')[0]}")
    print(f"  Role: {role}")
    
    user = create_user_profile(user_id, email, username, role)
    
    if user:
        print("\n✅ Thành công!")
    else:
        print("\n❌ Thất bại!")
        sys.exit(1)

if __name__ == "__main__":
    main() 