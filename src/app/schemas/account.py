from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum

class AccountTypeEnum(str, Enum):
    CONSUMER = "consumer"
    COMMUNITY = "community"
    NGO = "ngo"
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"


class AccountBase(BaseModel):
    """Base schema for Account"""

    name: str = Field(..., min_length=1, max_length=200)
    type: AccountTypeEnum
    user_id: UUID


class AccountCreate(AccountBase):
    """Schema for creating an account"""

    tax_number: Optional[str] = Field(None, max_length=50)
    tax_country: Optional[str] = Field(None, max_length=3)
    subscription_tier: Optional[str] = Field(None, max_length=50)


class AccountUpdate(BaseModel):
    """Schema for updating an account"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[AccountTypeEnum] = None
    tax_number: Optional[str] = Field(None, max_length=50)
    tax_country: Optional[str] = Field(None, max_length=3)
    subscription_tier: Optional[str] = Field(None, max_length=50)
    is_active: Optional[str] = None
    is_verified: Optional[str] = None


class AccountResponse(AccountBase):
    """Schema for account responses"""

    id: UUID
    tax_country: Optional[str] = None
    subscription_tier: Optional[str] = None
    subscription_expires_at: Optional[datetime] = None
    is_active: str
    is_verified: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True