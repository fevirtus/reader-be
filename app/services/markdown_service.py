import markdown
import os
from typing import Optional
from app.core.config import settings


class MarkdownService:
    def __init__(self):
        self.storage_path = settings.storage_path
        self.md = markdown.Markdown(extensions=['extra', 'codehilite'])
    
    def read_markdown_file(self, file_path: str) -> Optional[str]:
        """Đọc nội dung từ file markdown"""
        try:
            full_path = os.path.join(self.storage_path, file_path)
            if not os.path.exists(full_path):
                return None
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"Error reading markdown file: {e}")
            return None
    
    def convert_to_html(self, markdown_content: str) -> str:
        """Chuyển đổi markdown thành HTML"""
        return self.md.convert(markdown_content)
    
    def get_word_count(self, content: str) -> int:
        """Đếm số từ trong nội dung"""
        return len(content.split())
    
    def save_markdown_file(self, file_path: str, content: str) -> bool:
        """Lưu nội dung vào file markdown"""
        try:
            full_path = os.path.join(self.storage_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving markdown file: {e}")
            return False
    
    def delete_markdown_file(self, file_path: str) -> bool:
        """Xóa file markdown"""
        try:
            full_path = os.path.join(self.storage_path, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting markdown file: {e}")
            return False 