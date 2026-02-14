from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum

class EventBase(BaseModel):
    """Base schema for Event"""

    name: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    place_id: UUID
    account_id: UUID
    start_time_utc: datetime
    end_time_utc: datetime
    is_active: bool = True
    
    @field_validator('end_time_utc')
    @classmethod
    def validate_end_time(cls, v, info):
        """Ensure end time is after start time"""
    
        if 'start_time_utc' in info.data and v <= info.data['start_time_utc']:
            raise ValueError('end_time_utc must be after start_time_utc')
        return v


class EventCreate(EventBase):
    """Schema for creating an event"""
    blob_storage_id: Optional[str] = Field(None, max_length=500)


class EventUpdate(BaseModel):
    """Schema for updating an event"""

    name: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    place_id: Optional[UUID] = None
    start_time_utc: Optional[datetime] = None
    end_time_utc: Optional[datetime] = None
    is_active: Optional[bool] = None
    blob_storage_id: Optional[str] = Field(None, max_length=500)


class EventResponse(EventBase):
    """Schema for event responses"""

    id: UUID
    creator_user_id: Optional[UUID] = None
    event_chat_ids: Optional[List[UUID]] = None
    blob_storage_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EventWithDetails(EventResponse):
    """Event with related details"""

    place_name: Optional[str] = None
    account_name: Optional[str] = None
    attendee_count: Optional[int] = None
    ticket_price_range: Optional[str] = None