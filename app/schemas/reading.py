from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReadingProgressCreate(BaseModel):
    novel_id: int
    chapter_id: int
    chapter_number: float


class ReadingProgressUpdate(BaseModel):
    chapter_id: Optional[int] = None
    chapter_number: Optional[float] = None


class ReadingProgressResponse(BaseModel):
    id: int
    user_id: str
    novel_id: int
    chapter_id: int
    chapter_number: float
    read_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ReadingProgressWithNovel(BaseModel):
    id: int
    novel_id: int
    chapter_id: int
    chapter_number: float
    read_at: datetime
    novel_title: str
    novel_author: str
    novel_cover_image: Optional[str] = None
    chapter_title: Optional[str] = None
    
    class Config:
        from_attributes = True


class BookshelfAdd(BaseModel):
    novel_id: int


class BookshelfResponse(BaseModel):
    id: int
    user_id: str
    novel_id: int
    added_at: datetime
    novel_title: str
    novel_author: str
    novel_description: Optional[str] = None
    novel_cover_image: Optional[str] = None
    novel_status: str
    novel_total_chapters: int
    novel_views: int
    novel_rating: int
    
    class Config:
        from_attributes = True 