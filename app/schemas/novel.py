from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class NovelBase(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    status: str = "ongoing"


class NovelCreate(NovelBase):
    pass


class NovelUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    status: Optional[str] = None


class NovelResponse(NovelBase):
    id: int
    total_chapters: int
    views: int
    rating: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True 