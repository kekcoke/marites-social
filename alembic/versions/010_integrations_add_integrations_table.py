"""add integrations table

Revision ID: 010_integrations
Revises: 009_orders
Create Date: 2026-02-16 00:06:55.629307

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '010_integrations'
down_revision: Union[str, Sequence[str], None] = '009_orders'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ========== CREATE REFERENCE TABLES ==========
    
    # Integration types table
    op.create_table(
        'integration_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255)),
        sa.Column('icon', sa.String(50)),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('sort_order', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_integration_types_code', 'integration_types', ['code'], unique=True)

    # Integration providers table
    op.create_table(
        'integration_providers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255)),
        sa.Column('website', sa.String(255)),
        sa.Column('docs_url', sa.String(255)),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('sort_order', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_integration_providers_code', 'integration_providers', ['code'], unique=True)

    # ========== INSERT REFERENCE DATA ==========
    
    # Insert integration types
    op.bulk_insert(
        sa.table('integration_types',
            sa.column('code', sa.String),
            sa.column('name', sa.String),
            sa.column('description', sa.String),
            sa.column('icon', sa.String),
            sa.column('sort_order', sa.Integer)
        ),
        [
            {'code': 'PAYMENT', 'name': 'Payment', 'description': 'Payment processing integrations', 'icon': 'credit-card', 'sort_order': 10},
            {'code': 'EMAIL', 'name': 'Email', 'description': 'Email service integrations', 'icon': 'mail', 'sort_order': 20},
            {'code': 'SMS', 'name': 'SMS', 'description': 'SMS service integrations', 'icon': 'message-square', 'sort_order': 30},
            {'code': 'CALENDAR', 'name': 'Calendar', 'description': 'Calendar integrations', 'icon': 'calendar', 'sort_order': 40},
            {'code': 'VIDEO', 'name': 'Video', 'description': 'Video conferencing integrations', 'icon': 'video', 'sort_order': 50},
            {'code': 'ANALYTICS', 'name': 'Analytics', 'description': 'Analytics and tracking', 'icon': 'bar-chart', 'sort_order': 60},
            {'code': 'SOCIAL', 'name': 'Social Media', 'description': 'Social media integrations', 'icon': 'share-2', 'sort_order': 70},
            {'code': 'CRM', 'name': 'CRM', 'description': 'Customer relationship management', 'icon': 'users', 'sort_order': 80},
            {'code': 'TICKETING', 'name': 'Ticketing', 'description': 'Ticketing system integrations', 'icon': 'ticket', 'sort_order': 90},
            {'code': 'STREAMING', 'name': 'Streaming', 'description': 'Live streaming integrations', 'icon': 'radio', 'sort_order': 100},
            {'code': 'STORAGE', 'name': 'Storage', 'description': 'Cloud storage integrations', 'icon': 'cloud', 'sort_order': 110},
            {'code': 'MARKETING', 'name': 'Marketing', 'description': 'Marketing tool integrations', 'icon': 'trending-up', 'sort_order': 120},
        ]
    )

    # Insert common providers
    op.bulk_insert(
        sa.table('integration_providers',
            sa.column('code', sa.String),
            sa.column('name', sa.String),
            sa.column('description', sa.String),
            sa.column('website', sa.String),
            sa.column('docs_url', sa.String),
            sa.column('sort_order', sa.Integer)
        ),
        [
            {'code': 'STRIPE', 'name': 'Stripe', 'description': 'Stripe payment processing', 'website': 'https://stripe.com', 'docs_url': 'https://stripe.com/docs', 'sort_order': 10},
            {'code': 'PAYPAL', 'name': 'PayPal', 'description': 'PayPal payments', 'website': 'https://paypal.com', 'docs_url': 'https://developer.paypal.com', 'sort_order': 20},
            {'code': 'SENDGRID', 'name': 'SendGrid', 'description': 'Email delivery service', 'website': 'https://sendgrid.com', 'docs_url': 'https://docs.sendgrid.com', 'sort_order': 30},
            {'code': 'TWILIO', 'name': 'Twilio', 'description': 'SMS and communication', 'website': 'https://twilio.com', 'docs_url': 'https://twilio.com/docs', 'sort_order': 40},
            {'code': 'ZOOM', 'name': 'Zoom', 'description': 'Video conferencing', 'website': 'https://zoom.us', 'docs_url': 'https://marketplace.zoom.us/docs', 'sort_order': 50},
            {'code': 'GOOGLE', 'name': 'Google', 'description': 'Google services', 'website': 'https://google.com', 'docs_url': 'https://developers.google.com', 'sort_order': 60},
            {'code': 'MICROSOFT', 'name': 'Microsoft', 'description': 'Microsoft services', 'website': 'https://microsoft.com', 'docs_url': 'https://docs.microsoft.com', 'sort_order': 70},
        ]
    )

    # ========== CREATE INTEGRATIONS TABLE ==========
    op.create_table(
        'integrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        
        # Foreign keys
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Reference table foreign keys
        sa.Column('integration_type_id', sa.Integer(), nullable=False),
        sa.Column('integration_provider_id', sa.Integer(), nullable=False),
        
        # Integration details
        sa.Column('name', sa.String(length=100), nullable=False),
        
        # Configuration (should be encrypted in production)
        sa.Column('config', postgresql.JSONB(), nullable=True),
        
        # OAuth tokens (should be encrypted in production)
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        
        # Webhook configuration
        sa.Column('webhook_url', sa.String(length=500), nullable=True),
        sa.Column('webhook_secret', sa.String(length=255), nullable=True),
        
        # Status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_configured', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        
        # Error tracking
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('last_error_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_count', sa.Integer(), server_default='0', nullable=False),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        # Foreign key constraints
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['integration_type_id'], ['integration_types.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['integration_provider_id'], ['integration_providers.id'], ondelete='RESTRICT'),
    )
    
    # ========== CREATE INDEXES ==========
    op.create_index('ix_integrations_account_id', 'integrations', ['account_id'])
    op.create_index('ix_integrations_type_id', 'integrations', ['integration_type_id'])
    op.create_index('ix_integrations_provider_id', 'integrations', ['integration_provider_id'])
    op.create_index('ix_integrations_account_type', 'integrations', ['account_id', 'integration_type_id'])
    op.create_index('ix_integrations_provider_active', 'integrations', ['integration_provider_id', 'is_active'])
    
    # ========== CREATE TRIGGERS ==========
    op.execute("""
        CREATE TRIGGER update_integrations_updated_at 
        BEFORE UPDATE ON integrations
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)
    
    op.execute("""
        CREATE TRIGGER update_integration_types_updated_at 
        BEFORE UPDATE ON integration_types
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)
    
    op.execute("""
        CREATE TRIGGER update_integration_providers_updated_at 
        BEFORE UPDATE ON integration_providers
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)
    
    # ========== ADD SECURITY COMMENTS ==========
    op.execute("""
        COMMENT ON COLUMN integrations.config IS 
        'SECURITY: Must be encrypted at rest in production using application-level encryption';
    """)
    
    op.execute("""
        COMMENT ON COLUMN integrations.access_token IS 
        'SECURITY: Must be encrypted at rest in production using application-level encryption';
    """)
    
    op.execute("""
        COMMENT ON COLUMN integrations.refresh_token IS 
        'SECURITY: Must be encrypted at rest in production using application-level encryption';
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS update_integrations_updated_at ON integrations")
    op.execute("DROP TRIGGER IF EXISTS update_integration_types_updated_at ON integration_types")
    op.execute("DROP TRIGGER IF EXISTS update_integration_providers_updated_at ON integration_providers")
    
    # Drop tables in reverse order
    op.drop_table('integrations')
    op.drop_table('integration_providers')
    op.drop_table('integration_types')
    
    # Drop any remaining enum types if they exist
    enum_types = ['integrationtype']
    for enum_name in enum_types:
        op.execute(f"DROP TYPE IF EXISTS {enum_name} CASCADE")