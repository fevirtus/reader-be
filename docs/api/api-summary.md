# 📋 API Endpoints Summary

## 🔍 **Overview**

**Base URL:** `http://localhost:8000/api/v1`

**Total Endpoints:** 28 endpoints across 7 categories

## 📊 **API Statistics**

| Category | Endpoints | Description |
|----------|-----------|-------------|
| 🔐 Authentication | 6 | OAuth và user management |
| 📚 Novels | 2 | Read-only novel APIs |
| 📖 Chapters | 2 | Read-only chapter APIs |
| 📊 Reading | 10 | Progress và bookshelf |
| 🔄 Sync | 6 | Content synchronization |
| 🔑 OAuth | 6 | Google OAuth flow |

## 🔐 **Authentication & User Management** (6 endpoints)

### User Profile
- `GET /user/profile` - Get current user profile
- `PUT /user/profile` - Update user profile
- `GET /user/me` - Alias for profile (backward compatibility)
- `PUT /user/me` - Alias for profile (backward compatibility)

### Session Management
- `POST /user/logout` - User logout
- `POST /user/validate-session` - Validate session token

## 🔑 **OAuth Authentication** (6 endpoints)

### Google OAuth Flow
- `GET /oauth/google/auth` - Get Google OAuth URL
- `GET /oauth/google/callback` - Handle OAuth callback (redirects to frontend)
- `GET /oauth/google/callback/redirect` - Alternative callback with custom redirect
- `POST /oauth/google/verify` - Verify Google ID token

### OAuth Configuration
- `GET /oauth/providers` - Get available OAuth providers
- `GET /oauth/frontend-config` - Get frontend configuration

## 📚 **Novels** (2 endpoints)

### Read-Only APIs
- `GET /novels` - Get list of novels with filtering and pagination
- `GET /novels/{novel_id}` - Get novel details

**Note:** Novels are managed automatically via sync service. No create/update/delete APIs.

## 📖 **Chapters** (2 endpoints)

### Read-Only APIs
- `GET /chapters` - Get chapters by novel ID with pagination
- `GET /chapters/{chapter_id}` - Get chapter content (markdown/html)

**Note:** Chapters are managed automatically via sync service. No create/update/delete APIs.

## 📊 **Reading Progress** (10 endpoints)

### Progress Management
- `POST /reading/progress` - Update reading progress
- `GET /reading/progress` - Get reading progress
- `GET /reading/progress/with-novels` - Get reading progress with novel info

### Bookshelf Management
- `POST /reading/bookshelf` - Add novel to bookshelf
- `DELETE /reading/bookshelf/{novel_id}` - Remove novel from bookshelf
- `GET /reading/bookshelf` - Get user's bookshelf
- `GET /reading/bookshelf/{novel_id}/check` - Check if novel is in bookshelf

### Statistics & Guest Access
- `GET /reading/stats` - Get reading statistics
- `GET /reading/novels/{novel_id}/progress` - Get novel progress (guest users)
- `GET /reading/novels/{novel_id}/bookshelf-check` - Check bookshelf (guest users)

## 🔄 **Sync Service** (6 endpoints)

### Manual Sync
- `POST /sync/novels` - Manual sync novels from storage
- `POST /sync/novels/background` - Background sync novels
- `GET /sync/novels/status` - Get sync status

### Scheduler Management
- `POST /sync/scheduler/start` - Start hourly sync scheduler
- `POST /sync/scheduler/stop` - Stop sync scheduler
- `GET /sync/scheduler/status` - Get scheduler status

## 🎯 **Key Features**

### ✅ **OAuth-Only Authentication**
- Google OAuth 2.0 integration
- Session-based authentication
- No traditional email/password login

### ✅ **Automatic Content Management**
- Hourly sync from storage/novels/
- Read-only novel APIs
- Automatic create/update/delete based on storage

### ✅ **Advanced Filtering**
- Search by title and author
- Filter by status (ongoing/completed)
- Filter by author
- Pagination support

### ✅ **Reading Progress**
- Track reading progress per user
- Bookshelf management
- Statistics and analytics
- Guest user support

### ✅ **Content Management**
- Markdown support for chapters
- Chapter navigation
- Content formatting (markdown/html)

## 📈 **Usage Examples**

### **Frontend Integration**
```typescript
// Get novels with filtering
const novels = await fetch('/api/v1/novels?search=tu tiên&status=ongoing&limit=20')

// Get chapter content
const chapter = await fetch('/api/v1/chapters/novel/1/chapter/1/content?format=html')

// Update reading progress
await fetch('/api/v1/reading/progress', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer <token>' },
  body: JSON.stringify({ novel_id: 1, chapter_id: 1, chapter_number: 1 })
})
```

### **Sync Management**
```bash
# Manual sync
curl -X POST http://localhost:8000/api/v1/sync/novels

# Start scheduler
curl -X POST http://localhost:8000/api/v1/sync/scheduler/start

# Check status
curl http://localhost:8000/api/v1/sync/novels/status
```

## 🔒 **Security Features**

- **OAuth 2.0**: Secure authentication with Google
- **Session Management**: 7-day session tokens
- **Row Level Security**: Database-level security
- **Input Validation**: Pydantic schemas
- **CORS**: Cross-origin request handling

## 📚 **Documentation**

- **Interactive API Docs**: `http://localhost:8000/docs`
- **Detailed Guides**: See `docs/` folder
- **Setup Instructions**: Check `docs/setup/`
- **Troubleshooting**: See `docs/troubleshooting/`

**All APIs are production-ready! 🚀** 