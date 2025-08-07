#!/usr/bin/env python3

import asyncio
import httpx
from app.services.oauth_service import OAuthService
from app.services.auth_service import AuthService

async def test_oauth_flow():
    """Test OAuth flow và session token"""
    try:
        print("🧪 Testing OAuth flow...")
        
        # Tạo OAuth service
        oauth_service = OAuthService()
        auth_service = AuthService()
        
        # Test tạo session token
        print("🔑 Testing session token creation...")
        session_token = auth_service._create_session_token()
        print(f"✅ Session token created: {session_token}")
        
        # Test user profile API
        print("👤 Testing user profile API...")
        try:
            # Tạo test user profile
            test_user_data = {
                'id': 'test-user-id',
                'email': 'test@example.com',
                'username': 'testuser',
                'role': 'user'
            }
            
            # Test với session token
            headers = {'Authorization': f'Bearer {session_token}'}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'http://localhost:8000/api/v1/user/profile',
                    headers=headers
                )
                print(f"📊 User profile API response: {response.status_code}")
                print(f"📄 Response body: {response.text}")
                
        except Exception as e:
            print(f"❌ User profile API error: {e}")
        
        print("✅ OAuth flow test completed")
        
    except Exception as e:
        print(f"❌ OAuth flow test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_oauth_flow()) 