from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class Post(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    published: bool = True
    author: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    rating: Optional[float] = None
    likes: int = 0
    comments: Optional[List[str]] = None
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123",
                "title": "My First Post",
                "content": "This is my first post content",
                "author": "John Doe",
                "created_at": "2024-01-15T10:30:00",
                "likes": 5,
                "comments": []
            }
        }
class CreatePost(BaseModel):
    title: str
    content: str
    author: str

class UpdatePost(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    published: Optional[bool] = None
