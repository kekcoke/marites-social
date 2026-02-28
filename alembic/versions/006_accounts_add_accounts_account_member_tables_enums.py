"""add accounts, account member tables, enums

Revision ID: 006_accounts
Revises: 005_places
Create Date: 2026-02-15 17:52:59.148493

"""
import json
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
    
    # ========== CREATE REFERENCE TABLES ==========
    
    # 1. Account types table
    op.create_table(
        'account_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255)),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_account_types_code', 'account_types', ['code'], unique=True)

    # 2. Subscription tiers table
    op.create_table(
        'subscription_tiers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255)),
        sa.Column('price_monthly', sa.Numeric(10, 2)),
        sa.Column('price_yearly', sa.Numeric(10, 2)),
        sa.Column('max_users', sa.Integer()),
        sa.Column('max_storage_gb', sa.Integer()),
        sa.Column('features', postgresql.JSONB),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('sort_order', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_subscription_tiers_code', 'subscription_tiers', ['code'], unique=True)
    
    # 3. Account roles table
    op.create_table(
        'account_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255)),
        sa.Column('permissions', postgresql.JSONB),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('level', sa.Integer(), comment='Higher number = more privileges'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_account_roles_code', 'account_roles', ['code'], unique=True)

    # ========== INSERT REFERENCE DATA ==========
    
    # Insert account types
    op.bulk_insert(
        sa.table('account_types',
            sa.column('code', sa.String),
            sa.column('name', sa.String),
            sa.column('description', sa.String)
        ),
        [
            {'code': 'CONSUMER', 'name': 'Consumer', 'description': 'Individual consumer'},
            {'code': 'COMMUNITY', 'name': 'Community', 'description': 'Community organization'},
            {'code': 'NGO', 'name': 'Non-Governmental Organization', 'description': 'NGO'},
            {'code': 'ENTERPRISE', 'name': 'Enterprise', 'description': 'Business enterprise'},
            {'code': 'GOVERNMENT', 'name': 'Government', 'description': 'Government entity'},
        ]
    )
    
    # Insert subscription tiers
    op.bulk_insert(
        sa.table('subscription_tiers',
            sa.column('code', sa.String),
            sa.column('name', sa.String),
            sa.column('description', sa.String),
            sa.column('price_monthly', sa.Numeric),
            sa.column('max_users', sa.Integer),
            sa.column('max_storage_gb', sa.Integer),
            sa.column('features', postgresql.JSONB),
            sa.column('sort_order', sa.Integer)
        ),
        [
            {
                'code': 'FREE', 
                'name': 'Free', 
                'description': 'Basic free tier',
                'price_monthly': 0,
                'max_users': 1,
                'max_storage_gb': 5,
                'features': json.dumps({'basic_support': True, 'api_access': False}),
                'sort_order': 1
            },
            {
                'code': 'PRO', 
                'name': 'Professional', 
                'description': 'Professional tier',
                'price_monthly': 29.99,
                'max_users': 10,
                'max_storage_gb': 100,
                'features': json.dumps({'priority_support': True, 'api_access': True, 'analytics': True}),
                'sort_order': 2
            },
            {
                'code': 'BUSINESS', 
                'name': 'Business', 
                'description': 'Business tier',
                'price_monthly': 99.99,
                'max_users': 999999,
                'max_storage_gb': 1000,
                'features': json.dumps({'priority_support': True, 'api_access': True, 'analytics': True, 'custom_domain': True}),
                'sort_order': 3
            },
        ]
    )

    # Insert account roles
    op.bulk_insert(
        sa.table('account_roles',
            sa.column('code', sa.String),
            sa.column('name', sa.String),
            sa.column('description', sa.String),
            sa.column('permissions', postgresql.JSONB),
            sa.column('level', sa.Integer)
        ),
        [
            {
                'code': 'OWNER', 
                'name': 'Owner', 
                'description': 'Full account ownership',
                'permissions': json.dumps({'manage_users': True, 'manage_billing': True, 'delete_account': True, 'all': True}),
                'level': 100
            },
            {
                'code': 'ADMIN', 
                'name': 'Administrator', 
                'description': 'Administrative access',
                'permissions': json.dumps({'manage_users': True, 'manage_settings': True, 'view_billing': True}),
                'level': 80
            },
            {
                'code': 'MANAGER', 
                'name': 'Manager', 
                'description': 'Management access',
                'permissions': json.dumps({'manage_users': True, 'view_reports': True}),
                'level': 60
            },
            {
                'code': 'MEMBER', 
                'name': 'Member', 
                'description': 'Standard member',
                'permissions': json.dumps({'view_content': True, 'create_content': True}),
                'level': 40
            },
            {
                'code': 'VIEWER', 
                'name': 'Viewer', 
                'description': 'Read-only access',
                'permissions': json.dumps({'view_content': True}),
                'level': 20
            },
        ]
    )
    
    # ========== CREATE ACCOUNTS TABLE WITH FK REFERENCES ==========
    op.create_table(
        'accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Foreign key columns (replacing enum strings)
        sa.Column('account_type_id', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('subscription_tier_id', sa.Integer(), nullable=False, server_default='1'),
        
        sa.Column('tax_number', sa.String(length=50), nullable=True),
        sa.Column('tax_country', sa.String(length=3), nullable=True),
        # sa.Column('billing_address_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('subscription_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        
        # Foreign key constraints
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['account_type_id'], ['account_types.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['subscription_tier_id'], ['subscription_tiers.id'], ondelete='RESTRICT'),
        # sa.ForeignKeyConstraint(['billing_address_id'], ['addresses.id'], ondelete='SET NULL'),
    )

    # ========== CREATE ACCOUNT MEMBERS TABLE ==========
    op.create_table(
        'account_members',
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False, server_default='4'),  # Default to MEMBER
        sa.Column('permissions', postgresql.JSONB, nullable=True),
        sa.Column('invited_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        
        # Foreign key constraints
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['account_roles.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['invited_by'], ['users.id'], ondelete='SET NULL'),
        
        sa.PrimaryKeyConstraint('account_id', 'user_id')
    )

    # ========== CREATE INDEXES ==========
    op.create_index('ix_accounts_user_id', 'accounts', ['user_id'])
    op.create_index('ix_accounts_account_type_id', 'accounts', ['account_type_id'])
    op.create_index('ix_accounts_subscription_tier_id', 'accounts', ['subscription_tier_id'])
    op.create_index('ix_accounts_name', 'accounts', ['name'])
    op.create_index('ix_accounts_is_active', 'accounts', ['is_active'])
    
    op.create_index('ix_account_members_account_id', 'account_members', ['account_id'])
    op.create_index('ix_account_members_user_id', 'account_members', ['user_id'])
    op.create_index('ix_account_members_role_id', 'account_members', ['role_id'])
    op.create_index('ix_account_members_composite', 'account_members', ['account_id', 'user_id', 'role_id'])

    # ========== CREATE UPDATED AT TRIGGER ==========
    op.execute("""
        CREATE TRIGGER update_accounts_updated_at 
        BEFORE UPDATE ON accounts
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)
    
    op.execute("""
        CREATE TRIGGER update_account_types_updated_at 
        BEFORE UPDATE ON account_types
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)
    
    op.execute("""
        CREATE TRIGGER update_subscription_tiers_updated_at 
        BEFORE UPDATE ON subscription_tiers
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)
    
    op.execute("""
        CREATE TRIGGER update_account_roles_updated_at 
        BEFORE UPDATE ON account_roles
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS update_accounts_updated_at ON accounts")
    op.execute("DROP TRIGGER IF EXISTS update_account_types_updated_at ON account_types")
    op.execute("DROP TRIGGER IF EXISTS update_subscription_tiers_updated_at ON subscription_tiers")
    op.execute("DROP TRIGGER IF EXISTS update_account_roles_updated_at ON account_roles")
    
    # Drop tables in reverse order
    op.drop_table('account_members')
    op.drop_table('accounts')
    op.drop_table('account_roles')
    op.drop_table('subscription_tiers')
    op.drop_table('account_types')
    
    # Drop any remaining enum types if they exist (from previous migrations)
    enum_types = ['accounttype', 'subscriptiontier', 'accountrole']
    for enum_name in enum_types:
        op.execute(f"DROP TYPE IF EXISTS {enum_name} CASCADE")