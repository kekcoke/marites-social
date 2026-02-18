from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from app.core.enums import AccountType, SubscriptionTier

class AccountBase(BaseModel):
    """Base schema for Account"""
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(..., min_length=1, max_length=200)
    type: AccountType
    user_id: UUID


class AccountCreate(AccountBase):
    """Schema for creating an account"""
    tax_number: Optional[str] = Field(None, max_length=50)
    tax_country: Optional[str] = Field(None, max_length=3)
    subscription_tier: Optional[str] = Field(None, max_length=50)


class AccountUpdate(BaseModel):
    """Schema for updating an account"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    type: Optional[AccountType] = None
    tax_number: Optional[str] = Field(None, max_length=50)
    tax_country: Optional[str] = Field(None, max_length=3)
    subscription_tier: Optional[SubscriptionTier] = None
    is_active: Optional[bool] = None
    is_verified: Optional[str] = None


class AccountResponse(AccountBase):
    """Schema for account responses"""
    id: UUID
    tax_country: Optional[str] = None
    subscription_tier: Optional[str] = None
    subscription_expires_at: Optional[datetime] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime