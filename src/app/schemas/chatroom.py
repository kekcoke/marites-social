from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum

class ChatRoomBase(BaseModel):
    """Base schema for ChatRoom"""

    account_id: UUID
    event_id: Optional[UUID] = None
    owner_id: Optional[UUID] = None
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)


class ChatRoomCreate(ChatRoomBase):
    """Schema for creating a chat room"""
    pass


class ChatRoomUpdate(BaseModel):
    """Schema for updating a chat room"""

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    num_active_users_in_session: Optional[int] = Field(None, ge=0)
    activity_level_score: Optional[float] = Field(None, ge=0.0)


class ChatRoomResponse(ChatRoomBase):
    """Schema for chat room responses"""

    id: UUID
    num_active_users_in_session: int
    activity_level_score: float
    last_activity_at: Optional[datetime] = None
    grpc_service_url: Optional[str] = None
    created_on: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatRoomWithToken(ChatRoomResponse):
    """Chat room with gRPC connection token"""
    grpc_room_token: str