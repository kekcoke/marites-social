from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID

class ChatRoomBase(BaseModel):
    """Base schema for ChatRoom"""
    model_config = ConfigDict(from_attributes=True)
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
    archived_at: Optional[datetime] = None


class ChatRoomWithToken(ChatRoomResponse):
    """Chat room with gRPC connection token"""
    grpc_room_token: Optional[str] = None