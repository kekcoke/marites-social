from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class PostBase(BaseModel):
    """Base schema for Post with common fields"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=100)
    published: bool = Field(default=True, description="Published status")

class CreatePost(BaseModel):
    title: str
    content: str
    author: str
    published: bool = True

class UpdatePost(BaseModel):
    """Schema for updating an existing post - all fields optional"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    published: Optional[bool] = None

class PostResponse(PostBase):
    """Schema for post responses - includes all database fields"""
    id: int
    title: str
    content: str
    author: str
    published: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: UUID
    rating: Optional[float] = None
    votes: Optional[int] = None
    comments: Optional[str] = None

    class Config:
        from_attributes = True  # Pydantic v2 (use orm_mode for v1)
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "My First Post",
                "content": "This is my first post content",
                "author": "John Doe",
                "published": True,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00",
                "rating": None,
                "votes": 0,
                "comments": None
            }
        }

# Alias for backward compatibility
Post = PostResponse