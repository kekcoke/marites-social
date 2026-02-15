from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    DateTime,
    func,
    Index,
    Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.connection import Base
import uuid
import enum

class AccountMember(Base):
    """Junction table for account team members"""
    __tablename__ = "account_members"

    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    role = Column(SQLEnum(AccountRole), default=AccountRole.MEMBER, nullable=False)
    permissions = Column(JSONB, nullable=True)  # Fine-grained permissions
    
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_account_member_user', 'user_id'),
        Index('idx_account_member_role', 'account_id', 'role'),
    )


class AccountRole(enum.Enum):
    """Roles for account members"""
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"


class AccountType(enum.Enum):
    """Account type classifications"""
    CONSUMER = "consumer"
    COMMUNITY = "community"
    NGO = "ngo"
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"


class SubscriptionTier(enum.Enum):
    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"


class Account(Base):
    """
    SQLAlchemy model for accounts
    Represents organizations/entities that can host events
    """
    __tablename__ = "accounts"

    id = Column(UUID(
        as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name = Column(String(200), nullable=False, index=True)
    
    # Owner/primary user
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Account type
    type = Column(
        SQLEnum(AccountType), 
        nullable=False, 
        default=AccountType.CONSUMER
    )
    
    # Tax information - store securely, consider encryption at rest
    tax_number = Column(String(50), nullable=True)  # EIN, VAT, etc.
    tax_country = Column(String(3), nullable=True)  # ISO 3166-1 alpha-3
    
    # Billing information reference (store in separate secure table)
    billing_address_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Subscription/tier information
    subscription_tier = Column(
        SQLEnum(SubscriptionTier)
        nullable=False,
        default=SubscriptionTier.FREE
    ) 
    subscription_expires_at = Column(
        DateTime(timezone=True), 
        nullable=True
    )  # Create serverless job that converts to FREE after trial-period
    
    # Status
    is_active = Column(String(20), default="active", nullable=False)
    is_verified = Column(String(20), default="false", nullable=False)
    
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
    owner = relationship("User", back_populates="accounts")
    events = relationship("Event", back_populates="account", passive_deletes=True)
    chat_rooms = relationship("ChatRoom", back_populates="account", passive_deletes=True)
    integrations = relationship("Integration", back_populates="account", passive_deletes=True)
    
    __table_args__ = (
        Index('idx_account_type_active', 'type', 'is_active'),
        Index('idx_account_user', 'user_id'),
    )

    def __repr__(self):
        return f"<Account(id={self.id}, name='{self.name}', type='{self.type.value}')>"


# SECURITY CONSIDERATIONS:
# 1. Tax numbers and billing info should be encrypted at rest
# 2. Use SQLAlchemy TypeDecorator for transparent encryption/decryption
# 3. Store encryption keys in secure vault (AWS KMS, HashiCorp Vault)
# 4. Audit log all access to sensitive account data
# 5. Implement row-level security (RLS) in PostgreSQL