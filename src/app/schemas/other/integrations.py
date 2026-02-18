from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import UUID
from app.core.enums import IntegrationProvider, IntegrationType

class IntegrationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    account_id: UUID
    is_active: bool = True


class IntegrationCreate(IntegrationBase):
    type: IntegrationType
    provider: IntegrationProvider
    config: Dict[str, Any] = Field(default_factory=dict)
    credentials: Dict[str, Any] = Field(default_factory=dict)


class IntegrationUpdate(BaseModel):
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    error_message: Optional[str] = None


class IntegrationResponse(IntegrationBase):
    id: UUID
    type: IntegrationType
    provider: IntegrationProvider
    config: Dict[str, Any]
    last_sync_at: Optional[datetime] = None
    error_message: Optional[str] = None