from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Boolean,
    Integer,
    Float,
    Text,
    DateTime,
    func,
    Index,
    ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.connection import Base
import uuid

class Place(Base):
    """SQLAlchemy model for places/locations"""
    __tablename__ = "places"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )

    name = Column(
        String(200), 
        nullable=False, 
        index=True
    )

    slug = Column(
        String(200), 
        unique=True, 
        nullable=False, 
        index=True
    )
    description = Column(Text, nullable=True)
    
    # Geographic data - consider moving to PostGIS for better spatial queries
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    geo_continent = Column(String(50), nullable=True, index=True)
    country_abbreviation = Column(String(2), nullable=False, index=True)
    timezone = Column(String(50), nullable=False)
    
    # Media URLs - consider moving to separate media table or object storage references
    icon_desktop_url = Column(String(500), nullable=True)
    icon_mobile_url = Column(String(500), nullable=True)
    icon_square_url = Column(String(500), nullable=True)
    social_image_url = Column(String(500), nullable=True)
    
    # Metadata
    tint_color = Column(String(7), nullable=True)  # hex color
    template_id = Column(UUID(as_uuid=True), nullable=True)
    publication_name = Column(String(200), nullable=True)
    
    # Status flags
    is_launched = Column(Boolean, default=False, nullable=False)
    is_subscriber = Column(Boolean, default=False, nullable=False)
    
    # Denormalized counts for performance - update via triggers or async jobs
    event_count = Column(Integer, default=0, nullable=False)
    
    # Featured events - consider separate junction table for many-to-many
    featured_event_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    events = relationship("Event", back_populates="place", passive_deletes=True)
    geolocation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("geolocations.id", ondelete="CASCADE"),
        nullable=False
    )
    geolocation = relationship("Geolocation", back_populates="places")
    
    # Standard indexes
    Index('ix_places_name', 'name'),
    Index('ix_places_slug', 'slug', unique=True),
    Index('ix_places_country_abbreviation', 'country_abbreviation'),
    Index('ix_places_geo_continent', 'geo_continent'),
    Index('ix_places_is_launched', 'is_launched'),

    # Composite indexes
    Index('idx_place_coordinates', 'latitude', 'longitude'),
    Index('idx_place_country_abbreviation_continent', 'country_abbreviation', 'geo_continent'),

    def __repr__(self):
        return f"<Place(id={self.id}, name='{self.name}', country_abbreviation='{self.country_abbreviation}')>"


# SCALING CONSIDERATION: For distance calculations, consider:
# 1. PostGIS extension with geography type and spatial indexes
# 2. Separate read-optimized materialized view
# 3. Caching layer (Redis) for popular searches
# 4. Move to geospatial database (e.g., MongoDB with geospatial indexes)
