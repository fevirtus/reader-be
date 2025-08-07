# EPUB Upload Feature

## Tổng quan

Tính năng EPUB upload cho phép admin upload file EPUB và tự động tạo novel mới trong hệ thống. Hệ thống sẽ:

1. Nhận EPUB file từ admin
2. Trích xuất thông tin metadata (title, author, language, etc.)
3. Đọc table of contents để xác định cấu trúc chapters
4. Tách từng chapter và lưu dưới dạng HTML
5. Tạo novel và chapters trong database

## API Endpoint

### Upload EPUB và tạo novel

```
POST /api/v1/novels/upload-epub
```

**Headers:**
- `Authorization: Bearer {token}` (admin token)

**Parameters:**
- `epub_file`: EPUB file (multipart/form-data)
- `novel_title`: Tên novel (tùy chọn, nếu không có sẽ lấy từ EPUB metadata)

**Response:**
```json
{
  "message": "Upload EPUB thành công",
  "novel": {
    "id": 1,
    "title": "Tên truyện",
    "author": "Tác giả",
    "description": "Mô tả",
    "status": "ongoing",
    "total_chapters": 100,
    "language": "vi"
  },
  "total_chapters_created": 100,
  "epub_info": {
    "title": "Tên truyện",
    "creator": "Tác giả", 
    "language": "vi",
    "total_chapters": 100
  }
}
```

## Cấu trúc Storage mới

### Trước đây:
```
storage/
└── novels/
    └── {novel_title}/
        ├── book_info.json
        ├── 1.md
        ├── 2.md
        └── ...
```

### Hiện tại:
```
storage/
└── novels/
    └── {novel_title}/
        ├── book_info.json
        ├── 1.html
        ├── 2.html
        └── ...
```

## Quy trình xử lý EPUB

### 1. Validation
- Kiểm tra file có phải là EPUB hợp lệ không
- Kiểm tra kích thước file (tối đa 100MB)
- Kiểm tra cấu trúc EPUB (container.xml, OPF file)

### 2. Metadata Extraction
- Đọc OPF file để lấy metadata
- Trích xuất title, creator, language, identifier
- Đọc manifest để lấy danh sách files

### 3. Table of Contents
- Tìm NCX file (table of contents)
- Nếu không có NCX, sử dụng spine để xác định thứ tự chapters
- Trích xuất title và content file cho từng chapter

### 4. Content Processing
- Đọc content file của từng chapter
- Chuyển đổi HTML thành text content
- Lưu dưới dạng HTML trong storage

### 5. Database Creation
- Tạo novel record trong database
- Tạo chapter records cho từng chapter
- Cập nhật total_chapters

## Services

### EpubService

Chịu trách nhiệm xử lý EPUB files:

```python
class EpubService:
    def validate_epub_file(self, file_path: str) -> bool
    def extract_epub_info(self, epub_path: str) -> Dict[str, Any]
    def extract_chapter_content(self, epub_path: str, chapter_info: Dict) -> Optional[str]
    def process_epub_upload(self, epub_file_path: str, novel_title: str = None) -> Dict[str, Any]
    def save_chapter_to_storage(self, novel_title: str, chapter_number: int, content: str) -> str
```

### ContentService (thay thế MarkdownService)

Hỗ trợ đọc cả HTML và Markdown files:

```python
class ContentService:
    def read_content_file(self, file_path: str, novel_title: str = None) -> Optional[str]
    def convert_to_html(self, markdown_content: str) -> str
    def save_content_file(self, file_path: str, content: str, format: str = "html") -> bool
```

## Migration

### Script Migration

Chạy script để migrate dữ liệu hiện tại:

```bash
python scripts/migrate_storage_structure.py
```

Script này sẽ:
1. Chuyển đổi tất cả file .md thành .html
2. Cập nhật book_info.json để thay đổi filename
3. Xóa file .md cũ

### Test Script

Chạy script để test EPUB functionality:

```bash
python scripts/test_epub_upload.py
```

## Lưu ý

1. **Quyền truy cập**: Chỉ admin mới có thể upload EPUB
2. **File size**: Giới hạn 100MB cho EPUB files
3. **Format**: Chỉ chấp nhận file EPUB hợp lệ
4. **Storage**: Chapters được lưu dưới dạng HTML thay vì Markdown
5. **Backward compatibility**: Hệ thống vẫn hỗ trợ đọc Markdown files cũ

## Error Handling

- File không phải EPUB: `400 Bad Request`
- File quá lớn: `400 Bad Request` 
- EPUB không hợp lệ: `400 Bad Request`
- Không có quyền admin: `403 Forbidden`
- Lỗi xử lý: `500 Internal Server Error`

## Future Improvements

1. **Progress tracking**: Hiển thị tiến trình upload cho files lớn
2. **Batch processing**: Upload nhiều EPUB cùng lúc
3. **Content validation**: Kiểm tra chất lượng content
4. **Image handling**: Xử lý images trong EPUB
5. **Format conversion**: Hỗ trợ các format khác (PDF, MOBI) 