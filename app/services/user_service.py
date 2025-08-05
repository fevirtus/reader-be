from typing import List, Optional, Dict, Any
from app.services.supabase_service import SupabaseService


class UserService:
    def __init__(self):
        self.supabase_service = SupabaseService()
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Lấy thông tin profile của user"""
        try:
            response = self.supabase_service.supabase_admin.table('user_profiles').select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    def update_user_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Cập nhật thông tin profile của user"""
        try:
            self.supabase_service.supabase_admin.table('user_profiles').update(profile_data).eq('id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False
    
    def is_admin(self, user_id: str) -> bool:
        """Kiểm tra user có role admin không"""
        try:
            profile = self.get_user_profile(user_id)
            return profile and profile.get('role') == 'admin'
        except Exception as e:
            print(f"Error checking admin role: {e}")
            return False
    
    def change_user_role(self, admin_user_id: str, target_user_id: str, new_role: str) -> bool:
        """Thay đổi role của user (chỉ admin mới có quyền)"""
        try:
            # Kiểm tra admin có quyền không
            if not self.is_admin(admin_user_id):
                print(f"User {admin_user_id} is not admin")
                return False
            
            # Kiểm tra role hợp lệ
            if new_role not in ['user', 'admin']:
                print(f"Invalid role: {new_role}")
                return False
            
            # Thay đổi role
            self.supabase_service.supabase_admin.table('user_profiles').update({
                'role': new_role
            }).eq('id', target_user_id).execute()
            
            print(f"Changed user {target_user_id} role to {new_role}")
            return True
        except Exception as e:
            print(f"Error changing user role: {e}")
            return False
    
    def get_all_users(self, admin_user_id: str) -> List[Dict]:
        """Lấy danh sách tất cả users (chỉ admin)"""
        try:
            if not self.is_admin(admin_user_id):
                return []
            
            response = self.supabase_service.supabase_admin.table('user_profiles').select('*').execute()
            return response.data
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def get_users_by_role(self, admin_user_id: str, role: str) -> List[Dict]:
        """Lấy danh sách users theo role (chỉ admin)"""
        try:
            if not self.is_admin(admin_user_id):
                return []
            
            response = self.supabase_service.supabase_admin.table('user_profiles').select('*').eq('role', role).execute()
            return response.data
        except Exception as e:
            print(f"Error getting users by role: {e}")
            return [] 