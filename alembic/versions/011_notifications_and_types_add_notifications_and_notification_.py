"""add notifications and notification types tables

Revision ID: 011_notifications_and_types
Revises: 010_integrations
Create Date: 2026-02-16 13:02:52.395347

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '011_notifications_and_types'
down_revision: Union[str, Sequence[str], None] = '010_integrations'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # ========== NOTIFICATION TYPES REFERENCE TABLE ==========
    op.create_table('notification_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255)),
        sa.Column('icon', sa.String(50)),
        sa.Column('requires_email', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('requires_push', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('requires_sms', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('sort_order', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notification_types_code', 'notification_types', ['code'], unique=True)

    # Insert notification types
    op.bulk_insert(
        sa.table('notification_types',
            sa.column('code', sa.String),
            sa.column('name', sa.String),
            sa.column('description', sa.String),
            sa.column('icon', sa.String),
            sa.column('requires_email', sa.Boolean),
            sa.column('requires_push', sa.Boolean),
            sa.column('requires_sms', sa.Boolean),
            sa.column('sort_order', sa.Integer)
        ),
        [
            {'code': 'EVENT_REMINDER', 'name': 'Event Reminder', 'description': 'Reminder about upcoming event', 'icon': 'bell', 'requires_email': True, 'requires_push': True, 'requires_sms': False, 'sort_order': 10},
            {'code': 'EVENT_UPDATE', 'name': 'Event Update', 'description': 'Event details have been updated', 'icon': 'edit', 'requires_email': True, 'requires_push': True, 'requires_sms': False, 'sort_order': 20},
            {'code': 'EVENT_CANCELLED', 'name': 'Event Cancelled', 'description': 'Event has been cancelled', 'icon': 'x-circle', 'requires_email': True, 'requires_push': True, 'requires_sms': True, 'sort_order': 30},
            {'code': 'NEW_MESSAGE', 'name': 'New Message', 'description': 'New message in chat', 'icon': 'message-square', 'requires_email': False, 'requires_push': True, 'requires_sms': False, 'sort_order': 40},
            {'code': 'ORDER_CONFIRMED', 'name': 'Order Confirmed', 'description': 'Order has been confirmed', 'icon': 'check-circle', 'requires_email': True, 'requires_push': True, 'requires_sms': False, 'sort_order': 50},
            {'code': 'ORDER_REFUNDED', 'name': 'Order Refunded', 'description': 'Order has been refunded', 'icon': 'refresh-cw', 'requires_email': True, 'requires_push': True, 'requires_sms': False, 'sort_order': 60},
            {'code': 'ACCOUNT_INVITE', 'name': 'Account Invite', 'description': 'Invitation to join account', 'icon': 'user-plus', 'requires_email': True, 'requires_push': True, 'requires_sms': False, 'sort_order': 70},
            {'code': 'FOLLOWER', 'name': 'New Follower', 'description': 'Someone followed your event/account', 'icon': 'heart', 'requires_email': False, 'requires_push': True, 'requires_sms': False, 'sort_order': 80},
            {'code': 'COMMENT', 'name': 'New Comment', 'description': 'New comment on your post', 'icon': 'message-circle', 'requires_email': False, 'requires_push': True, 'requires_sms': False, 'sort_order': 90},
            {'code': 'MENTION', 'name': 'Mention', 'description': 'Someone mentioned you', 'icon': 'at-sign', 'requires_email': False, 'requires_push': True, 'requires_sms': False, 'sort_order': 100},
        ]
    )

    # ========== NOTIFICATIONS TABLE ==========
    op.create_table('notifications',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('notification_type_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('related_entity_type', sa.String(length=50), nullable=True),
        sa.Column('related_entity_id', sa.UUID(), nullable=True),
        sa.Column('is_read', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sent_via_email', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('sent_via_push', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('sent_via_sms', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['notification_type_id'], ['notification_types.id'], ondelete='RESTRICT'),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indexes
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_notification_type_id', 'notifications', ['notification_type_id'])
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])
    op.create_index('idx_notification_user_unread', 'notifications', ['user_id', 'is_read', 'created_at'])
    op.create_index('idx_notification_expire', 'notifications', ['expires_at'])
    op.create_index('idx_notification_entity', 'notifications', ['related_entity_type', 'related_entity_id'])


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('notification_types')
    
    # Drop any remaining enum types
    op.execute("DROP TYPE IF EXISTS notificationtype CASCADE")