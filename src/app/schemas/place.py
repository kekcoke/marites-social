from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class PlaceBase(BaseModel):
    """Base schema for Place"""

    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    geo_continent: Optional[str] = Field(None, max_length=50)
    country_abbreviation: str = Field(..., min_length=2, max_length=2)
    timezone: str = Field(..., min_length=1, max_length=50)
    
    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v):
        """Validate timezone format"""
        import pytz
        if v not in pytz.all_timezones:
            raise ValueError(f"Invalid timezone: {v}")
        return v

class PlaceCreate(PlaceBase):
    """Schema for creating a place"""

    icon_desktop_url: Optional[str] = Field(None, max_length=500)
    icon_mobile_url: Optional[str] = Field(None, max_length=500)
    icon_square_url: Optional[str] = Field(None, max_length=500)
    social_image_url: Optional[str] = Field(None, max_length=500)
    tint_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    template_id: Optional[UUID] = None
    publication_name: Optional[str] = Field(None, max_length=200)
    is_launched: bool = False
    is_subscriber: bool = False
    geolocation_id: Optional[UUID] = None

class PlaceUpdate(BaseModel):
    """Schema for updating a place - all fields optional"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    geo_continent: Optional[str] = Field(None, max_length=50)
    country_abbreviation: Optional[str] = Field(None, min_length=2, max_length=2)
    timezone: Optional[str] = Field(None, min_length=1, max_length=50)
    icon_desktop_url: Optional[str] = Field(None, max_length=500)
    icon_mobile_url: Optional[str] = Field(None, max_length=500)
    icon_square_url: Optional[str] = Field(None, max_length=500)
    social_image_url: Optional[str] = Field(None, max_length=500)
    tint_color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    is_launched: Optional[bool] = None
    is_subscriber: Optional[bool] = None

class PlaceResponse(PlaceBase):
    """Schema for place responses"""

    id: UUID
    icon_desktop_url: Optional[str] = None
    icon_mobile_url: Optional[str] = None
    icon_square_url: Optional[str] = None
    social_image_url: Optional[str] = None
    tint_color: Optional[str] = None
    template_id: Optional[UUID] = None
    publication_name: Optional[str] = None
    is_launched: bool
    is_subscriber: bool
    event_count: int
    featured_event_ids: Optional[List[UUID]] = None
    created_at: datetime
    updated_at: datetime
    geolocation_id: Optional[UUID] = None

    class Config:
        from_attributes = True

class PlaceWithDistance(PlaceResponse):
    """Place schema with calculated distance from user"""
    
    distance_km: Optional[float] = Field(None, description="Distance in kilometers from user")


class PlaceListResponse(BaseModel):
    """Paginated list of places"""

    items: List[PlaceResponse]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool