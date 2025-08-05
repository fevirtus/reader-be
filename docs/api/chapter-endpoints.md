# 📖 Chapter API Endpoints

## 📋 **Overview**

**Base URL:** `http://localhost:8000/api/v1/chapters`

## 🎯 **Lưu ý quan trọng**

Chapters được quản lý tự động thông qua **Sync Service**:
- ✅ **Tự động tạo/update** từ storage/novels/ khi sync
- ✅ **Tự động xóa** khi folder bị xóa
- ✅ **Không có API tạo/sửa/xóa** thủ công
- ✅ **Chỉ có API đọc** thông tin và nội dung

## 🔧 **Endpoints**

### **1. Lấy danh sách chapters**

```http
GET /api/v1/chapters
```

**Description:** Lấy danh sách chapters của một novel với phân trang

**Query Parameters:**
- `novel_id` (required): ID của novel
- `page` (optional): Trang hiện tại (bắt đầu từ 1, default: 1)
- `limit` (optional): Số bản ghi trả về (1-200, default: 50)

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "novel_id": 1,
      "title": "Chapter 1: The Beginning",
      "chapter_number": 1,
      "content_file": "https://example.com/chapter1.md",
      "word_count": 2500,
      "views": 150,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T13:00:00Z"
    }
  ],
  "total": 867,
  "page": 1,
  "limit": 50,
  "total_pages": 18,
  "has_next": true,
  "has_prev": false,
  "next_page": 2,
  "prev_page": null
}
```

**Examples:**
```bash
# Lấy trang đầu tiên chapters của novel
curl "http://localhost:8000/api/v1/chapters?novel_id=1"

# Phân trang
curl "http://localhost:8000/api/v1/chapters?novel_id=1&page=2&limit=50"
```

---

### **2. Lấy nội dung chapter**

```http
GET /api/v1/chapters/{chapter_id}
```

**Description:** Lấy nội dung chapter để hiển thị (markdown/html)

**Path Parameters:**
- `chapter_id` (required): ID của chapter

**Query Parameters:**
- `format` (optional): Định dạng nội dung (markdown/html, default: markdown)

**Response (200):**
```json
{
  "content": "# Chapter 1: The Beginning\n\nThis is the content of chapter 1...",
  "format": "markdown",
  "chapter_info": {
    "id": 1,
    "title": "Chapter 1: The Beginning",
    "chapter_number": 1,
    "novel_id": 1
  }
}
```

**Response (404):**
```json
{
  "detail": "Chapter không tồn tại"
}
```

**Examples:**
```bash
# Lấy nội dung markdown
curl "http://localhost:8000/api/v1/chapters/1"

# Lấy nội dung HTML
curl "http://localhost:8000/api/v1/chapters/1?format=html"
```

## 🚀 **Frontend Integration**

### **1. Lấy danh sách chapters**

```typescript
const getChapters = async (novelId: number, params: {
  page?: number
  limit?: number
}) => {
  const queryParams = new URLSearchParams()
  queryParams.append('novel_id', novelId.toString())
  
  if (params.page) queryParams.append('page', params.page.toString())
  if (params.limit) queryParams.append('limit', params.limit.toString())
  
  const response = await fetch(`http://localhost:8000/api/v1/chapters?${queryParams}`)
  return response.json()
}

// Sử dụng
const result = await getChapters(1, { page: 1, limit: 50 })
console.log(result.items) // Danh sách chapters
console.log(result.total) // Tổng số chapters
console.log(result.total_pages) // Tổng số trang
```

### **2. Lấy nội dung chapter**

```typescript
const getChapterContent = async (chapterId: number, format: 'markdown' | 'html' = 'markdown') => {
  const response = await fetch(`http://localhost:8000/api/v1/chapters/${chapterId}?format=${format}`)
  
  if (!response.ok) {
    throw new Error('Chapter không tồn tại')
  }
  
  return response.json()
}

