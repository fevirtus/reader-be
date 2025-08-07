#!/usr/bin/env python3
"""
Script để migrate cấu trúc storage từ cũ sang mới
Từ: storage/novels/{novel_title}/
Sang: storage/novels/{novel_title}/
Và chuyển đổi từ .md sang .html
"""

import os
import shutil
import markdown
from pathlib import Path
from app.core.config import settings


def convert_markdown_to_html(markdown_content: str) -> str:
    """Chuyển đổi markdown thành HTML"""
    md = markdown.Markdown(extensions=['extra', 'codehilite'])
    return md.convert(markdown_content)


def migrate_storage_structure():
    """Migrate cấu trúc storage"""
    storage_path = settings.storage_path
    novels_path = storage_path  # storage_path đã là ./storage/novels
    
    if not os.path.exists(novels_path):
        print(f"Novels path không tồn tại: {novels_path}")
        return
    
    print("Bắt đầu migrate cấu trúc storage...")
    
    # Duyệt qua tất cả novels
    for novel_dir in os.listdir(novels_path):
        novel_path = os.path.join(novels_path, novel_dir)
        
        if not os.path.isdir(novel_path):
            continue
        
        print(f"Đang xử lý novel: {novel_dir}")
        
        # Tìm tất cả file .md
        md_files = []
        for file in os.listdir(novel_path):
            if file.endswith('.md'):
                md_files.append(file)
        
        print(f"  Tìm thấy {len(md_files)} file .md")
        
        # Chuyển đổi từng file
        for md_file in md_files:
            md_path = os.path.join(novel_path, md_file)
            html_file = md_file.replace('.md', '.html')
            html_path = os.path.join(novel_path, html_file)
            
            try:
                # Đọc nội dung markdown
                with open(md_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                # Chuyển đổi thành HTML
                html_content = convert_markdown_to_html(md_content)
                
                # Lưu file HTML
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                print(f"    Đã chuyển đổi: {md_file} -> {html_file}")
                
                # Xóa file .md cũ
                os.remove(md_path)
                print(f"    Đã xóa file cũ: {md_file}")
                
            except Exception as e:
                print(f"    Lỗi khi xử lý {md_file}: {e}")
        
        print(f"  Hoàn thành novel: {novel_dir}")
    
    print("Migrate hoàn thành!")


def update_book_info_files():
    """Cập nhật book_info.json để thay đổi filename từ .md sang .html"""
    storage_path = settings.storage_path
    novels_path = storage_path  # storage_path đã là ./storage/novels
    
    if not os.path.exists(novels_path):
        print(f"Novels path không tồn tại: {novels_path}")
        return
    
    print("Bắt đầu cập nhật book_info.json...")
    
    import json
    
    for novel_dir in os.listdir(novels_path):
        novel_path = os.path.join(novels_path, novel_dir)
        
        if not os.path.isdir(novel_path):
            continue
        
        book_info_path = os.path.join(novel_path, 'book_info.json')
        
        if not os.path.exists(book_info_path):
            continue
        
        print(f"Đang cập nhật book_info.json cho: {novel_dir}")
        
        try:
            # Đọc book_info.json
            with open(book_info_path, 'r', encoding='utf-8') as f:
                book_info = json.load(f)
            
            # Cập nhật filename trong chapters
            updated = False
            if 'chapters' in book_info:
                for chapter in book_info['chapters']:
                    if 'filename' in chapter and chapter['filename'].endswith('.md'):
                        chapter['filename'] = chapter['filename'].replace('.md', '.html')
                        updated = True
            
            # Lưu lại nếu có thay đổi
            if updated:
                with open(book_info_path, 'w', encoding='utf-8') as f:
                    json.dump(book_info, f, ensure_ascii=False, indent=2)
                print(f"  Đã cập nhật book_info.json cho: {novel_dir}")
            else:
                print(f"  Không cần cập nhật cho: {novel_dir}")
                
        except Exception as e:
            print(f"  Lỗi khi cập nhật book_info.json cho {novel_dir}: {e}")
    
    print("Cập nhật book_info.json hoàn thành!")


if __name__ == "__main__":
    print("=== Script Migrate Storage Structure ===")
    
    # Migrate cấu trúc storage
    migrate_storage_structure()
    
    # Cập nhật book_info.json
    update_book_info_files()
    
    print("=== Hoàn thành migrate ===") 