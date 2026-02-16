"""add accounts, account member tables, enums

Revision ID: 006_accounts
Revises: 005_places
Create Date: 2026-02-15 17:52:59.148493

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '006_accounts'
down_revision: Union[str, Sequence[str], None] = '005_places'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create all ENUM types first
    account_type_enum = postgresql.ENUM('CONSUMER', 'COMMUNITY', 'NGO', 'ENTERPRISE', 'GOVERNMENT', name='accounttype')
    sub_tier_enum = postgresql.ENUM('FREE', 'PRO', 'BUSINESS', name='subscriptiontier')
    account_role_enum = postgresql.ENUM('OWNER', 'ADMIN', 'MANAGER', 'MEMBER', 'VIEWER', name='accountrole')
    
    account_type_enum.create(op.get_bind())
    sub_tier_enum.create(op.get_bind())
    account_role_enum.create(op.get_bind())

    # 2. Create Accounts Table
    op.create_table(
        'accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', account_type_enum, server_default='CONSUMER', nullable=False),
        sa.Column('tax_number', sa.String(length=50), nullable=True),
        sa.Column('tax_country', sa.String(length=3), nullable=True),
        sa.Column('billing_address_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('subscription_tier', sub_tier_enum, server_default='FREE', nullable=False),
        sa.Column('subscription_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.String(length=20), server_default='active', nullable=False),
        sa.Column('is_verified', sa.String(length=20), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )

    # 3. Create Account Members Table (The Missing Junction Table)
    op.create_table(
        'account_members',
        sa.Column('account_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('accounts.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('role', account_role_enum, server_default='MEMBER', nullable=False),
        sa.Column('permissions', postgresql.JSONB, nullable=True),
        sa.Column('invited_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )

    # 4. Indexes
    op.create_index('ix_accounts_name', 'accounts', ['name'])
    op.create_index('idx_account_type_active', 'accounts', ['type', 'is_active'])
    op.create_index('idx_account_member_role', 'account_members', ['account_id', 'role'])

    #5. Update At Trigger
    op.execute("""
        CREATE TRIGGER update_accounts_updated_at 
        BEFORE UPDATE ON accounts
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

def downgrade() -> None:
    # 1. Remove Triggers
    op.execute("DROP TRIGGER IF EXISTS update_accounts_updated_at ON accounts")

    # 2. Drop Tables (Drop children first to avoid FK constraints)
    op.drop_table('account_members')
    op.drop_table('accounts')

    # 3. Drop Custom Enum Types
    # Note: Using checkfirst=True prevents errors if types were already removed
    sa.Enum(name='accountrole').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='subscriptiontier').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='accounttype').drop(op.get_bind(), checkfirst=True)