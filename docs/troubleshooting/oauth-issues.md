# 🛠️ OAuth Troubleshooting Guide

## 📋 **Common Issues & Solutions**

## 🔍 **Issue 1: "User not allowed"**

### **Symptoms:**
```
{"detail":"Google OAuth callback failed: Login existing user failed: Create profile for existing user failed: User not allowed"}
```

### **Cause:**
- RLS (Row Level Security) policies blocking operations
- Using wrong Supabase client (anon vs service role)

### **Solution:**
1. **Use service role key for admin operations**
```python
# ✅ Correct: Use supabase_admin
self.supabase_admin.table('user_profiles').insert(profile_data).execute()

# ❌ Wrong: Using anon key
self.supabase.table('user_profiles').insert(profile_data).execute()
```

2. **Check RLS policies**
```sql
-- Ensure RLS allows service role operations
CREATE POLICY "Enable service role access" ON user_profiles
FOR ALL USING (auth.role() = 'service_role');
```

## 🔍 **Issue 2: "'list' object has no attribute 'users'"**

### **Symptoms:**
```
AttributeError: 'list' object has no attribute 'users'
```

### **Cause:**
- Wrong method call on Supabase client
- Incorrect response handling

### **Solution:**
```python
# ✅ Correct: Use admin client
auth_response = self.supabase_admin.auth.admin.list_users()

# ❌ Wrong: Using regular client
auth_response = self.supabase.auth.admin.list_users()
```

## 🔍 **Issue 3: "null value in column 'id'"**

### **Symptoms:**
```
{'message': 'null value in column "id" of relation "user_profiles" violates not-null constraint'}
```

### **Cause:**
- Trying to insert profile without user ID
- Missing user creation step

### **Solution:**
```python
# ✅ Correct: Generate UUID for user ID
import uuid
user_id = str(uuid.uuid4())

profile_data = {
    "id": user_id,
    "username": username,
    "email": email
}
```

## 🔍 **Issue 4: "duplicate key value violates unique constraint"**

### **Symptoms:**
```
{'message': 'duplicate key value violates unique constraint "user_profiles_username_key"'}
```

### **Cause:**
- Username already exists
- No unique username generation

### **Solution:**
```python
# ✅ Correct: Generate unique username
import time
base_username = email.split('@')[0]
unique_username = f"{base_username}_{int(time.time())}"

# Or use UUID
username_uuid = str(uuid.uuid4())[:8]
```

## 🔍 **Issue 5: "For security purposes, you can only request this after 8 seconds"**

### **Symptoms:**
```
For security purposes, you can only request this after 8 seconds.
```

### **Cause:**
- Supabase rate limiting
- Too many requests in short time

### **Solution:**
1. **Add delay between requests**
```python
import time
time.sleep(8)  # Wait 8 seconds
```

2. **Check existing data first**
```python
# Check if user exists before creating
existing_profile = self.supabase_admin.table('user_profiles').select('*').eq('email', email).execute()
if existing_profile.data:
    return existing_profile.data[0]
```

## 🔍 **Issue 6: "Invalid redirect URI"**

### **Symptoms:**
```
Error: redirect_uri_mismatch
```

### **Cause:**
- Redirect URI không khớp với Google Console
- Wrong environment variables

### **Solution:**
1. **Check Google Console settings**
```
Authorized redirect URIs:
http://localhost:8000/api/v1/oauth/google/callback
http://localhost:3000/callback
```

2. **Verify environment variables**
```env
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/oauth/google/callback
FRONTEND_REDIRECT_URI=http://localhost:3000/callback
```

## 🔍 **Issue 7: "Session token required"**

### **Symptoms:**
```
{"detail":"Session token required"}
```

### **Cause:**
- Missing Authorization header
- Wrong header format

### **Solution:**
```bash
# ✅ Correct: Bearer token
curl 'http://localhost:8000/api/v1/user/profile' \
  -H 'Authorization: Bearer your-session-token'

# ❌ Wrong: Missing Bearer prefix
curl 'http://localhost:8000/api/v1/user/profile' \
  -H 'Authorization: your-session-token'
```

## 🔍 **Issue 8: "Invalid authorization header format"**

### **Symptoms:**
```
{"detail":"Invalid authorization header format"}
```

### **Cause:**
- Wrong Authorization header format
- Missing "Bearer " prefix

### **Solution:**
```typescript
// ✅ Correct: Bearer token
const response = await fetch('/api/v1/user/profile', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})

// ❌ Wrong: Missing Bearer
const response = await fetch('/api/v1/user/profile', {
  headers: {
    'Authorization': token
  }
})
```

## 🔍 **Issue 9: "Invalid or expired session token"**

### **Symptoms:**
```
{"detail":"Invalid or expired session token"}
```

### **Cause:**
- Session token expired
- Token not found in database
- Wrong token format

### **Solution:**
1. **Check token expiration**
```python
expires_at = datetime.fromisoformat(session['expires_at'])
if expires_at > datetime.now(timezone.utc):
    # Token valid
    pass
```

2. **Verify token in database**
```bash
python check_sessions.py
```

3. **Generate new token**
```python
session_token = secrets.token_urlsafe(32)
```

## 🔍 **Issue 10: "No data to update"**

### **Symptoms:**
```
{"detail":"No data to update"}
```

### **Cause:**
- Empty update data
- All fields are None

### **Solution:**
```python
# ✅ Correct: Filter out None values
update_data = {k: v for k, v in profile_data.dict().items() if v is not None}

if not update_data:
    raise HTTPException(status_code=400, detail="No data to update")
```

## 🛠️ **Debug Tools**

### **1. Check Sessions**
```bash
python check_sessions.py
```

### **2. Test OAuth Flow**
```bash
curl http://localhost:8000/api/v1/oauth/google/auth
```

### **3. Validate Session**
```bash
curl -X POST 'http://localhost:8000/api/v1/user/validate-session' \
  -H 'Content-Type: application/json' \
  -d '{"session_token": "your-token"}'
```

### **4. Check User Profile**
```bash
curl 'http://localhost:8000/api/v1/user/profile' \
  -H 'Authorization: Bearer your-token'
```

## 📊 **Prevention Tips**

### **✅ Best Practices**
1. **Always use service role key** for admin operations
2. **Generate unique usernames** to avoid conflicts
3. **Add proper error handling** for all operations
4. **Use Bearer token format** for Authorization headers
5. **Check existing data** before creating new records
6. **Add delays** for rate-limited operations
7. **Validate environment variables** on startup

### **✅ Testing**
1. **Test OAuth flow** end-to-end
2. **Verify session management**
3. **Check database consistency**
4. **Monitor error logs**

## 🎯 **Quick Fixes**

### **Most Common Issues:**
1. **Rate limiting** → Add 8-second delay
2. **RLS blocking** → Use service role key
3. **Duplicate usernames** → Generate unique names
4. **Missing Bearer** → Add "Bearer " prefix
5. **Expired tokens** → Generate new session

**Most issues can be resolved with these fixes! 🚀** 