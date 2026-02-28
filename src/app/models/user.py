import uuid
from sqlalchemy import (
    Column,
    Index,
    String,
    Boolean,
    DateTime,
    func
)
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.connection import Base
from sqlalchemy.orm import relationship
from typing import List

class User(Base):
    """SQLAlchemy model for users table"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, server_default='true')

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_activity = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # --- RELATIONSHIPS ---

    # 1. Accounts (Owner & Inviter)
    owned_accounts = relationship("Account", back_populates="owner", foreign_keys="Account.user_id")
    invitations_sent = relationship("AccountMember", back_populates="inviter", foreign_keys="AccountMember.invited_by")
    account_memberships = relationship("AccountMember", back_populates="user", foreign_keys="AccountMember.user_id")

    # 2. Events & Attendance
    event_attendances: Mapped[List["EventAttendee"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # User -> Event (creator relationship)
    created_events: Mapped[List["Event"]] = relationship(
        back_populates="creator"
    )

    
    # 3. Communications & Content
    posts = relationship("Post", back_populates="user", passive_deletes=True)
    comments = relationship("Comment", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    owned_chatrooms = relationship("ChatRoom", back_populates="owner")

    # 4. Transactions
    orders = relationship("Order", back_populates="user")

    __table_args__ = (
        # Partial indexes for soft-delete: Email must be unique among active users only
        Index('ix_users_email_active', 'email', unique=True, postgresql_where=(deleted_at == None)),
        Index('ix_users_username_active', 'username', unique=True, postgresql_where=(deleted_at == None)),
    )
    
    def __repr__(self):
        return f"<Users(id={self.id}, username='{self.username}', email='{self.email}')>"