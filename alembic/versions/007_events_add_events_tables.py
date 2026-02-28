"""add events tables

Revision ID: 007_events
Revises: 006_accounts
Create Date: 2026-02-15 22:39:12.731151

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '007_events'
down_revision: Union[str, Sequence[str], None] = '006_accounts'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Events Table
    op.create_table(
        'events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('place_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('creator_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('start_time_utc', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time_utc', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('event_chat_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('blob_storage_id', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['creator_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['place_id'], ['places.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Composite Indexes (Aligning with Model)
    op.create_index('idx_event_time_range', 'events', ['start_time_utc', 'end_time_utc'])
    op.create_index('idx_event_active_start', 'events', ['is_active', 'start_time_utc'])
    op.create_index('idx_event_place_time', 'events', ['place_id', 'start_time_utc'])
    op.create_index('idx_event_account', 'events', ['account_id', 'is_active'])

    # 3. Standard Column Indexes
    op.create_index(op.f('ix_events_name'), 'events', ['name'])

    # 4. Trigger for updated_at
    op.execute("""
        CREATE TRIGGER update_events_updated_at 
        BEFORE UPDATE ON events
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

def downgrade() -> None:
    # Clean rollback: Only drop what this migration created
    op.execute("DROP TRIGGER IF EXISTS update_events_updated_at ON events")
    op.drop_table('events')