#!/usr/bin/env python3
"""
Script để test upload EPUB
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

def test_epub_upload():
    """Test upload EPUB API"""
    try:
        # Token từ localStorage của frontend (cần copy từ browser)
        token = input("Nhập session token từ browser: ").strip()
        
        if not token:
            print("❌ Không có token!")
            return
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        
        # Test file path (cần có file EPUB thực)
        epub_file_path = input("Nhập đường dẫn đến file EPUB (hoặc Enter để bỏ qua): ").strip()
        
        if not epub_file_path or not os.path.exists(epub_file_path):
            print("❌ File EPUB không tồn tại!")
            return
        
        print("🔍 Testing EPUB upload...")
        
        # Upload file
        with open(epub_file_path, 'rb') as f:
            files = {'epub_file': (os.path.basename(epub_file_path), f, 'application/epub+zip')}
            data = {'novel_title': 'Test Novel from Script'}
            
            response = requests.post(
                'http://localhost:8000/api/v1/novels/upload-epub',
                headers=headers,
                files=files,
                data=data
            )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_epub_upload() 