from sqlalchemy import Column, Integer, String, Boolean
from src.app.db.connection import Base

class Posts(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, default=True)
    author = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    rating = Column(Float, nullable=True)
    likes = Column(Integer, default=0)