// Sử dụng
const chapterContent = await getChapterContent(1, 'html')
console.log(chapterContent.content) // HTML content
console.log(chapterContent.chapter_info.title) // Chapter title
```

### **3. Chapter List Component**

```typescript
const ChapterList = ({ novelId }: { novelId: number }) => {
  const [chapters, setChapters] = useState([])
  const [pagination, setPagination] = useState({
    page: 1,
    total: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false
  })
  const [loading, setLoading] = useState(false)
  
  const loadChapters = async (pageNum: number) => {
    setLoading(true)
    try {
      const result = await getChapters(novelId, { page: pageNum, limit: 50 })
      setChapters(result.items)
      setPagination({
        page: result.page,
        total: result.total,
        total_pages: result.total_pages,
        has_next: result.has_next,
        has_prev: result.has_prev
      })
    } catch (error) {
      console.error('Error loading chapters:', error)
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    loadChapters(1)
  }, [novelId])
  
  const handlePageChange = (newPage: number) => {
    loadChapters(newPage)
  }
  
  return (
    <div>
      {chapters.map(chapter => (
        <ChapterItem key={chapter.id} chapter={chapter} />
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

### **4. Chapter Reader Component**

```typescript
const ChapterReader = ({ chapterId }: { chapterId: number }) => {
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)
  
  const loadChapterContent = async () => {
    setLoading(true)
    try {
      const data = await getChapterContent(chapterId, 'html')
      setContent(data.content)
    } catch (error) {
      console.error('Error loading chapter content:', error)
    } finally {
      setLoading(false)
    }
  }
  
  useEffect(() => {
    loadChapterContent()
  }, [chapterId])
  
  return (
    <div>
      {loading ? (
        <div>Loading...</div>
      ) : (
        <div dangerouslySetInnerHTML={{ __html: content }} />
      )}
    </div>
  )
}
```

## 📊 **Response Schema**

### **ChapterResponse**
```typescript
interface ChapterResponse {
  id: number
  novel_id: number
  title: string
  chapter_number: number
  content_file: string
  word_count: number
  views: number
  created_at: string
  updated_at: string
}

interface ChapterListResponse {
  items: ChapterResponse[]
  total: number
  page: number
  limit: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
  next_page: number | null
  prev_page: number | null
}
```

### **ChapterContentResponse**
```typescript
interface ChapterContentResponse {
  content: string
  format: 'markdown' | 'html'
  chapter_info: {
    id: number
    title: string
    chapter_number: number
    novel_id: number
  }
}
```

## 🎯 **Features**

### ✅ **Read-Only APIs**
- Chỉ có API đọc thông tin và nội dung
- Không có API tạo/sửa/xóa thủ công
- Quản lý tự động qua sync service

### ✅ **Content Formatting**
- Hỗ trợ markdown và HTML
- Tự động convert markdown sang HTML
- Flexible content display

### ✅ **Auto Progress Tracking**
- Tự động cập nhật reading progress khi đọc
- Tăng lượt xem tự động
- Guest user support

### ✅ **Pagination**
- Hỗ trợ phân trang cho danh sách chapters
- Efficient loading cho novels dài

## 📈 **Error Codes**

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (Invalid parameters) |
| 404 | Chapter not found |
| 500 | Internal Server Error |

## 🎉 **Best Practices**

### **✅ Frontend Usage**
1. **Pagination**: Sử dụng skip/limit cho novels dài
2. **Content Loading**: Load content khi cần thiết
3. **Caching**: Cache chapter content để tăng tốc độ
4. **Error Handling**: Xử lý 404 cho chapter không tồn tại

### **✅ Performance**
1. **Lazy Loading**: Load chapters theo demand
2. **Content Format**: Chọn format phù hợp (markdown cho edit, HTML cho display)
3. **Caching**: Cache response để giảm API calls

### **✅ Content Management**
1. **Sync Integration**: Chapters được sync tự động
2. **Format Support**: Markdown cho storage, HTML cho display
3. **Progress Tracking**: Tự động track reading progress

**Chapter APIs optimized for reading experience! 📖** 