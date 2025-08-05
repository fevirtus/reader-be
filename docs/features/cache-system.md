# Cache System

## Tổng quan

Hệ thống cache được thiết kế để tăng tốc độ truy cập dữ liệu bằng cách lưu trữ tạm thời các kết quả truy vấn trong bộ nhớ.

## Tính năng

### 1. Cache Service
- **In-memory cache**: Lưu trữ trong RAM
- **TTL (Time To Live)**: Tự động xóa cache hết hạn
- **Key-based access**: Truy cập theo key
- **Statistics**: Thống kê cache usage

### 2. Cache Strategy

#### Novels
- **Single novel**: Cache 30 phút
- **Novels list**: Cache 15 phút
- **Search results**: Cache 10 phút

#### Chapters
- **Single chapter**: Cache 1 giờ
- **Chapters list**: Cache 30 phút
- **Chapter content**: Cache 2 giờ

## Cache Keys

### Novel Cache
```
novel:{novel_id}                    # Thông tin novel cụ thể
novels:page:{page}:limit:{limit}:status:{status}:author:{author}  # Danh sách novels
novels:search:{query}:page:{page}:limit:{limit}  # Kết quả tìm kiếm
```

### Chapter Cache
```
chapter:{chapter_id}                 # Thông tin chapter cụ thể
chapters:novel:{novel_id}:page:{page}:limit:{limit}  # Danh sách chapters
chapter_content:{chapter_id}:{format}  # Nội dung chapter (markdown/html)
```

## API Endpoints

### Cache Management (Admin Only)

#### 1. Lấy thống kê cache
```http
GET /api/v1/cache/stats
Authorization: Bearer <admin_token>
```

Response:
```json
{
    "success": true,
    "data": {
        "total_entries": 50,
        "valid_entries": 45,
        "expired_entries": 5,
        "memory_usage": 1024000
    }
}
```

#### 2. Xóa tất cả cache
```http
POST /api/v1/cache/clear
Authorization: Bearer <admin_token>
```

#### 3. Dọn dẹp cache hết hạn
```http
POST /api/v1/cache/cleanup
Authorization: Bearer <admin_token>
```

#### 4. Xóa cache novel cụ thể
```http
DELETE /api/v1/cache/novels/{novel_id}
Authorization: Bearer <admin_token>
```

#### 5. Xóa cache chapter cụ thể
```http
DELETE /api/v1/cache/chapters/{chapter_id}
Authorization: Bearer <admin_token>
```

#### 6. Liệt kê cache keys
```http
GET /api/v1/cache/keys
Authorization: Bearer <admin_token>
```

## Cache Invalidation

### Tự động
- **TTL**: Cache tự động hết hạn theo thời gian
- **Cleanup**: Dọn dẹp cache hết hạn định kỳ

### Thủ công (Admin)
- **Clear all**: Xóa tất cả cache
- **Clear specific**: Xóa cache của novel/chapter cụ thể
- **Cleanup**: Dọn dẹp cache hết hạn

### Khi có thay đổi
- **Create/Update/Delete novel**: Invalidate novel cache + novels list cache
- **Create/Update/Delete chapter**: Invalidate chapter cache + chapters list cache

## Performance Benefits

### Trước khi có cache
```
Request → Database → File System → Response
```

### Sau khi có cache
```
Request → Cache → Response (nếu có cache)
Request → Database → File System → Cache → Response (nếu không có cache)
```

## Memory Usage

### Cache Entry Structure
```python
{
    'data': actual_data,
    'created_at': datetime,
    'expires_at': datetime,
    'ttl': seconds
}
```

### Memory Optimization
- **TTL**: Tự động xóa cache hết hạn
- **Cleanup**: Dọn dẹp định kỳ
- **Key limits**: Giới hạn số lượng keys trong response

## Monitoring

### Cache Statistics
- **Total entries**: Tổng số cache entries
- **Valid entries**: Số entries còn hiệu lực
- **Expired entries**: Số entries hết hạn
- **Memory usage**: Dung lượng bộ nhớ sử dụng

### Cache Keys
- **Novel keys**: `novel:*`, `novels:*`
- **Chapter keys**: `chapter:*`, `chapters:*`, `chapter_content:*`

## Best Practices

### 1. Cache Strategy
- **Frequently accessed**: Cache lâu hơn
- **Rarely accessed**: Cache ngắn hơn
- **Critical data**: Cache ngắn hơn để đảm bảo accuracy

### 2. Memory Management
- **Regular cleanup**: Dọn dẹp cache hết hạn
- **Monitor usage**: Theo dõi memory usage
- **Clear when needed**: Xóa cache khi cần thiết

### 3. Cache Invalidation
- **Automatic**: Dựa trên TTL
- **Manual**: Khi có thay đổi data
- **Selective**: Xóa cache cụ thể

## Troubleshooting

### Cache không hoạt động
- Kiểm tra cache service được import
- Kiểm tra cache key generation
- Kiểm tra TTL settings

### Memory usage cao
- Giảm TTL
- Tăng cleanup frequency
- Clear cache thủ công

### Cache không được invalidate
- Kiểm tra invalidation logic
- Kiểm tra admin permissions
- Kiểm tra cache key patterns 