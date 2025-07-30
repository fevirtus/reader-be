from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChapterBase(BaseModel):
    chapter_number: float
    title: Optional[str] = None


class ChapterCreate(ChapterBase):
    novel_id: int
    content_file: str


class ChapterUpdate(BaseModel):
    chapter_number: Optional[float] = None
    title: Optional[str] = None
    content_file: Optional[str] = None


class ChapterResponse(ChapterBase):
    id: int
    novel_id: int
    content_file: str
    word_count: int
    views: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True 