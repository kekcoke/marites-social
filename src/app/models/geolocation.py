from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    func,
    Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.connection import Base
import uuid


class Geolocation(Base):
    """SQLAlchemy model for geolocation aggregations"""
    __tablename__ = "geolocations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    continent = Column(String(2), nullable=False, index=True)  # ISO code
    continent_name = Column(String(100), nullable=False)
    
    # Denormalized counts - update via materialized view or scheduled job
    places_count = Column(Integer, server_default='0', default=0, nullable=False)
    country_count = Column(Integer, server_default='0', default=0, nullable=False)
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    places = relationship("Place", back_populates="geolocation")

    def __repr__(self):
        return f"<Geolocation(continent='{self.continent_name}', places={self.places_count})>"


# SCALING CONSIDERATION:
# This table has low cardinality (7 continents) - perfect for caching
# Consider Redis cache with TTL for geolocation data
# Use PostgreSQL materialized views for aggregated counts