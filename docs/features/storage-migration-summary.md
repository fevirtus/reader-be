# Storage Migration Summary

## Tổng quan

Đã hoàn thành việc chuyển đổi từ mô hình quản lý nội dung dựa trên storage folder sang mô hình BE-controlled content management với khả năng upload EPUB.

## Những thay đổi chính

### 1. Cấu trúc Storage

**Trước đây:**
```
storage/
└── novels/
    └── {novel_title}/
        ├── book_info.json
        ├── 1.md
        ├── 2.md
        └── ...
```

**Hiện tại:**
```
storage/
└── novels/
    └── {novel_title}/
        ├── book_info.json
        ├── 1.html
        ├── 2.html
        └── ...
```

### 2. Services mới

#### EpubService (`app/services/epub_service.py`)
- `validate_epub_file()`: Kiểm tra tính hợp lệ của EPUB
- `extract_epub_info()`: Trích xuất metadata từ EPUB
- `extract_chapter_content()`: Trích xuất nội dung chapter
- `process_epub_upload()`: Xử lý toàn bộ quy trình upload EPUB
- `save_chapter_to_storage()`: Lưu chapter vào storage

#### ContentService (`app/services/markdown_service.py`)
- Thay thế MarkdownService
- Hỗ trợ đọc cả HTML và Markdown files
- Backward compatibility với MarkdownService

### 3. API Endpoints mới

#### Upload EPUB
```
POST /api/v1/novels/upload-epub
```
- Chỉ admin có thể sử dụng
- Upload EPUB file và tự động tạo novel + chapters
- Giới hạn file size: 100MB

### 4. Quy trình xử lý EPUB

1. **Validation**: Kiểm tra file EPUB hợp lệ
2. **Metadata Extraction**: Trích xuất title, author, language
3. **Table of Contents**: Đọc NCX hoặc spine để xác định chapters
4. **Content Processing**: Trích xuất và chuyển đổi nội dung
5. **Storage**: Lưu chapters dưới dạng HTML
6. **Database**: Tạo novel và chapter records

## Migration đã thực hiện

### Script Migration (`scripts/migrate_storage_structure.py`)
- Chuyển đổi tất cả file `.md` thành `.html`
- Cập nhật `book_info.json` để thay đổi filename
- Xóa file `.md` cũ

### Kết quả Migration
- ✅ Đã chuyển đổi 2107 chapters từ `.md` sang `.html`
- ✅ Đã cập nhật `book_info.json`
- ✅ Đã xóa file `.md` cũ

## Mô hình mới

### Quy trình thêm truyện mới:
1. **Admin upload EPUB file** → BE nhận file
2. **BE nhận dạng table of contents** → Trích xuất cấu trúc chapters
3. **Tạo truyện mới trong DB** → Novel record với metadata
4. **Tách chương theo table of contents** → Xử lý từng chapter
5. **Lưu từng chương dưới dạng HTML** → Storage folder

### Ưu điểm của mô hình mới:
- **Tự động hóa**: Không cần thủ công tạo novel và chapters
- **Chuẩn hóa**: EPUB là format chuẩn cho e-books
- **Metadata rich**: Tự động lấy title, author, language
- **Structured content**: Table of contents được parse tự động
- **Scalable**: Có thể xử lý nhiều EPUB cùng lúc

## Backward Compatibility

- ✅ Hệ thống vẫn đọc được Markdown files cũ
- ✅ ContentService hỗ trợ cả HTML và Markdown
- ✅ API endpoints cũ vẫn hoạt động bình thường

## Testing

### Test Scripts
- `scripts/test_epub_upload.py`: Test EPUB functionality
- `scripts/migrate_storage_structure.py`: Migration script

### Manual Testing
```bash
# Test EPUB upload (cần file EPUB thực tế)
curl -X POST "http://localhost:8000/api/v1/novels/upload-epub" \
  -H "Authorization: Bearer {admin_token}" \
  -F "epub_file=@novel.epub"
```

## Documentation

- `docs/features/epub-upload.md`: Chi tiết về EPUB upload feature
- `docs/features/storage-migration-summary.md`: Tóm tắt migration

## Future Improvements

1. **Progress tracking**: Hiển thị tiến trình upload cho files lớn
2. **Batch processing**: Upload nhiều EPUB cùng lúc
3. **Content validation**: Kiểm tra chất lượng content
4. **Image handling**: Xử lý images trong EPUB
5. **Format conversion**: Hỗ trợ các format khác (PDF, MOBI)

## Lưu ý quan trọng

1. **Quyền truy cập**: Chỉ admin mới có thể upload EPUB
2. **File size**: Giới hạn 100MB cho EPUB files
3. **Format**: Chỉ chấp nhận file EPUB hợp lệ
4. **Storage**: Chapters được lưu dưới dạng HTML
5. **Backward compatibility**: Hệ thống vẫn hỗ trợ đọc Markdown files cũ 