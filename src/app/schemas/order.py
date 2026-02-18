from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from app.core.enums import PaymentMethod, OrderStatus


class OrderBase(BaseModel):
    """Base schema for Order"""
    model_config = ConfigDict(from_attributes=True)

    event_id: UUID
    ticket_price: int = Field(..., ge=0, description="Price in cents")
    total_tax: int = Field(..., ge=0, description="Tax in cents")
    total_price: int = Field(..., ge=0, description="Total in cents")
    currency: str = Field(default="USD", max_length=3)
    payment_method: PaymentMethod
    ticket_quantity: int = Field(default=1, ge=1)
    ticket_type: Optional[str] = Field(None, max_length=100)


class OrderCreate(OrderBase):
    """Schema for creating an order"""
    user_id: Optional[UUID] = None  # Optional for guest checkout
    session_id: Optional[str] = Field(None, max_length=255)


class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    status: Optional[OrderStatus] = None
    payment_processor_id: Optional[str] = Field(None, max_length=255)


class OrderResponse(OrderBase):
    """Schema for order responses"""
    id: UUID
    confirmation_id: str = Field(..., max_length=50)
    user_id: Optional[UUID] = None
    status: OrderStatus # Use core enum
    payment_processor_id: Optional[str] = None
    session_id: Optional[str] = None
    time_utc: datetime
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime