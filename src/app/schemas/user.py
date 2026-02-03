from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    """Base schema for User with common fields"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., description="Email address of the user")
    is_active: bool = Field(default=True, description="Active status of the user")

class UserCreate(UserBase):
    """Schema for creating a new user - includes password field"""
    password: str = Field(..., min_length=6, max_length=100)

class UserResponse(UserBase):
    """Schema for user responses - includes all database fields"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic v2 (use orm_mode for v1)
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "johndoe",
                "email": "",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00",
                "last_login": None,
                "last_activity": None,
                "deleted_at": None
            }
        }

# Alias for backward compatibility
User = UserResponse