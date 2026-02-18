from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import UUID
from app.core.enums import NotificationType


class NotificationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str = Field(..., max_length=200)
    message: str
    related_entity_type: Optional[str] = Field(None, max_length=50)
    related_entity_id: Optional[UUID] = None


class NotificationResponse(NotificationBase):
    id: UUID
    user_id: UUID
    type: NotificationType
    is_read: bool
    sent_via_email: bool
    sent_via_push: bool
    sent_via_sms: bool
    created_at: datetime
    expires_at: Optional[datetime] = None