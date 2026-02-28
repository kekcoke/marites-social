from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID

user_example = {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "johndoe",
    "email": "john.doe@example.com",
    "is_active": True,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "last_login": None,
    "last_activity": None,
    "deleted_at": None
}

class UserBase(BaseModel):
    """Base schema for User with common fields"""
    model_config = ConfigDict(from_attributes=True, json_schema_extra={ "example" : user_example })

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., description="Email address of the user")
    is_active: bool = Field(default=True, description="Active status of the user")

class UserCreate(UserBase):
    """Schema for creating a new user - includes password field"""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user details - all fields optional"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(...)


class UserResponse(UserBase):
    """Schema for user responses - includes all database fields"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    deleted_at: Optional[datetime] = None # Support for soft-delete transparency

# Alias for backward compatibility
User = UserResponse