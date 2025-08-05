import markdown
import os
from typing import Optional
from app.core.config import settings


class MarkdownService:
    def __init__(self):
        self.storage_path = settings.storage_path
        self.md = markdown.Markdown(extensions=['extra', 'codehilite'])
    
    def read_markdown_file(self, file_path: str, novel_title: str = None) -> Optional[str]:
        """Đọc nội dung từ file markdown"""
        try:
            if not os.path.exists(self.storage_path):
                print(f"Storage path not found: {self.storage_path}")
                return None
            
            # Nếu có novel_title, tìm trong directory cụ thể
            if novel_title:
                novel_path = os.path.join(self.storage_path, novel_title)
                full_path = os.path.join(novel_path, file_path)
                if os.path.exists(full_path):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return content
                else:
                    print(f"File not found: {full_path}")
                    return None
            
            # Nếu không có novel_title, tìm trong tất cả directories
            for novel_dir in os.listdir(self.storage_path):
                novel_path = os.path.join(self.storage_path, novel_dir)
                if os.path.isdir(novel_path):
                    full_path = os.path.join(novel_path, file_path)
                    if os.path.exists(full_path):
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        return content
            
            print(f"File not found: {file_path}")
            return None
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