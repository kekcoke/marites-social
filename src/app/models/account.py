from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Integer,
    DateTime,
    Boolean,
    func,
    Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.enums import AccountType, AccountRole, SubscriptionTier
from app.db.connection import Base
import uuid

class AccountType(Base):
    """Reference table for account types"""
    __tablename__ = "account_types"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    is_active = Column(Boolean, server_default='true', nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    accounts = relationship("Account", back_populates="account_type_rel")

    @property
    def enum_value(self) -> AccountType:
        """Get enum value from code"""
        return AccountType[self.code]


class SubscriptionTier(Base):
    """Reference table for subscription tiers"""
    __tablename__ = "subscription_tiers"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    price_monthly = Column(Integer)  # Store in cents
    price_yearly = Column(Integer)  # Store in cents
    max_users = Column(Integer)
    max_storage_gb = Column(Integer)
    features = Column(JSONB)
    is_active = Column(Boolean, server_default='true', nullable=False)
    sort_order = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    accounts = relationship("Account", back_populates="subscription_tier_rel")

    @property
    def enum_value(self) -> SubscriptionTier:
        """Get enum value from code"""
        return SubscriptionTier[self.code]


class AccountRoleModel(Base):
    """Reference table for account roles"""
    __tablename__ = "account_roles"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    permissions = Column(JSONB)
    is_active = Column(Boolean, server_default='true', nullable=False)
    level = Column(Integer, comment='Higher number = more privileges')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    account_members = relationship("AccountMember", back_populates="role_rel")

    @property
    def enum_value(self) -> AccountRole:
        """Get enum value from code"""
        return AccountRole[self.code]


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
    
    role_id = Column(
        Integer,
        ForeignKey("account_roles.id", ondelete="RESTRICT"),
        nullable=False,
        server_default='4'  # Default to MEMBER (id=4)
    )
    
    permissions = Column(JSONB, nullable=True)  # Fine-grained permissions
    
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    account = relationship("Account", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])
    inviter = relationship("User", foreign_keys=[invited_by])
    role_rel = relationship("AccountRoleModel", back_populates="account_members")
    
    # Indexes
    __table_args__ = (
        Index('ix_account_members_account_id', 'account_id'),
        Index('ix_account_members_user_id', 'user_id'),
        Index('ix_account_members_role_id', 'role_id'),
        Index('ix_account_members_composite', 'account_id', 'user_id', 'role_id'),
    )

    @property
    def role(self) -> AccountRole:
        """Get enum value from role relation"""
        return self.role_rel.enum_value if self.role_rel else None

    @role.setter
    def role(self, value: AccountRole):
        """Set role_id from enum value"""
        if isinstance(value, AccountRole):
            role = AccountRoleModel.query.filter_by(code=value.name).first()
            if role:
                self.role_id = role.id


class Account(Base):
    """
    SQLAlchemy model for accounts
    Represents organizations/entities that can host events
    """
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    
    # Owner/primary user
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Account type (foreign key to reference table)
    account_type_id = Column(
        Integer,
        ForeignKey("account_types.id", ondelete="RESTRICT"),
        nullable=False,
        server_default='1'  # Default to CONSUMER (id=1)
    )
    
    # Tax information - store securely, consider encryption at rest
    tax_number = Column(String(50), nullable=True)  # EIN, VAT, etc.
    tax_country = Column(String(3), nullable=True)  # ISO 3166-1 alpha-3
    
    # Billing information reference (store in separate secure table)
    # billing_address_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Subscription/tier information (foreign key to reference table)
    subscription_tier_id = Column(
        Integer,
        ForeignKey("subscription_tiers.id", ondelete="RESTRICT"),
        nullable=False,
        server_default='1'  # Default to FREE (id=1)
    )

    subscription_expires_at = Column(
        DateTime(timezone=True), 
        nullable=True
    )  # Create serverless job that converts to FREE after trial-period
    
    # Status
    is_active = Column(Boolean, server_default="true", default=True, nullable=False)
    is_verified = Column(Boolean, server_default="false", default=False, nullable=False)
    
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
    owner = relationship("User", foreign_keys=[user_id], back_populates="owned_accounts")
    account_type_rel = relationship("AccountType", back_populates="accounts")
    subscription_tier_rel = relationship("SubscriptionTier", back_populates="accounts")
    events = relationship("Event", back_populates="account", passive_deletes=True)
    chat_rooms = relationship("ChatRoom", back_populates="account", passive_deletes=True)
    integrations = relationship("Integration", back_populates="account", passive_deletes=True)
    members = relationship("AccountMember", back_populates="account", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('ix_accounts_user_id', 'user_id'),
        Index('ix_accounts_account_type_id', 'account_type_id'),
        Index('ix_accounts_subscription_tier_id', 'subscription_tier_id'),
        Index('ix_accounts_name', 'name'),
        Index('ix_accounts_is_active', 'is_active'),
        # Note: Composite index 'ix_accounts_account_type_id' is separate from single-column index
    )

    @property
    def type(self) -> AccountType:
        """Get enum value from account type relation"""
        return self.account_type_rel.enum_value if self.account_type_rel else None

    @type.setter
    def type(self, value: AccountType):
        """Set account_type_id from enum value"""
        if isinstance(value, AccountType):
            account_type = AccountType.query.filter_by(code=value.name).first()
            if account_type:
                self.account_type_id = account_type.id

    @property
    def subscription_tier(self) -> SubscriptionTier:
        """Get enum value from subscription tier relation"""
        return self.subscription_tier_rel.enum_value if self.subscription_tier_rel else None

    @subscription_tier.setter
    def subscription_tier(self, value: SubscriptionTier):
        """Set subscription_tier_id from enum value"""
        if isinstance(value, SubscriptionTier):
            tier = SubscriptionTier.query.filter_by(code=value.name).first()
            if tier:
                self.subscription_tier_id = tier.id

    def __repr__(self):
        type_val = self.type.value if self.type else "unknown"
        return f"<Account(id={self.id}, name='{self.name}', type='{type_val}')>"