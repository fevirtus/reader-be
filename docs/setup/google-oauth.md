# 🔐 Google OAuth Setup Guide

## 📋 **Overview**

Hướng dẫn cấu hình Google OAuth 2.0 cho Reader Backend.

## 🎯 **Prerequisites**

- Google account
- Access to Google Cloud Console
- Backend server running

## 🔧 **Setup Steps**

### **1. Create Google Cloud Project**

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** > **New Project**
3. Đặt tên project: `Reader Backend OAuth`
4. Click **Create**

### **2. Enable APIs**

1. Vào **APIs & Services** > **Library**
2. Tìm và enable các APIs:
   - **Google+ API**
   - **Google OAuth2 API**

### **3. Create OAuth 2.0 Credentials**

1. Vào **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client IDs**
3. Chọn **Web application**
4. Điền thông tin:

#### **Authorized JavaScript origins:**
```
http://localhost:3000
```

#### **Authorized redirect URIs:**
```
http://localhost:8000/api/v1/oauth/google/callback
http://localhost:3000/callback
```

5. Click **Create**

### **4. Get Credentials**

Sau khi tạo xong, copy:
- **Client ID**
- **Client Secret**

## 🔧 **Backend Configuration**

### **1. Environment Variables**

Thêm vào file `.env`:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/oauth/google/callback

# OAuth Settings
OAUTH_ENABLED=True
OAUTH_PROVIDERS=["google"]
FRONTEND_REDIRECT_URI=http://localhost:3000/callback
```

### **2. Install Dependencies**

```bash
# Install Google OAuth dependencies
uv sync
```

### **3. Test Configuration**

```bash
# Test OAuth URL generation
curl http://localhost:8000/api/v1/oauth/google/auth

# Test frontend config
curl http://localhost:8000/api/v1/oauth/frontend-config
```

## 🚀 **Frontend Integration**

### **1. OAuth Login Button**

```typescript
const loginWithGoogle = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/oauth/google/auth')
    const data = await response.json()
    
    if (data.auth_url) {
      window.location.href = data.auth_url
    }
  } catch (error) {
    console.error('OAuth login error:', error)
  }
}
```

### **2. Callback Handler**

```typescript
const handleCallback = () => {
  const urlParams = new URLSearchParams(window.location.search)
  const sessionToken = urlParams.get('session_token')
  const isNewUser = urlParams.get('is_new_user')
  const error = urlParams.get('error')
  
  if (error) {
    console.error('OAuth error:', error)
    return
  }
  
  if (sessionToken) {
    localStorage.setItem('session_token', sessionToken)
    localStorage.setItem('is_new_user', isNewUser || 'false')
    window.location.href = '/dashboard'
  }
}
```

## 🛠️ **Troubleshooting**

### **Error: "Invalid redirect URI"**

**Cause:** Redirect URI không khớp với cấu hình trong Google Console

**Solution:**
1. Kiểm tra redirect URI trong Google Console
2. Đảm bảo URI khớp với `GOOGLE_REDIRECT_URI`
3. Thêm domain vào authorized origins

### **Error: "Client ID not found"**

**Cause:** Environment variables chưa được cấu hình

**Solution:**
1. Kiểm tra `GOOGLE_CLIENT_ID` trong `.env`
2. Đảm bảo OAuth credentials đã được tạo
3. Enable Google+ API trong Google Console

### **Error: "Invalid authorization code"**

**Cause:** Code đã được sử dụng hoặc hết hạn

**Solution:**
1. Kiểm tra code không bị sử dụng 2 lần
2. Đảm bảo code chưa hết hạn
3. Verify redirect URI khớp với authorization request

## 📊 **Security Best Practices**

### **✅ Environment Variables**
- ✅ Không commit credentials vào git
- ✅ Sử dụng `.env` file cho local development
- ✅ Sử dụng environment variables cho production

### **✅ Redirect URIs**
- ✅ Chỉ allow specific domains
- ✅ Sử dụng HTTPS cho production
- ✅ Validate redirect URIs

### **✅ Session Management**
- ✅ Secure session token generation
- ✅ Token expiration
- ✅ Proper logout handling

## 🎯 **Production Setup**

### **1. Update Redirect URIs**

Thêm production domains vào Google Console:
```
https://yourdomain.com/api/v1/oauth/google/callback
https://yourdomain.com/callback
```

### **2. Environment Variables**

```env
# Production
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/v1/oauth/google/callback
FRONTEND_REDIRECT_URI=https://yourdomain.com/callback
OAUTH_ENABLED=True
```

### **3. SSL Certificate**

- ✅ Setup SSL certificate
- ✅ Force HTTPS redirects
- ✅ Secure cookie settings

## 🎉 **Verification**

### **✅ Test OAuth Flow**

1. **Frontend**: Click login button
2. **Google**: Authenticate user
3. **Backend**: Process callback
4. **Frontend**: Receive session token
5. **Dashboard**: User logged in

### **✅ Check Database**

```bash
# Check user profiles
curl http://localhost:8000/api/v1/user/profile \
  -H 'Authorization: Bearer <session_token>'

# Check sessions
python check_sessions.py
```

**OAuth setup complete! 🚀** 