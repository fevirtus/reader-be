import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from app.core.config import settings


class CacheService:
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.default_ttl = 3600  # 1 giờ mặc định
    
    def _generate_key(self, prefix: str, identifier: Any) -> str:
        """Tạo cache key"""
        return f"{prefix}:{identifier}"
    
    def _is_expired(self, cache_entry: Dict) -> bool:
        """Kiểm tra cache entry có hết hạn không"""
        if 'expires_at' not in cache_entry:
            return True
        
        return datetime.now() > cache_entry['expires_at']
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Lưu data vào cache"""
        if ttl is None:
            ttl = self.default_ttl
        
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        self.cache[key] = {
            'data': value,
            'created_at': datetime.now(),
            'expires_at': expires_at,
            'ttl': ttl
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Lấy data từ cache"""
        if key not in self.cache:
            return None
        
        cache_entry = self.cache[key]
        
        if self._is_expired(cache_entry):
            del self.cache[key]
            return None
        
        return cache_entry['data']
    
    def delete(self, key: str) -> bool:
        """Xóa cache entry"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Xóa tất cả cache"""
        self.cache.clear()
    
    def cleanup_expired(self) -> int:
        """Dọn dẹp cache entries hết hạn"""
        expired_keys = []
        
        for key, entry in self.cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê cache"""
        total_entries = len(self.cache)
        expired_entries = sum(1 for entry in self.cache.values() if self._is_expired(entry))
        valid_entries = total_entries - expired_entries
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'memory_usage': len(json.dumps(self.cache, default=str))
        }


# Global cache instance
cache_service = CacheService() 