from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Integer,
    DateTime,
    Boolean,
    func,
    Index,
    Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.enums import PaymentMethod, OrderStatus
from app.db.connection import Base
import uuid


class PaymentMethodModel(Base):
    """Reference table for payment methods"""
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    is_active = Column(Boolean, server_default='true', nullable=False)
    sort_order = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    orders = relationship("Order", back_populates="payment_method_rel")

    @property
    def enum_value(self) -> PaymentMethod:
        """Get enum value from code"""
        return PaymentMethod[self.code]


class OrderStatusModel(Base):
    """Reference table for order statuses"""
    __tablename__ = "order_statuses"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    is_final = Column(Boolean, server_default='false', nullable=False)
    color = Column(String(20))
    sort_order = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    orders = relationship("Order", back_populates="status_rel")

    @property
    def enum_value(self) -> OrderStatus:
        """Get enum value from code"""
        return OrderStatus[self.code]


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
    
    # Reference table foreign keys
    payment_method_id = Column(
        Integer,
        ForeignKey("payment_methods.id", ondelete="RESTRICT"),
        nullable=False
    )
    
    status_id = Column(
        Integer,
        ForeignKey("order_statuses.id", ondelete="RESTRICT"),
        nullable=False,
        server_default='1'  # Default to PENDING (id=1)
    )
    
    # Pricing - store in cents to avoid floating point issues
    ticket_price = Column(Integer, nullable=False)  # In cents
    total_tax = Column(Integer, nullable=False)  # In cents
    total_price = Column(Integer, nullable=False)  # In cents
    currency = Column(String(3), nullable=False, server_default="USD")  # ISO 4217
    
    # Payment information
    payment_processor_id = Column(String(255), nullable=True)  # Stripe charge ID, etc.
    session_id = Column(String(255), nullable=True)
    
    # Timestamps - crucial for time-series analysis
    time_utc = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Ticket details
    ticket_quantity = Column(Integer, nullable=False, server_default='1')
    ticket_type = Column(String(100), nullable=True)  # VIP, General, Early Bird, etc.
    
    # Relationships
    user = relationship("User")
    event = relationship("Event", back_populates="orders")
    attendees = relationship("EventAttendee", back_populates="order")  # One order can have multiple attendees
    payment_method_rel = relationship("PaymentMethodModel", back_populates="orders")
    status_rel = relationship("OrderStatusModel", back_populates="orders")
    
    # ALL INDEXES FROM MIGRATION INCLUDED
    __table_args__ = (
        # Single-column indexes
        Index('ix_orders_user_id', 'user_id'),
        Index('ix_orders_event_id', 'event_id'),
        Index('ix_orders_payment_method_id', 'payment_method_id'),
        Index('ix_orders_status_id', 'status_id'),
        
        # Composite indexes for common query patterns
        Index('ix_orders_user_time', 'user_id', 'time_utc'),
        Index('ix_orders_event_time', 'event_id', 'time_utc'),
        Index('ix_orders_status_time', 'status_id', 'time_utc'),
    )

    @property
    def payment_method(self) -> PaymentMethod:
        """Get enum value from payment method relation"""
        return self.payment_method_rel.enum_value if self.payment_method_rel else None

    @payment_method.setter
    def payment_method(self, value: PaymentMethod):
        """Set payment_method_id from enum value"""
        if isinstance(value, PaymentMethod):
            method = PaymentMethodModel.query.filter_by(code=value.name).first()
            if method:
                self.payment_method_id = method.id

    @property
    def status(self) -> OrderStatus:
        """Get enum value from status relation"""
        return self.status_rel.enum_value if self.status_rel else None

    @status.setter
    def status(self, value: OrderStatus):
        """Set status_id from enum value"""
        if isinstance(value, OrderStatus):
            status = OrderStatusModel.query.filter_by(code=value.name).first()
            if status:
                self.status_id = status.id

    def __repr__(self):
        status_val = self.status.value if self.status else "unknown"
        return f"<Order(id={self.id}, confirmation='{self.confirmation_id}', status='{status_val}')>"