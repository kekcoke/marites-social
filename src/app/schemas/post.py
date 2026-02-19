from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List

post_example = {
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
class PostBase(BaseModel):
    """Base schema for Post with common fields"""
    model_config = ConfigDict(from_attributes=True, json_schema_extra={ "example" : post_example })
    
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=100)
    published: bool = Field(default=True, description="Published status")
    user_id: UUID

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=100)
    published: bool = Field(default=True, description="Published status")


class PostUpdate(BaseModel):
    """Schema for updating an existing post - all fields optional"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    published: Optional[bool] = None
    author: Optional[str] = Field(None, max_length=100)
    rating: Optional[float] = Field(None, ge=0, le=5)
    votes: Optional[int] = None
    comments: Optional[str] = None

class PostResponse(PostBase):
    """Schema for post responses - includes all database fields"""
    id: int
    rating: Optional[float] = None
    votes: int
    comments: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

# Alias for backward compatibility
Post = PostResponse