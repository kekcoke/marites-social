from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum

class GeolocationBase(BaseModel):
    """Base schema for Geolocation"""
    continent: str = Field(..., min_length=2, max_length=2)
    continent_name: str = Field(..., min_length=1, max_length=100)


class GeolocationCreate(GeolocationBase):
    """Schema for creating a geolocation"""
    pass


class GeolocationResponse(GeolocationBase):
    """Schema for geolocation responses"""
    id: UUID
    places_count: int
    country_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True