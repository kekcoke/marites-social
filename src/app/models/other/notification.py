from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    func,
    Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.enums import NotificationType
from app.db.connection import Base
import uuid


class NotificationTypeModel(Base):
    """Reference table for notification types"""
    __tablename__ = "notification_types"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    icon = Column(String(50))
    requires_email = Column(Boolean, server_default='false', nullable=False)
    requires_push = Column(Boolean, server_default='false', nullable=False)
    requires_sms = Column(Boolean, server_default='false', nullable=False)
    is_active = Column(Boolean, server_default='true', nullable=False)
    sort_order = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    notifications = relationship("Notification", back_populates="notification_type_rel")

    __table_args__ = (
        Index('ix_notification_types_code', 'code', unique=True),
    )

    @property
    def enum(self) -> NotificationType:
        """Get enum value from code"""
        return NotificationType[self.code] if self.code else None


class Notification(Base):
    """User notifications"""
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    notification_type_id = Column(
        Integer,
        ForeignKey("notification_types.id", ondelete="RESTRICT"),
        nullable=False
    )
    
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Reference to related entity
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Status
    is_read = Column(Boolean, server_default='false', nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Delivery channels
    sent_via_email = Column(Boolean, server_default='false', nullable=False)
    sent_via_push = Column(Boolean, server_default='false', nullable=False)
    sent_via_sms = Column(Boolean, server_default='false', nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    notification_type_rel = relationship("NotificationTypeModel", back_populates="notifications")
    
    __table_args__ = (
        Index('ix_notifications_user_id', 'user_id'),
        Index('ix_notifications_notification_type_id', 'notification_type_id'),
        Index('ix_notifications_created_at', 'created_at'),
        Index('ix_notifications_related_entity', 'related_entity_type', 'related_entity_id'),
        Index('idx_notification_user_unread', 'user_id', 'is_read', 'created_at'),
        Index('idx_notification_expire', 'expires_at'),
    )

    @property
    def type(self) -> NotificationType:
        """Get notification type enum from relation"""
        return self.notification_type_rel.enum if self.notification_type_rel else None

    @type.setter
    def type(self, value: NotificationType):
        """Set notification_type_id from enum value"""
        if isinstance(value, NotificationType):
            notif_type = NotificationTypeModel.query.filter_by(code=value.name).first()
            if notif_type:
                self.notification_type_id = notif_type.id