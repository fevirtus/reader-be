#!/usr/bin/env python3
"""
Script để tạo admin user đầu tiên
Sử dụng: python scripts/create_admin.py <user_id>
"""

import sys
import os
from pathlib import Path

# Thêm thư mục gốc vào Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.supabase_service import SupabaseService
from app.core.config import settings


def create_admin_user(user_id: str):
    """Tạo admin user"""
    try:
        supabase_service = SupabaseService()
        
        # Kiểm tra user có tồn tại không
        user_response = supabase_service.supabase_admin.table('user_profiles').select('*').eq('id', user_id).execute()
        
        if not user_response.data:
            print(f"❌ User {user_id} không tồn tại")
            return False
        
        # Cập nhật role thành admin
        update_response = supabase_service.supabase_admin.table('user_profiles').update({
            'role': 'admin'
        }).eq('id', user_id).execute()
        
        if update_response.data:
            print(f"✅ Đã cập nhật user {user_id} thành admin")
            return True
        else:
            print(f"❌ Không thể cập nhật user {user_id}")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False


def main():
    if len(sys.argv) != 2:
        print("Sử dụng: python scripts/create_admin.py <user_id>")
        sys.exit(1)
    
    user_id = sys.argv[1]
    success = create_admin_user(user_id)
    
    if success:
        print("🎉 Tạo admin thành công!")
    else:
        print("💥 Tạo admin thất bại!")
        sys.exit(1)


if __name__ == "__main__":
    main() 