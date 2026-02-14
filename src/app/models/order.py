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
    confirmation_id = Column(String(50), unique=True, nullable=False, index=True)
    
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
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)
    
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
    
    # Composite indexes for analytics queries
    __table_args__ = (
        Index('idx_order_time_status', 'time_utc', 'status'),
        Index('idx_order_event_time', 'event_id', 'time_utc'),
        Index('idx_order_user_time', 'user_id', 'time_utc'),
        Index('idx_order_confirmation', 'confirmation_id'),
    )

    def __repr__(self):
        return f"<Order(id={self.id}, confirmation='{self.confirmation_id}', status='{self.status.value}')>"


# TIME-SERIES DATABASE CONSIDERATION:
# Orders are excellent candidates for time-series optimization:
#
# 1. POSTGRESQL PARTITIONING:
#    - Partition by month: orders_2024_01, orders_2024_02, etc.
#    - Automatic routing of queries to relevant partitions
#    - Faster aggregations and analytics
#
# 2. ANALYTICS/OLAP (ClickHouse, BigQuery):
#    - Copy order data to OLAP database for analytics
#    - Real-time dashboards: revenue, sales trends, popular events
#    - Complex aggregations without impacting transactional DB
#    - Columnar storage for fast analytical queries
#
# 3. DATA RETENTION:
#    - Keep hot data (last 6 months) in main PostgreSQL
#    - Warm data (6 months - 2 years) in compressed partitions
#    - Cold data (>2 years) in S3/data warehouse for compliance
#
# 4. STREAMING PIPELINE:
#    - Kafka/Kinesis for real-time order events
#    - Stream to analytics DB, data warehouse, and monitoring
#    - Enable real-time revenue tracking and fraud detection
#
# Example partition setup:
# CREATE TABLE orders_2024_01 PARTITION OF orders
#   FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');