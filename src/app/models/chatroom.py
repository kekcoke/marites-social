from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Float,
    DateTime,
    func,
    Index,
    String
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.connection import Base
import uuid


class ChatRoom(Base):
    """
    SQLAlchemy model for chat rooms
    Interfaces with gRPC + Go container for real-time messaging
    """
    __tablename__ = "chat_rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    event_id = Column(
        UUID(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=True,  # Can be null for general community chat
        index=True
    )
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Metadata
    name = Column(String(200), nullable=True)
    description = Column(String(500), nullable=True)
    
    # Real-time metrics - updated frequently by gRPC service
    num_active_users_in_session = Column(Integer, default=0, nullable=False)
    activity_level_score = Column(Float, default=0.0, nullable=False)
    
    # Last activity tracking for cleanup/archival
    last_activity_at = Column(DateTime(timezone=True), nullable=True)
    
    created_on = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    archived_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # gRPC service reference - the actual chat service endpoint
    grpc_service_url = Column(String(500), nullable=True)
    grpc_room_token = Column(String(255), nullable=True)  # Auth token for gRPC service
    
    # Relationships
    account = relationship("Account", back_populates="chat_rooms")
    event = relationship("Event", back_populates="chat_rooms")
    owner = relationship("User", foreign_keys=[owner_id])
    
    # Indexes for queries
    __table_args__ = (
        Index('idx_chatroom_event', 'event_id', 'account_id'),
        Index('idx_chatroom_active', 'num_active_users_in_session', 'last_activity_at'),
    )

    def __repr__(self):
        return f"<ChatRoom(id={self.id}, event_id={self.event_id}, active_users={self.num_active_users_in_session})>"
