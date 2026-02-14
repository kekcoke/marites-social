from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum

class PaymentMethodEnum(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"


class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    FAILED = "failed"


class OrderBase(BaseModel):
    """Base schema for Order"""
    event_id: UUID
    ticket_price: int = Field(..., ge=0, description="Price in cents")
    total_tax: int = Field(..., ge=0, description="Tax in cents")
    total_price: int = Field(..., ge=0, description="Total in cents")
    currency: str = Field(default="USD", max_length=3)
    payment_method: PaymentMethodEnum
    ticket_quantity: int = Field(default=1, ge=1)
    ticket_type: Optional[str] = Field(None, max_length=100)


class OrderCreate(OrderBase):
    """Schema for creating an order"""
    user_id: Optional[UUID] = None  # Optional for guest checkout
    session_id: Optional[str] = Field(None, max_length=255)


class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    status: Optional[OrderStatusEnum] = None
    payment_processor_id: Optional[str] = Field(None, max_length=255)


class OrderResponse(OrderBase):
    """Schema for order responses"""
    id: UUID
    confirmation_id: str
    user_id: Optional[UUID] = None
    status: OrderStatusEnum
    payment_processor_id: Optional[str] = None
    session_id: Optional[str] = None
    time_utc: datetime
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    updated_at: datetime

    class Config:
        from_attributes = True