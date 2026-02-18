from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID

class GeolocationBase(BaseModel):
    """Base schema for Geolocation with ORM mapping enabled"""
    model_config = ConfigDict(from_attributes=True)

    continent: str = Field(..., min_length=2, max_length=2, description="ISO 2-letter continent code")
    continent_name: str = Field(..., min_length=1, max_length=100)


class GeolocationCreate(GeolocationBase):
    """Schema for creating a geolocation entry"""
    # Denormalized counts usually start at 0 as defined in the model
    places_count: Optional[int] = 0
    country_count: Optional[int] = 0


class GeolocationUpdate(BaseModel):
    """Schema for updating geolocation data or counts"""
    continent: Optional[str] = Field(None, min_length=2, max_length=2)
    continent_name: Optional[str] = Field(None, min_length=1, max_length=100)
    places_count: Optional[int] = Field(None, ge=0)
    country_count: Optional[int] = Field(None, ge=0)


class GeolocationResponse(GeolocationBase):
    """Schema for geolocation responses"""
    id: UUID
    places_count: int
    country_count: int
    created_at: datetime
    updated_at: datetime