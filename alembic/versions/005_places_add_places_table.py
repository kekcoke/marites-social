"""add places table

Revision ID: 005_places
Revises: e0d01e1211da
Create Date: 2026-02-15 17:18:37.943023

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_places'
down_revision: Union[str, Sequence[str], None] = 'e0d01e1211da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable PostGIS extension (requires superuser privileges)
    # This should be done manually or via a separate migration if needed
    # op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    
    # Create places table
    op.create_table(
        'places',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Geographic data
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('geo_continent', sa.String(length=50), nullable=True),
        sa.Column('country_abbreviation', sa.String(length=2), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=False),
        
        # Media URLs
        sa.Column('icon_desktop_url', sa.String(length=500), nullable=True),
        sa.Column('icon_mobile_url', sa.String(length=500), nullable=True),
        sa.Column('icon_square_url', sa.String(length=500), nullable=True),
        sa.Column('social_image_url', sa.String(length=500), nullable=True),
        
        # Metadata
        sa.Column('tint_color', sa.String(length=7), nullable=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('publication_name', sa.String(length=200), nullable=True),
        
        # Status flags
        sa.Column('is_launched', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_subscriber', sa.Boolean(), nullable=False, server_default='false'),
        
        # Denormalized counts
        sa.Column('event_count', sa.Integer(), nullable=False, server_default='0'),
        
        # Featured events array
        sa.Column('featured_event_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        # Foreign keys
        sa.Column('geolocation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['geolocation_id'], ['geolocations.id'], ondelete='CASCADE'),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    
    # Create indexes for common queries

    op.create_index('ix_places_name', 'places', ['name'])
    op.create_index('ix_places_slug', 'places', ['slug'], unique=True)
    op.create_index('ix_places_country_abbreviation', 'places', ['country_abbreviation'])
    op.create_index('ix_places_geo_continent', 'places', ['geo_continent'])
    op.create_index('ix_places_is_launched', 'places', ['is_launched'])
    
    # Composite indexes
    op.create_index('idx_place_coordinates', 'places', ['latitude', 'longitude'])
    op.create_index('idx_place_country_abbreviation_continent', 'places', ['country_abbreviation', 'geo_continent'])

    # Add trigger for updated_at
    op.execute("""
        CREATE TRIGGER update_places_updated_at 
        BEFORE UPDATE ON places
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)
    
    # Optional: Add PostGIS geography column for efficient spatial queries
    # Uncomment if PostGIS is available
    # op.execute("""
    #     ALTER TABLE places 
    #     ADD COLUMN location geography(Point, 4326);
    # """)
    # 
    # op.execute("""
    #     UPDATE places 
    #     SET location = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography;
    # """)
    # 
    # op.create_index(
    #     'idx_places_location',
    #     'places',
    #     ['location'],
    #     postgresql_using='gist'
    # )


def downgrade() -> None:
    # Drop PostGIS column if it exists
    # op.execute("ALTER TABLE places DROP COLUMN IF EXISTS location")
    
    op.execute("DROP TRIGGER IF EXISTS update_places_updated_at ON places")
    
    # Drop indexes
    op.drop_index('idx_place_country_abbreviation_continent', table_name='places')
    op.drop_index('idx_place_coordinates', table_name='places')
    op.drop_index('ix_places_is_launched', table_name='places')
    op.drop_index('ix_places_geo_continent', table_name='places')
    op.drop_index('ix_places_country_abbreviation', table_name='places')
    op.drop_index('ix_places_slug', table_name='places')
    op.drop_index('ix_places_name', table_name='places')
    
    # Drop table
    op.drop_table('places')