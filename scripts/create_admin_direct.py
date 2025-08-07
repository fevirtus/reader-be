#!/usr/bin/env python3
"""
Script để tạo admin user trực tiếp với service key
"""

import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client
from app.core.config import settings

def create_admin_user(email: str, username: str = None):
    """Tạo admin user trực tiếp với service key"""
    try:
        # Sử dụng service key để bypass RLS
        supabase = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key  # Sử dụng service role key
        )
        
        # Kiểm tra user đã tồn tại chưa
        existing_user = supabase.table('user_profiles').select('*').eq('email', email).execute()
        
        if existing_user.data:
            print(f"User với email {email} đã tồn tại!")
            user = existing_user.data[0]
            if user.get('role') == 'admin':
                print("User đã là admin!")
                return user
            else:
                # Cập nhật role thành admin
                supabase.table('user_profiles').update({
                    'role': 'admin'
                }).eq('email', email).execute()
                print(f"Đã cập nhật user {email} thành admin!")
                return user
        
        # Tạo user mới với role admin
        user_data = {
            'id': str(uuid.uuid4()),
            'email': email,
            'username': username or email.split('@')[0],
            'role': 'admin'
        }
        
        response = supabase.table('user_profiles').insert(user_data).execute()
        
        if response.data:
            print(f"Đã tạo admin user thành công: {email}")
            return response.data[0]
        else:
            print("Lỗi khi tạo admin user!")
            return None
            
    except Exception as e:
        print(f"Lỗi: {e}")
        return None

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python create_admin_direct.py <email> [username]")
        print("Example: python create_admin_direct.py admin@example.com 'Admin User'")
        sys.exit(1)
    
    email = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Tạo admin user với email: {email}")
    if username:
        print(f"Username: {username}")
    
    user = create_admin_user(email, username)
    
    if user:
        print("Thành công!")
        print(f"User ID: {user['id']}")
        print(f"Email: {user['email']}")
        print(f"Username: {user['username']}")
        print(f"Role: {user['role']}")
    else:
        print("Thất bại!")
        sys.exit(1)

if __name__ == "__main__":
    main() 