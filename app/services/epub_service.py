import os
import zipfile
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re
from app.core.config import settings


class EpubService:
    def __init__(self):
        self.storage_path = settings.storage_path
        self.epub_extensions = ['.epub']
    
    def extract_epub_info(self, epub_path: str) -> Dict[str, Any]:
        """
        Trích xuất thông tin cơ bản từ EPUB file
        
        Returns:
            Dict chứa title, creator, language, identifier, total_chapters
        """
        try:
            with zipfile.ZipFile(epub_path, 'r') as epub:
                # Đọc container.xml để tìm OPF file
                container_content = epub.read('META-INF/container.xml')
                container_tree = ET.fromstring(container_content)
                
                # Tìm OPF file path
                rootfile = container_tree.find('.//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile')
                if rootfile is None:
                    raise ValueError("Không tìm thấy rootfile trong container.xml")
                
                opf_path = rootfile.get('full-path')
                opf_content = epub.read(opf_path)
                opf_tree = ET.fromstring(opf_content)
                
                # Trích xuất metadata
                metadata = opf_tree.find('.//{http://www.idpf.org/2007/opf}metadata')
                
                # Lấy title
                title_elem = metadata.find('.//{http://purl.org/dc/elements/1.1/}title')
                title = title_elem.text if title_elem is not None else "Unknown Title"
                
                # Lấy creator (author)
                creator_elem = metadata.find('.//{http://purl.org/dc/elements/1.1/}creator')
                creator = creator_elem.text if creator_elem is not None else "Unknown Author"
                
                # Lấy language
                language_elem = metadata.find('.//{http://purl.org/dc/elements/1.1/}language')
                language = language_elem.text if language_elem is not None else "vi"
                
                # Lấy identifier
                identifier_elem = metadata.find('.//{http://purl.org/dc/elements/1.1/}identifier')
                identifier = identifier_elem.text if identifier_elem is not None else None
                
                # Đọc manifest để lấy danh sách files
                manifest = opf_tree.find('.//{http://www.idpf.org/2007/opf}manifest')
                items = manifest.findall('.//{http://www.idpf.org/2007/opf}item')
                
                # Tìm NCX file (table of contents)
                ncx_file = None
                for item in items:
                    if item.get('media-type') == 'application/x-dtbncx+xml':
                        ncx_file = item.get('href')
                        break
                
                # Nếu không có NCX, tìm trong spine
                if not ncx_file:
                    spine = opf_tree.find('.//{http://www.idpf.org/2007/opf}spine')
                    if spine is not None:
                        spine_items = spine.findall('.//{http://www.idpf.org/2007/opf}itemref')
                        # Lấy danh sách chapters từ spine
                        chapters = []
                        for itemref in spine_items:
                            idref = itemref.get('idref')
                            for item in items:
                                if item.get('id') == idref:
                                    chapters.append({
                                        'id': idref,
                                        'href': item.get('href'),
                                        'media_type': item.get('media-type')
                                    })
                                    break
                    else:
                        chapters = []
                else:
                    # Đọc NCX file để lấy table of contents
                    ncx_content = epub.read(ncx_file)
                    ncx_tree = ET.fromstring(ncx_content)
                    chapters = self._extract_chapters_from_ncx(ncx_tree, items)
                
                return {
                    'title': title,
                    'creator': creator,
                    'language': language,
                    'identifier': identifier,
                    'total_chapters': len(chapters),
                    'chapters': chapters,
                    'opf_path': opf_path,
                    'epub_files': {item.get('id'): item.get('href') for item in items}
                }
                
        except Exception as e:
            print(f"Error extracting EPUB info: {e}")
            return None
    
    def _extract_chapters_from_ncx(self, ncx_tree: ET.Element, items: List[ET.Element]) -> List[Dict[str, Any]]:
        """Trích xuất thông tin chapters từ NCX file"""
        chapters = []
        nav_points = ncx_tree.findall('.//{http://www.daisy.org/z3986/2005/ncx/}navPoint')
        
        for nav_point in nav_points:
            # Lấy title
            text_elem = nav_point.find('.//{http://www.daisy.org/z3986/2005/ncx/}text')
            title = text_elem.text if text_elem is not None else "Unknown Chapter"
            
            # Lấy content file
            content_elem = nav_point.find('.//{http://www.daisy.org/z3986/2005/ncx/}content')
            src = content_elem.get('src') if content_elem is not None else None
            
            if src:
                # Tìm item tương ứng trong manifest
                for item in items:
                    if item.get('href') == src or item.get('href') in src:
                        chapters.append({
                            'title': title,
                            'href': item.get('href'),
                            'media_type': item.get('media-type'),
                            'id': item.get('id')
                        })
                        break
        
        return chapters
    
    def extract_chapter_content(self, epub_path: str, chapter_info: Dict[str, Any]) -> Optional[str]:
        """Trích xuất nội dung của một chapter từ EPUB"""
        try:
            with zipfile.ZipFile(epub_path, 'r') as epub:
                # Đọc file content
                content_file = chapter_info['href']
                content = epub.read(content_file).decode('utf-8')
                
                # Parse HTML và trích xuất text content
                content = self._extract_text_from_html(content)
                
                return content
                
        except Exception as e:
            print(f"Error extracting chapter content: {e}")
            return None
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """Trích xuất text từ HTML content"""
        # Loại bỏ HTML tags nhưng giữ lại cấu trúc
        # Đơn giản hóa - có thể cần cải thiện
        import re
        
        # Loại bỏ script và style tags
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
        
        # Thay thế các HTML tags phổ biến
        html_content = re.sub(r'<br\s*/?>', '\n', html_content)
        html_content = re.sub(r'<p[^>]*>', '\n', html_content)
        html_content = re.sub(r'</p>', '\n', html_content)
        html_content = re.sub(r'<div[^>]*>', '\n', html_content)
        html_content = re.sub(r'</div>', '\n', html_content)
        
        # Loại bỏ tất cả HTML tags còn lại
        html_content = re.sub(r'<[^>]+>', '', html_content)
        
        # Xử lý HTML entities
        html_content = html_content.replace('&nbsp;', ' ')
        html_content = html_content.replace('&amp;', '&')
        html_content = html_content.replace('&lt;', '<')
        html_content = html_content.replace('&gt;', '>')
        html_content = html_content.replace('&quot;', '"')
        
        # Loại bỏ khoảng trắng thừa
        lines = html_content.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        return '\n\n'.join(cleaned_lines)
    
    def save_chapter_to_storage(self, novel_title: str, chapter_number: int, content: str) -> str:
        """Lưu chapter content vào storage folder"""
        try:
            # Tạo directory cho novel
            novel_dir = os.path.join(self.storage_path, novel_title)
            os.makedirs(novel_dir, exist_ok=True)
            
            # Tạo filename cho chapter
            filename = f"{chapter_number}.html"
            file_path = os.path.join(novel_dir, filename)
            
            # Lưu content dưới dạng HTML
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return filename
            
        except Exception as e:
            print(f"Error saving chapter to storage: {e}")
            return None
    
    def process_epub_upload(self, epub_file_path: str, novel_title: str = None) -> Dict[str, Any]:
        """
        Xử lý upload EPUB file và trả về thông tin cần thiết để tạo novel
        
        Returns:
            Dict chứa thông tin novel và chapters
        """
        try:
            # Trích xuất thông tin từ EPUB
            epub_info = self.extract_epub_info(epub_file_path)
            if not epub_info:
                raise ValueError("Không thể trích xuất thông tin từ EPUB file")
            
            # Sử dụng title từ EPUB nếu không có novel_title
            if not novel_title:
                novel_title = epub_info['title']
            
            # Xử lý từng chapter
            processed_chapters = []
            for i, chapter_info in enumerate(epub_info['chapters'], 1):
                # Trích xuất content
                content = self.extract_chapter_content(epub_file_path, chapter_info)
                if content:
                    # Lưu vào storage
                    filename = self.save_chapter_to_storage(novel_title, i, content)
                    
                    if filename:
                        processed_chapters.append({
                            'number': i,
                            'title': chapter_info['title'],
                            'filename': filename,
                            'word_count': len(content.split())
                        })
            
            return {
                'title': epub_info['title'],
                'creator': epub_info['creator'],
                'language': epub_info['language'],
                'identifier': epub_info['identifier'],
                'total_chapters': len(processed_chapters),
                'chapters': processed_chapters
            }
            
        except Exception as e:
            print(f"Error processing EPUB upload: {e}")
            return None
    
    def validate_epub_file(self, file_path: str) -> bool:
        """Kiểm tra xem file có phải là EPUB hợp lệ không"""
        try:
            # Kiểm tra extension
            if not any(file_path.lower().endswith(ext) for ext in self.epub_extensions):
                return False
            
            # Kiểm tra xem có phải là ZIP file hợp lệ không
            with zipfile.ZipFile(file_path, 'r') as epub:
                # Kiểm tra xem có container.xml không
                if 'META-INF/container.xml' not in epub.namelist():
                    return False
                
                # Kiểm tra xem có OPF file không
                container_content = epub.read('META-INF/container.xml')
                container_tree = ET.fromstring(container_content)
                rootfile = container_tree.find('.//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile')
                
                if rootfile is None:
                    return False
                
                opf_path = rootfile.get('full-path')
                if opf_path not in epub.namelist():
                    return False
                
                return True
                
        except Exception as e:
            print(f"Error validating EPUB file: {e}")
            return False 