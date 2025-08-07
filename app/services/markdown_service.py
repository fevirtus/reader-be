import markdown
import os
from typing import Optional
from app.core.config import settings


class ContentService:
    def __init__(self):
        self.storage_path = settings.storage_path
        self.md = markdown.Markdown(extensions=['extra', 'codehilite'])
    
    def read_content_file(self, file_path: str, novel_title: str = None) -> Optional[str]:
        """Đọc nội dung từ file (HTML hoặc markdown)"""
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
            novels_path = self.storage_path  # storage_path đã là ./storage
            if os.path.exists(novels_path):
                for novel_dir in os.listdir(novels_path):
                    novel_path = os.path.join(novels_path, novel_dir)
                    if os.path.isdir(novel_path):
                        full_path = os.path.join(novel_path, file_path)
                        if os.path.exists(full_path):
                            with open(full_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            return content
            
            print(f"File not found: {file_path}")
            return None
        except Exception as e:
            print(f"Error reading content file: {e}")
            return None
    
    def read_markdown_file(self, file_path: str, novel_title: str = None) -> Optional[str]:
        """Đọc nội dung từ file markdown (backward compatibility)"""
        return self.read_content_file(file_path, novel_title)
    
    def convert_to_html(self, markdown_content: str) -> str:
        """Chuyển đổi markdown thành HTML"""
        return self.md.convert(markdown_content)
    
    def get_word_count(self, content: str) -> int:
        """Đếm số từ trong nội dung"""
        return len(content.split())
    
    def save_content_file(self, file_path: str, content: str, format: str = "html") -> bool:
        """Lưu nội dung vào file"""
        try:
            full_path = os.path.join(self.storage_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving content file: {e}")
            return False
    
    def save_markdown_file(self, file_path: str, content: str) -> bool:
        """Lưu nội dung vào file markdown (backward compatibility)"""
        return self.save_content_file(file_path, content, "markdown")
    
    def delete_content_file(self, file_path: str) -> bool:
        """Xóa file content"""
        try:
            full_path = os.path.join(self.storage_path, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting content file: {e}")
            return False
    
    def delete_markdown_file(self, file_path: str) -> bool:
        """Xóa file markdown (backward compatibility)"""
        return self.delete_content_file(file_path)


# Backward compatibility
MarkdownService = ContentService 