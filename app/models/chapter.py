from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=False)
    chapter_number = Column(Float, nullable=False)  # Float để hỗ trợ chapter 1.5, 2.1, etc.
    title = Column(String(255), nullable=True)
    content_file = Column(String(500), nullable=False)  # Path to markdown file
    word_count = Column(Integer, default=0)
    views = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    novel = relationship("Novel", back_populates="chapters")
    
    def __repr__(self):
        return f"<Chapter(id={self.id}, novel_id={self.novel_id}, chapter_number={self.chapter_number})>" 