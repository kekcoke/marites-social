from typing import List
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Boolean,
    Text,
    DateTime,
    func,
    Index,
    ARRAY
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship
from app.db.connection import Base
import uuid


class Event(Base):
    """SQLAlchemy model for events"""
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(300), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Foreign keys
    place_id = Column(
        UUID(as_uuid=True),
        ForeignKey("places.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    creator_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Time fields - CRITICAL for time-series queries
    start_time_utc = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time_utc = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Chat room references - array for multiple chat rooms
    event_chat_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    
    # Blob storage reference for media/files
    blob_storage_id = Column(String(500), nullable=True)
    
    # Relationships
    place = relationship("Place", back_populates="events")
    account = relationship("Account", back_populates="events")
    chat_rooms = relationship("ChatRoom", back_populates="event", passive_deletes=True)
    orders = relationship("Order", back_populates="event", passive_deletes=True)

    # Event -> EventAttendee
    attendees: Mapped[List["EventAttendee"]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan"
    )

    # Event -> User (creator)
    creator: Mapped["User"] = relationship(
        back_populates="created_events"
    )

    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_event_time_range', 'start_time_utc', 'end_time_utc'),
        Index('idx_event_active_start', 'is_active', 'start_time_utc'),
        Index('idx_event_place_time', 'place_id', 'start_time_utc'),
        Index('idx_event_account', 'account_id', 'is_active'),
    )

    def __repr__(self):
        return f"<Event(id={self.id}, name='{self.name}', start='{self.start_time_utc}')>"


# TIME-SERIES DATABASE CONSIDERATION:
# Events are perfect candidates for time-series optimization:
# - Primary query pattern: time-range based queries
# - High read-to-write ratio
# - Natural partitioning by time
# 
# RECOMMENDATIONS:
# 1. Use PostgreSQL table partitioning by time range (monthly/quarterly)
# 2. Consider TimescaleDB extension for automatic partitioning and compression
# 3. Archive old events (>1 year) to separate cold storage
# 4. Use materialized views for upcoming events (next 30 days)
# 5. Separate analytics queries to read replicas or OLAP database
#
# Example TimescaleDB setup:
# SELECT create_hypertable('events', 'start_time_utc', chunk_time_interval => INTERVAL '1 month');
# SELECT add_retention_policy('events', INTERVAL '2 years');