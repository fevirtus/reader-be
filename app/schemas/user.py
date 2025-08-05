from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True 


class UserProfileBase(BaseModel):
    username: str
    email: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class UserProfileResponse(UserProfileBase):
    id: str
    role: str = 'user'
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoleUpdateRequest(BaseModel):
    user_id: str
    role: str  # 'user' hoặc 'admin'


class RoleUpdateResponse(BaseModel):
    success: bool
    message: str
    user_id: str
    new_role: str 