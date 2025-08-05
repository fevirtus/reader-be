# 📚 Novel API Endpoints

## 📋 **Overview**

**Base URL:** `http://localhost:8000/api/v1/novels`

## 🎯 **Lưu ý quan trọng**

Novels được quản lý tự động thông qua **Sync Service**:
- ✅ **Tự động tạo/update** từ storage/novels/
- ✅ **Tự động xóa** khi folder bị xóa
- ✅ **Không có API tạo/sửa/xóa** thủ công
- ✅ **Chỉ có API đọc** thông tin

## 🔧 **Endpoints**

### **1. Lấy danh sách novels**

```http
GET /api/v1/novels
```

**Description:** Lấy danh sách novels với phân trang và filtering

**Query Parameters:**
- `page` (optional): Trang hiện tại (bắt đầu từ 1, default: 1)
- `limit` (optional): Số bản ghi trả về (1-100, default: 20)
- `search` (optional): Từ khóa tìm kiếm trong title và description
- `status` (optional): Lọc theo trạng thái (ongoing, completed)
- `author` (optional): Lọc theo tác giả

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Ai Bảo Hắn Tu Tiên",
      "author": "Tác giả A",
      "description": "Mô tả truyện...",
      "cover_image": "https://example.com/cover.jpg",
      "status": "ongoing",
      "total_chapters": 867,
      "views": 1500,
      "rating": 4.5,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T13:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20,
  "total_pages": 8,
  "has_next": true,
  "has_prev": false,
  "next_page": 2,
  "prev_page": null
}
```

**Examples:**
```bash
# Lấy trang đầu tiên
curl "http://localhost:8000/api/v1/novels"

# Phân trang
curl "http://localhost:8000/api/v1/novels?page=2&limit=20"

# Tìm kiếm
curl "http://localhost:8000/api/v1/novels?search=tu tiên"

# Lọc theo trạng thái
curl "http://localhost:8000/api/v1/novels?status=ongoing"

# Lọc theo tác giả
curl "http://localhost:8000/api/v1/novels?author=Tác giả A"

# Kết hợp nhiều filter
curl "http://localhost:8000/api/v1/novels?search=tu tiên&status=ongoing&page=3&limit=30"
```

---

### **2. Lấy thông tin novel**

```http
GET /api/v1/novels/{novel_id}
```

**Description:** Lấy thông tin chi tiết của một novel

**Path Parameters:**
- `novel_id` (required): ID của novel

**Response (200):**
```json
{
  "id": 1,
  "title": "Ai Bảo Hắn Tu Tiên",
  "author": "Tác giả A",
  "description": "Mô tả chi tiết về truyện...",
  "cover_image": "https://example.com/cover.jpg",
  "status": "ongoing",
  "total_chapters": 867,
  "views": 1501,
  "rating": 4.5,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T13:00:00Z"
}
```

**Response (404):**
```json
{
  "detail": "Novel không tồn tại"
}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/novels/1"
```

## 🚀 **Frontend Integration**

### **1. Lấy danh sách novels**

```typescript
const getNovels = async (params: {
  page?: number
  limit?: number
  search?: string
  status?: string
  author?: string
}) => {
  const queryParams = new URLSearchParams()
  
  if (params.page) queryParams.append('page', params.page.toString())
  if (params.limit) queryParams.append('limit', params.limit.toString())
  if (params.search) queryParams.append('search', params.search)
  if (params.status) queryParams.append('status', params.status)
  if (params.author) queryParams.append('author', params.author)
  
  const response = await fetch(`http://localhost:8000/api/v1/novels?${queryParams}`)
  return response.json()
}

// Sử dụng
const result = await getNovels({ 
  page: 1,
  limit: 20, 
  status: 'ongoing',
  search: 'tu tiên'
})

console.log(result.items) // Danh sách novels
console.log(result.total) // Tổng số novels
console.log(result.total_pages) // Tổng số trang
```

### **2. Lấy thông tin novel**

```typescript
const getNovel = async (novelId: number) => {
  const response = await fetch(`http://localhost:8000/api/v1/novels/${novelId}`)
  
  if (!response.ok) {
    throw new Error('Novel không tồn tại')
  }
  
  return response.json()
}

// Sử dụng
const novel = await getNovel(1)
console.log(novel.title) // "Ai Bảo Hắn Tu Tiên"
```

### **3. Pagination Component**

```typescript
const NovelList = () => {
  const [novels, setNovels] = useState([])
  const [pagination, setPagination] = useState({
    page: 1,
    total: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false
  })
  const [loading, setLoading] = useState(false)
  
  const loadNovels = async (pageNum: number) => {
    setLoading(true)
    try {
      const result = await getNovels({ 
        page: pageNum, 
        limit: 20 
      })
      setNovels(result.items)
      setPagination({
        page: result.page,
        total: result.total,
        total_pages: result.total_pages,
        has_next: result.has_next,
        has_prev: result.has_prev
      })
    } catch (error) {
      console.error('Error loading novels:', error)
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    loadNovels(1)
  }, [])
  
  const handlePageChange = (newPage: number) => {
    loadNovels(newPage)
  }
  
  return (
    <div>
      {novels.map(novel => (
        <NovelCard key={novel.id} novel={novel} />
      ))}
      <Pagination 
        currentPage={pagination.page}
        totalPages={pagination.total_pages}
        hasNext={pagination.has_next}
        hasPrev={pagination.has_prev}
        onPageChange={handlePageChange}
        loading={loading}
      />
    </div>
  )
}
```

## 📊 **Response Schema**

### **NovelResponse**
```typescript
interface NovelResponse {
  id: number
  title: string
  author: string
  description: string | null
  cover_image: string | null
  status: 'ongoing' | 'completed'
  total_chapters: number
  views: number
  rating: number
  created_at: string
  updated_at: string
}
```

## 🎯 **Features**

### ✅ **Pagination**
- Hỗ trợ phân trang với `skip` và `limit`
- Giới hạn tối đa 1000 bản ghi mỗi lần

### ✅ **Search & Filter**
- Tìm kiếm theo title và author
- Lọc theo trạng thái (ongoing/completed)
- Lọc theo tác giả
- Kết hợp nhiều filter

### ✅ **Auto Views**
- Tự động tăng lượt xem khi truy cập novel
- Tracking thống kê chính xác

### ✅ **Sync Integration**
- Dữ liệu được sync tự động từ storage
- Không cần quản lý thủ công

## 📈 **Error Codes**

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (Invalid parameters) |
| 404 | Novel not found |
| 500 | Internal Server Error |

## 🎉 **Best Practices**

### **✅ Frontend Usage**
1. **Pagination**: Sử dụng `skip` và `limit` cho danh sách dài
2. **Search**: Kết hợp với debounce để tránh spam request
3. **Caching**: Cache novel data để giảm API calls
4. **Error Handling**: Xử lý 404 cho novel không tồn tại

### **✅ Performance**
1. **Limit**: Sử dụng limit hợp lý (20-50 items)
2. **Filtering**: Sử dụng filter để giảm dữ liệu trả về
3. **Caching**: Cache response để tăng tốc độ

**Novel APIs ready for production! 🚀** 