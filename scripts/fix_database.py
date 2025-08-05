#!/usr/bin/env python3
"""
Script để kiểm tra và sửa lỗi database
"""

import sys
import os
from pathlib import Path

# Thêm thư mục gốc vào Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.supabase_service import SupabaseService
from app.core.config import settings


def check_database_schema():
    """Kiểm tra schema database"""
    try:
        supabase_service = SupabaseService()
        
        print("🔍 Kiểm tra database schema...")
        
        # Kiểm tra bảng user_profiles
        try:
            response = supabase_service.supabase.table('user_profiles').select('*').limit(1).execute()
            print("✅ Bảng user_profiles tồn tại")
        except Exception as e:
            print(f"❌ Lỗi với bảng user_profiles: {e}")
            return False
        
        # Kiểm tra column role
        try:
            # Thử query với role
            response = supabase_service.supabase.table('user_profiles').select('role').limit(1).execute()
            print("✅ Column 'role' tồn tại")
        except Exception as e:
            print(f"❌ Column 'role' không tồn tại: {e}")
            print("💡 Chạy script sql/add_role_column.sql để thêm column role")
            return False
        
        # Kiểm tra bảng novels
        try:
            response = supabase_service.supabase.table('novels').select('*').limit(1).execute()
            print("✅ Bảng novels tồn tại")
        except Exception as e:
            print(f"❌ Lỗi với bảng novels: {e}")
            return False
        
        # Kiểm tra bảng chapters
        try:
            response = supabase_service.supabase.table('chapters').select('*').limit(1).execute()
            print("✅ Bảng chapters tồn tại")
        except Exception as e:
            print(f"❌ Lỗi với bảng chapters: {e}")
            return False
        
        print("🎉 Database schema OK!")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi kiểm tra database: {e}")
        return False


def add_role_column():
    """Thêm column role vào user_profiles"""
    try:
        supabase_service = SupabaseService()
        
        print("🔧 Thêm column role...")
        
        # Thực hiện SQL để thêm column
        sql = """
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'user_profiles' 
                AND column_name = 'role'
            ) THEN
                ALTER TABLE user_profiles ADD COLUMN role VARCHAR(20) DEFAULT 'user';
                ALTER TABLE user_profiles ADD CONSTRAINT check_role CHECK (role IN ('user', 'admin'));
                RAISE NOTICE 'Added role column to user_profiles table';
            ELSE
                RAISE NOTICE 'Role column already exists in user_profiles table';
            END IF;
        END $$;
        """
        
        # Thực hiện SQL
        response = supabase_service.supabase.rpc('exec_sql', {'sql': sql}).execute()
        print("✅ Đã thêm column role")
        
        # Cập nhật users hiện tại
        update_sql = "UPDATE user_profiles SET role = 'user' WHERE role IS NULL;"
        supabase_service.supabase.rpc('exec_sql', {'sql': update_sql}).execute()
        print("✅ Đã cập nhật users hiện tại")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi thêm column role: {e}")
        return False


def list_users():
    """Liệt kê users hiện tại"""
    try:
        supabase_service = SupabaseService()
        
        print("👥 Danh sách users:")
        
        response = supabase_service.supabase.table('user_profiles').select('id, username, email, role').execute()
        
        for user in response.data:
            print(f"  - {user['username']} ({user['email']}) - Role: {user.get('role', 'N/A')} - ID: {user['id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi liệt kê users: {e}")
        return False


def main():
    print("🔧 Database Fix Tool")
    print("=" * 50)
    
    # Kiểm tra schema
    if not check_database_schema():
        print("\n🔧 Thử sửa lỗi...")
        if add_role_column():
            print("✅ Đã sửa lỗi thành công!")
        else:
            print("❌ Không thể sửa lỗi tự động")
            print("💡 Vui lòng chạy script sql/add_role_column.sql trên Supabase")
            return
    
    # Liệt kê users
    print("\n" + "=" * 50)
    list_users()
    
    print("\n✅ Database check hoàn thành!")


if __name__ == "__main__":
    main() 