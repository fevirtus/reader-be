# 👤 User API Endpoints

## 📋 **Overview**

**Base URL:** `http://localhost:8000/api/v1/user`

## 🔧 **Endpoints**

### **1. Get User Profile**

```http
GET /profile
```

**Description:** Lấy thông tin user hiện tại

**Headers:**
```
Authorization: Bearer <session_token>
```

**Response (200):**
```json
{
  "id": "user-uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "avatar_url": "https://lh3.googleusercontent.com/a/...",
  "bio": "Software developer",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

**Response (401 - Unauthorized):**
```json
{
  "detail": "Session token required"
}
```

**Example:**
```bash
curl 'http://localhost:8000/api/v1/user/profile' \
  -H 'Authorization: Bearer your-session-token'
```

---

### **2. Update User Profile**

```http
PUT /profile
```

**Description:** Cập nhật profile của user

**Headers:**
```
Authorization: Bearer <session_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "new_username",
  "avatar_url": "https://example.com/avatar.jpg",
  "bio": "Updated bio"
}
```

**Response (200):**
```json
{
  "id": "user-uuid",
  "username": "new_username",
  "email": "john@example.com",
  "avatar_url": "https://example.com/avatar.jpg",
  "bio": "Updated bio",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T13:00:00Z"
}
```

**Response (400 - Bad Request):**
```json
{
  "detail": "No data to update"
}
```

**Example:**
```bash
curl -X PUT 'http://localhost:8000/api/v1/user/profile' \
  -H 'Authorization: Bearer your-session-token' \
  -H 'Content-Type: application/json' \
  -d '{"bio": "Updated bio"}'
```

---

### **3. Logout User**

```http
POST /logout
```

**Description:** Đăng xuất user

**Headers:**
```
Authorization: Bearer <session_token>
```

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

**Response (400 - Bad Request):**
```json
{
  "detail": "Logout failed"
}
```

**Example:**
```bash
curl -X POST 'http://localhost:8000/api/v1/user/logout' \
  -H 'Authorization: Bearer your-session-token'
```

---

### **4. Validate Session**

```http
POST /validate-session
```

**Description:** Validate session token

**Request Body:**
```json
{
  "session_token": "your-session-token"
}
```

**Response (200 - Valid):**
```json
{
  "valid": true,
  "user": {
    "id": "user-uuid",
    "username": "john_doe",
    "email": "john@example.com",
    "avatar_url": "https://...",
    "bio": "Software developer",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
}
```

**Response (200 - Invalid):**
```json
{
  "valid": false
}
```

**Example:**
```bash
curl -X POST 'http://localhost:8000/api/v1/user/validate-session' \
  -H 'Content-Type: application/json' \
  -d '{"session_token": "your-session-token"}'
```

---

### **5. Get User Profile (Alias)**

```http
GET /me
```

**Description:** Alias cho `/profile` - để tương thích với frontend cũ

**Headers:**
```
Authorization: Bearer <session_token>
```

**Response:** Giống như `/profile`

**Example:**
```bash
curl 'http://localhost:8000/api/v1/user/me' \
  -H 'Authorization: Bearer your-session-token'
```

---

### **6. Update User Profile (Alias)**

```http
PUT /me
```

**Description:** Alias cho `/profile` - để tương thích với frontend cũ

**Headers:**
```
Authorization: Bearer <session_token>
Content-Type: application/json
```

**Request Body:** Giống như `/profile`

**Response:** Giống như `/profile`

**Example:**
```bash
curl -X PUT 'http://localhost:8000/api/v1/user/me' \
  -H 'Authorization: Bearer your-session-token' \
  -H 'Content-Type: application/json' \
  -d '{"bio": "Updated bio"}'
```

## 🚀 **Frontend Integration**

### **1. Get User Profile**

```typescript
const getUserProfile = async () => {
  const token = localStorage.getItem('session_token')
  
  try {
    const response = await fetch('http://localhost:8000/api/v1/user/profile', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      const user = await response.json()
      return user
    } else {
      throw new Error('Failed to get user profile')
    }
  } catch (error) {
    console.error('Error:', error)
    // Redirect to login
    window.location.href = '/login'
  }
}
```

### **2. Update User Profile**

```typescript
const updateUserProfile = async (profileData: {
  username?: string
  avatar_url?: string
  bio?: string
}) => {
  const token = localStorage.getItem('session_token')
  
  try {
    const response = await fetch('http://localhost:8000/api/v1/user/profile', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(profileData)
    })
    
    if (response.ok) {
      const updatedUser = await response.json()
      return updatedUser
    } else {
      throw new Error('Failed to update profile')
    }
  } catch (error) {
    console.error('Error:', error)
  }
}
```

### **3. Logout**

```typescript
const logout = async () => {
  const token = localStorage.getItem('session_token')
  
  try {
    const response = await fetch('http://localhost:8000/api/v1/user/logout', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      // Xóa session token
      localStorage.removeItem('session_token')
      
      // Redirect về trang login
      window.location.href = '/login'
    }
  } catch (error) {
    console.error('Error:', error)
  }
}
```

### **4. Validate Session**

```typescript
const validateSession = async () => {
  const token = localStorage.getItem('session_token')
  
  if (!token) {
    return false
  }
  
  try {
    const response = await fetch('http://localhost:8000/api/v1/user/validate-session', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ session_token: token })
    })
    
    const result = await response.json()
    return result.valid
  } catch (error) {
    console.error('Error:', error)
    return false
  }
}
```

## 📊 **Error Codes**

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (Invalid data, no data to update) |
| 401 | Unauthorized (Missing or invalid token) |
| 500 | Internal Server Error |

## 🎯 **Features**

### ✅ **Security**
- Session token validation
- Authorization headers required
- Automatic token expiration

### ✅ **User Experience**
- Simple profile management
- Alias endpoints for backward compatibility
- Clear error messages

### ✅ **Development**
- RESTful API design
- Consistent response format
- Comprehensive error handling 