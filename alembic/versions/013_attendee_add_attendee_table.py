"""add attendee table

Revision ID: 013_attendee
Revises: 012_comments
Create Date: 2026-02-16 14:25:38.655493

"""
from typing import Sequence, Union

from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '013_attendee'
down_revision: Union[str, Sequence[str], None] = '012_comments'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========== ATTENDEE STATUS ==========
    op.create_table(
        'attendee_statuses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Get the table reference
    attendee_statuses_table = table(
        'attendee_statuses',
        column('code', String(50)),
        column('name', String(100)),
        column('description', String(200)),
        column('color', String(20)),
        column('sort_order', Integer)
    )
    
    op.bulk_insert(attendee_statuses_table, [
        {'code': 'interested', 'name': 'Interested', 'description': None, 'color': '#ffb302', 'sort_order': 1},
        {'code': 'going', 'name': 'Going', 'description': None, 'color': '#3cb44b', 'sort_order': 2},
        {'code': 'not_going', 'name': 'Not Going', 'description': None, 'color': '#e6194B', 'sort_order': 3},
        {'code': 'attended', 'name': 'Attended', 'description': None, 'color': '#4363d8', 'sort_order': 4}
    ])

    # Index
    op.create_index('ix_attendee_statuses_code', 'attendee_statuses', ['code'])

    # ========== EVENT ATTENDEES TABLE ==========
    op.create_table(
        'event_attendees',
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('attendee_status_id', sa.Integer(), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rsvp_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('checked_in_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['attendee_status_id'], ['attendee_statuses.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('event_id', 'user_id')
    )
    
    #Index
    op.create_index('idx_event_attendee_status', 'event_attendees', ['event_id', 'attendee_status_id'])
    op.create_index('idx_attendee_user_status', 'event_attendees', ['user_id', 'attendee_status_id'])

    # ========== CREATE TRIGGERS ==========
    op.execute("""
        CREATE TRIGGER update_attendee_statuses_updated_at 
        BEFORE UPDATE ON attendee_statuses
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS update_attendee_statuses_updated_at ON notification_types")
    op.drop_table('event_attendees')
    op.drop_table('attendee_statuses')
    sa.Enum(name='attendeestatus').drop(op.get_bind(), checkfirst=True)