from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    func,
    Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.enums import IntegrationProvider, IntegrationType
from app.db.connection import Base
import uuid


class IntegrationTypeModel(Base):
    """Reference table for integration types"""
    __tablename__ = "integration_types"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    icon = Column(String(50))
    is_active = Column(Boolean, server_default='true', nullable=False)
    sort_order = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    integrations = relationship("Integration", back_populates="type_rel")

    __table_args__ = (
        Index('ix_integration_types_code', 'code', unique=True),
    )

    @property
    def enum(self) -> IntegrationType:
        """Get enum value from code"""
        return IntegrationType[self.code] if self.code else None


class IntegrationProviderModel(Base):
    """Reference table for integration providers"""
    __tablename__ = "integration_providers"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    website = Column(String(255))
    docs_url = Column(String(255))
    is_active = Column(Boolean, server_default='true', nullable=False)
    sort_order = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    integrations = relationship("Integration", back_populates="provider_rel")

    __table_args__ = (
        Index('ix_integration_providers_code', 'code', unique=True),
    )

    @property
    def enum(self) -> IntegrationProvider:
        """Get enum value from code"""
        return IntegrationProvider[self.code] if self.code else None


class Integration(Base):
    """
    SQLAlchemy model for third-party integrations
    Stores integration configurations per account
    """
    __tablename__ = "integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Reference table foreign keys
    integration_type_id = Column(
        Integer,
        ForeignKey("integration_types.id", ondelete="RESTRICT"),
        nullable=False
    )
    
    integration_provider_id = Column(
        Integer,
        ForeignKey("integration_providers.id", ondelete="RESTRICT"),
        nullable=False
    )
    
    # Integration details
    name = Column(String(100), nullable=False)
    
    # Configuration (should be encrypted in production)
    config = Column(JSONB, nullable=True)
    
    # OAuth tokens
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Webhook
    webhook_url = Column(String(500), nullable=True)
    webhook_secret = Column(String(255), nullable=True)
    
    # Status
    is_active = Column(Boolean, nullable=False, server_default='true')
    is_configured = Column(Boolean, nullable=False, server_default='false')
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error tracking
    last_error = Column(Text, nullable=True)
    last_error_at = Column(DateTime(timezone=True), nullable=True)
    error_count = Column(Integer, nullable=False, server_default='0')
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    account = relationship("Account", back_populates="integrations")
    type_rel = relationship("IntegrationTypeModel", back_populates="integrations")
    provider_rel = relationship("IntegrationProviderModel", back_populates="integrations")
    
    __table_args__ = (
        Index('ix_integrations_account_id', 'account_id'),
        Index('ix_integrations_integration_type_id', 'integration_type_id'),
        Index('ix_integrations_integration_provider_id', 'integration_provider_id'),
        Index('ix_integrations_account_type', 'account_id', 'integration_type_id'),
        Index('ix_integrations_provider_active', 'integration_provider_id', 'is_active'),
    )

    @property
    def type(self) -> IntegrationType:
        """Get integration type enum from relation"""
        return self.type_rel.enum if self.type_rel else None

    @type.setter
    def type(self, value: IntegrationType):
        """Set integration_type_id from enum value"""
        if isinstance(value, IntegrationType):
            type_model = IntegrationTypeModel.query.filter_by(code=value.name).first()
            if type_model:
                self.integration_type_id = type_model.id

    @property
    def provider(self) -> IntegrationProvider:
        """Get integration provider enum from relation"""
        return self.provider_rel.enum if self.provider_rel else None

    @provider.setter
    def provider(self, value: IntegrationProvider):
        """Set integration_provider_id from enum value"""
        if isinstance(value, IntegrationProvider):
            provider = IntegrationProviderModel.query.filter_by(code=value.name).first()
            if provider:
                self.integration_provider_id = provider.id