from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Integer,
    Float,
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


class PaymentMethod(enum.Enum):
    """Payment method types"""

    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"


class OrderStatus(enum.Enum):
    """Order status types"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    FAILED = "failed"


class Order(Base):
    """SQLAlchemy model for ticket orders"""
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    confirmation_id = Column(String(50), unique=True, nullable=False)
    
    # Foreign keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,  # Allow guest purchases
        index=True
    )

    event_id = Column(
        UUID(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Pricing - store in cents to avoid floating point issues
    ticket_price = Column(Integer, nullable=False)  # In cents
    total_tax = Column(Integer, nullable=False)  # In cents
    total_price = Column(Integer, nullable=False)  # In cents
    currency = Column(String(3), default="USD", nullable=False)  # ISO 4217
    
    # Payment information
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    payment_processor_id = Column(String(255), nullable=True)  # Stripe charge ID, etc.
    session_id = Column(String(255), nullable=True, index=True)  # Checkout session
    
    # Order status
    status = Column(
        SQLEnum(OrderStatus), 
        default=OrderStatus.PENDING, 
        nullable=False, 
        index=True)
    
    # Timestamps - crucial for time-series analysis
    time_utc = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Ticket details
    ticket_quantity = Column(Integer, default=1, nullable=False)
    ticket_type = Column(String(100), nullable=True)  # VIP, General, Early Bird, etc.
    
    # Relationships
    user = relationship("User")
    event = relationship("Event", back_populates="orders")
    
    # Indexes: Define only what isn't naturally indexed by Unique/Primary constraints
    __table_args__ = (
        Index('ix_orders_user_time', 'user_id', 'time_utc'),
        Index('ix_orders_event_time', 'event_id', 'time_utc'),
        Index('ix_orders_status_time', 'status', 'time_utc'),
    )

    def __repr__(self):
        return f"<Order(id={self.id}, confirmation='{self.confirmation_id}', status='{self.status.value}')>"
