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
    payment_method_enum = postgresql.ENUM(
        'CREDIT_CARD', 'DEBIT_CARD', 'PAYPAL', 'STRIPE', 
        'APPLE_PAY', 'GOOGLE_PAY', 'BANK_TRANSFER', 'CRYPTO',
        name='paymentmethod',
        create_type=False
    )

    order_status_enum = postgresql.ENUM(
        'PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED', 'REFUNDED', 'FAILED',
        name='orderstatus',
        create_type=False
    )

    payment_method_enum.create(op.get_bind())
    order_status_enum.create(op.get_bind())
    
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('confirmation_id', sa.String(length=50), nullable=False),
        
        # Foreign keys
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Pricing - stored in cents
        sa.Column('ticket_price', sa.Integer(), nullable=False),
        sa.Column('total_tax', sa.Integer(), nullable=False),
        sa.Column('total_price', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        
        # Payment information
        sa.Column('payment_method', payment_method_enum, nullable=False),
        sa.Column('payment_processor_id', sa.String(length=255), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        
        # Order status
        sa.Column('status', order_status_enum, nullable=False, server_default='PENDING'),
        
        # Timestamps - crucial for time-series
        sa.Column('time_utc', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('refunded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        # Ticket details
        sa.Column('ticket_quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('ticket_type', sa.String(length=100), nullable=True),
        
        # Foreign key constraints
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('confirmation_id')
    )
    
    # Indexes
    op.create_index('ix_orders_user_time', 'orders', ['user_id', 'time_utc'])
    op.create_index('ix_orders_event_time', 'orders', ['event_id', 'time_utc'])
    op.create_index('ix_orders_status_time', 'orders', ['status', 'time_utc'])
    
    # Add trigger for updated_at
    op.execute("""
        CREATE TRIGGER update_orders_updated_at 
        BEFORE UPDATE ON orders
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS update_orders_updated_at ON orders")
    op.drop_table('orders')
    sa.Enum(name='orderstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='paymentmethod').drop(op.get_bind(), checkfirst=True)