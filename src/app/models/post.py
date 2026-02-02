from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Float,
    Integer,
    Text,
    func,
    text
)
from sqlalchemy.orm import declarative_base
from src.app.db.connection import Base

class Post(Base):
    """SQLAlchemy model for posts table"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    published = Column(Boolean, server_default="true", nullable=False)    
    author = Column(String(100), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"), #auto-update timestamp on modification
        nullable=False,
    )
    rating = Column(Float, nullable=True)
    likes = Column(Integer, server_default="0", nullable=False)
    comments = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title}', author='{self.author}')>"
