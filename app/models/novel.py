from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Novel(Base):
    __tablename__ = "novels"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    cover_image = Column(String(500), nullable=True)
    status = Column(String(50), default="ongoing")  # ongoing, completed, hiatus
    total_chapters = Column(Integer, default=0)
    views = Column(Integer, default=0)
    rating = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    chapters = relationship("Chapter", back_populates="novel", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Novel(id={self.id}, title='{self.title}', author='{self.author}')>" 