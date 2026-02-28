"""add orders tables

Revision ID: 009_orders
Revises: 008_chatrooms
Create Date: 2026-02-15 23:05:29.249329

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '009_orders'
down_revision: Union[str, Sequence[str], None] = '008_chatrooms'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ========== CREATE REFERENCE TABLES ==========
    
    # 1. Payment methods table
    op.create_table(
        'payment_methods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255)),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('sort_order', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_payment_methods_code', 'payment_methods', ['code'], unique=True)
    
    # 2. Order statuses table
    op.create_table(
        'order_statuses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255)),
        sa.Column('is_final', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('color', sa.String(20)),
        sa.Column('sort_order', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_order_statuses_code', 'order_statuses', ['code'], unique=True)

    # ========== INSERT REFERENCE DATA ==========
    
    # Insert payment methods
    op.bulk_insert(
        sa.table('payment_methods',
            sa.column('code', sa.String),
            sa.column('name', sa.String),
            sa.column('description', sa.String),
            sa.column('sort_order', sa.Integer)
        ),
        [
            {'code': 'CREDIT_CARD', 'name': 'Credit Card', 'description': 'Credit card payment', 'sort_order': 10},
            {'code': 'DEBIT_CARD', 'name': 'Debit Card', 'description': 'Debit card payment', 'sort_order': 20},
            {'code': 'PAYPAL', 'name': 'PayPal', 'description': 'PayPal payment', 'sort_order': 30},
            {'code': 'STRIPE', 'name': 'Stripe', 'description': 'Stripe payment', 'sort_order': 40},
            {'code': 'APPLE_PAY', 'name': 'Apple Pay', 'description': 'Apple Pay', 'sort_order': 50},
            {'code': 'GOOGLE_PAY', 'name': 'Google Pay', 'description': 'Google Pay', 'sort_order': 60},
            {'code': 'BANK_TRANSFER', 'name': 'Bank Transfer', 'description': 'Direct bank transfer', 'sort_order': 70},
            {'code': 'CRYPTO', 'name': 'Cryptocurrency', 'description': 'Cryptocurrency payment', 'sort_order': 80},
        ]
    )

    # Insert order statuses
    op.bulk_insert(
        sa.table('order_statuses',
            sa.column('code', sa.String),
            sa.column('name', sa.String),
            sa.column('description', sa.String),
            sa.column('is_final', sa.Boolean),
            sa.column('color', sa.String),
            sa.column('sort_order', sa.Integer)
        ),
        [
            {'code': 'PENDING', 'name': 'Pending', 'description': 'Order pending confirmation', 'is_final': False, 'color': 'yellow', 'sort_order': 10},
            {'code': 'CONFIRMED', 'name': 'Confirmed', 'description': 'Order confirmed', 'is_final': False, 'color': 'blue', 'sort_order': 20},
            {'code': 'COMPLETED', 'name': 'Completed', 'description': 'Order completed successfully', 'is_final': True, 'color': 'green', 'sort_order': 30},
            {'code': 'CANCELLED', 'name': 'Cancelled', 'description': 'Order cancelled', 'is_final': True, 'color': 'red', 'sort_order': 40},
            {'code': 'REFUNDED', 'name': 'Refunded', 'description': 'Order refunded', 'is_final': True, 'color': 'purple', 'sort_order': 50},
            {'code': 'FAILED', 'name': 'Failed', 'description': 'Order failed', 'is_final': True, 'color': 'red', 'sort_order': 60},
        ]
    )

    # ========== CREATE ORDERS TABLE ==========
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('confirmation_id', sa.String(length=50), nullable=False),
        
        # Foreign keys
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Reference table foreign keys
        sa.Column('payment_method_id', sa.Integer(), nullable=False),
        sa.Column('status_id', sa.Integer(), nullable=False, server_default='1'),  # Default to PENDING
        
        # Pricing - stored in cents
        sa.Column('ticket_price', sa.Integer(), nullable=False),
        sa.Column('total_tax', sa.Integer(), nullable=False),
        sa.Column('total_price', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        
        # Payment information
        sa.Column('payment_processor_id', sa.String(length=255), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        
        # Timestamps
        sa.Column('time_utc', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('refunded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        # Ticket details
        sa.Column('ticket_quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('ticket_type', sa.String(length=100), nullable=True),
        
        # Foreign key constraints
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['payment_method_id'], ['payment_methods.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['status_id'], ['order_statuses.id'], ondelete='RESTRICT'),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('confirmation_id')
    )
    
    # ========== CREATE INDEXES ==========
    op.create_index('ix_orders_user_id', 'orders', ['user_id'])
    op.create_index('ix_orders_event_id', 'orders', ['event_id'])
    op.create_index('ix_orders_payment_method_id', 'orders', ['payment_method_id'])
    op.create_index('ix_orders_status_id', 'orders', ['status_id'])
    op.create_index('ix_orders_user_time', 'orders', ['user_id', 'time_utc'])
    op.create_index('ix_orders_event_time', 'orders', ['event_id', 'time_utc'])
    op.create_index('ix_orders_status_time', 'orders', ['status_id', 'time_utc'])
    
    # ========== CREATE TRIGGERS ==========
    op.execute("""
        CREATE TRIGGER update_orders_updated_at 
        BEFORE UPDATE ON orders
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)
    
    op.execute("""
        CREATE TRIGGER update_payment_methods_updated_at 
        BEFORE UPDATE ON payment_methods
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)
    
    op.execute("""
        CREATE TRIGGER update_order_statuses_updated_at 
        BEFORE UPDATE ON order_statuses
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS update_orders_updated_at ON orders")
    op.execute("DROP TRIGGER IF EXISTS update_payment_methods_updated_at ON payment_methods")
    op.execute("DROP TRIGGER IF EXISTS update_order_statuses_updated_at ON order_statuses")
    
    # Drop tables in reverse order
    op.drop_table('orders')
    op.drop_table('order_statuses')
    op.drop_table('payment_methods')
    
    # Drop any remaining enum types if they exist
    enum_types = ['paymentmethod', 'orderstatus']
    for enum_name in enum_types:
        op.execute(f"DROP TYPE IF EXISTS {enum_name} CASCADE")