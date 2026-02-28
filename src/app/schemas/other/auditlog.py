from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Any, Dict
from uuid import UUID

class AuditLogBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    action: str = Field(..., max_length=100)
    entity_type: str = Field(..., max_length=50)
    entity_id: UUID
    user_id: Optional[UUID] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = Field(None, max_length=500)


class AuditLogCreate(AuditLogBase):
    """Internal schema for recording backend events"""
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None


class AuditLogResponse(AuditLogBase):
    id: UUID
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    created_at: datetime