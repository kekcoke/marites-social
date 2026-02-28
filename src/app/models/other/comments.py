from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Boolean,
    DateTime,
    Text,
    func,
    Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.connection import Base
import uuid


class Comment(Base):
    """Comments on posts or events"""
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Polymorphic - can comment on posts or events
    commentable_type = Column(String(50), nullable=False)
    commentable_id = Column(UUID(as_uuid=True), nullable=False)
    
    content = Column(Text, nullable=False)
    
    # Nested comments - reply to another comment
    parent_comment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True
    )
    
    # File attachments - store in blob storage
    attachments = Column(JSONB, nullable=True)
    
    # Moderation
    is_deleted = Column(Boolean, server_default='false', nullable=False)
    is_edited = Column(Boolean, server_default='false', nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    parent_comment = relationship("Comment", remote_side=[id], backref="replies")
    
    __table_args__ = (
        Index('ix_comments_user_id', 'user_id'),
        Index('ix_comments_commentable_type', 'commentable_type'),
        Index('ix_comments_commentable_id', 'commentable_id'),
        Index('ix_comments_parent_comment_id', 'parent_comment_id'),
        Index('ix_comments_created_at', 'created_at'),
        Index('idx_comment_commentable', 'commentable_type', 'commentable_id', 'created_at'),
        Index('idx_comment_user', 'user_id', 'created_at'),
    )