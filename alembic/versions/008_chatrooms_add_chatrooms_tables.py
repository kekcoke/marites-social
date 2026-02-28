"""add chatrooms tables

Revision ID: 008_chatrooms
Revises: 007_events
Create Date: 2026-02-15 22:52:58.146884

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '008_chatrooms'
down_revision: Union[str, Sequence[str], None] = '007_events'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Chat Rooms Table
    op.create_table(
        'chat_rooms',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('accounts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('events.id', ondelete='CASCADE'), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('num_active_users_in_session', sa.Integer(), server_default='0', nullable=False),
        sa.Column('activity_level_score', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('grpc_service_url', sa.String(length=500), nullable=True),
        sa.Column('grpc_room_token', sa.String(length=255), nullable=True),
        sa.Column('created_on', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('archived_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Composite Indexes for gRPC Service Queries
    op.create_index('idx_chatroom_event', 'chat_rooms', ['event_id', 'account_id'])
    op.create_index('idx_chatroom_active', 'chat_rooms', ['num_active_users_in_session', 'last_activity_at'])
    
    # 3. Standard Single-Column Indexes
    op.create_index(op.f('ix_chat_rooms_account_id'), 'chat_rooms', ['account_id'])

    # 4. Create Update Trigger (Fixed missing logic)
    op.execute("""
        CREATE TRIGGER update_chat_rooms_updated_at 
        BEFORE UPDATE ON chat_rooms
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

def downgrade() -> None:
    # Drop trigger first, then the table (indexes are dropped automatically with the table)
    op.execute("DROP TRIGGER IF EXISTS update_chat_rooms_updated_at ON chat_rooms")
    op.drop_table('chat_rooms')