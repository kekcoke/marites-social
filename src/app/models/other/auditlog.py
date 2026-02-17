from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    func,
    Index,
    Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.connection import Base
import uuid
import enum


class AuditLog(Base):
    """Audit trail for important actions"""
    __tablename__ = "audit_logs"

    id = Column(UUID(
        as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=True
    )

    action = Column(
        String(100), 
        nullable=False, 
        index=True
    )

    entity_type = Column(String(50), nullable=False)
    entity_id = Column(
        UUID(as_uuid=True), 
        nullable=False
    )

    # Store old and new values for changes
    old_values = Column(JSONB, nullable=True)
    new_values = Column(JSONB, nullable=True)

    # Request metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    __table_args__ = (
        Index('ix_audit_action', 'action'),
        Index('ix_audit_logs_created_at', 'created_at'),
        Index('ix_audit_logs_user_id', 'user_id'),
        Index('ix_audit_entity_lookup', 'entity_type', 'entity_id'),
    )

