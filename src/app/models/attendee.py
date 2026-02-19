from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Integer,
    Boolean,
    DateTime,
    func,
    Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship
from app.core.enums import AttendeeStatus
from app.db.connection import Base


class AttendeeStatuses(Base):
    """Reference table for attendee statuses"""
    __tablename__ = "attendee_statuses"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    color = Column(String(20))
    sort_order = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    event_attendees = relationship("EventAttendee", back_populates="status_rel")

    __table_args__ = (
        Index('ix_attendee_statuses_code', 'code', unique=True),
    )

    @property
    def enum(self) -> AttendeeStatus:
        return AttendeeStatus[self.code] if self.code else None


class EventAttendee(Base):
    """Junction table for event attendees"""
    __tablename__ = "event_attendees"

    event_id = Column(
        UUID(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        primary_key=True
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    attendee_status_id = Column(
        Integer,
        ForeignKey("attendee_statuses.id", ondelete="RESTRICT"),
        nullable=False,
        server_default='1'  # Default to INTERESTED (id=1)
    )
    
    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True
    )
    
    rsvp_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    checked_in_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    # EventAttendee -> User
    user: Mapped["User"] = relationship(
        back_populates="event_attendances"
    )

    # EventAttendee -> Event
    event: Mapped["Event"] = relationship(
        back_populates="attendees"
    )
    order = relationship("Order")
    status_rel = relationship("AttendeeStatuses", back_populates="event_attendees")
    
    __table_args__ = (
        Index('idx_event_attendee_status', 'event_id', 'attendee_status_id'),
        Index('idx_attendee_user_status', 'user_id', 'attendee_status_id')
    )

    @property
    def status(self) -> AttendeeStatus:
        """Get attendee status enum from relation"""
        return self.status_rel.enum if self.status_rel else None

    @status.setter
    def status(self, value: AttendeeStatus):
        """Set attendee_status_id from enum value"""
        if isinstance(value, AttendeeStatus):
            status = AttendeeStatuses.query.filter_by(code=value.name).first()
            if status:
                self.attendee_status_id = status.id