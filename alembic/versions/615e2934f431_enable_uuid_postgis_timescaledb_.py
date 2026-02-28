"""enable uuid postgis timescaledb extensions

Revision ID: 615e2934f431
Revises: 402842c97908
Create Date: 2026-02-14 22:13:52.444925

IMPORTANT: This migration should be run FIRST and requires SUPERUSER privileges.
Run this separately before running other migrations.

"""
from typing import Union, Sequence
from alembic import op
import sqlalchemy as sa

# get db name
conn = op.get_bind()
db_name = conn.execute(sa.text("SELECT current_database()")).scalar()

# revision identifiers, used by Alembic.
revision: str = '615e2934f431'
down_revision: Union[str, Sequence[str], None] = '402842c97908'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Enable required PostgreSQL extensions.
    
    NOTE: This requires SUPERUSER privileges. If you don't have superuser
    access, ask your DBA to run these commands manually:
    
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "postgis";
    CREATE EXTENSION IF NOT EXISTS "timescaledb"; (SKIP)
    """

    # Enable UUID extension
    try:
        op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        print("✓ UUID extension enabled")
    except Exception as e:
        print(f"⚠ Warning: Could not enable uuid-ossp extension: {e}")
        print("  This is optional if your app generates UUIDs in Python")
    
    # Enable PostGIS for spatial queries
    try:
        op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
        print("✓ PostGIS extension enabled")
    except Exception as e:
        print(f"⚠ Warning: Could not enable PostGIS extension: {e}")
        print("  Distance calculations will fall back to Haversine formula")
        print("  For production, PostGIS is highly recommended")
    
    # Enable TimescaleDB for time-series optimization
    # NOTE: Commented out due to underlying incompability of timescaledb binary written for 17 being used for 18.
    # try:
    #     op.execute('CREATE EXTENSION IF NOT EXISTS timescaledb')
    #     print("✓ TimescaleDB extension enabled")
    # except Exception as e:
    #     print(f"⚠ Warning: Could not enable TimescaleDB extension: {e}")
    #     print("  Time-series tables will use standard PostgreSQL")
    #     print("  For production with large datasets, TimescaleDB is recommended")
    
    # Create a comment documenting the extensions

    op.execute(f"""
        COMMENT ON DATABASE "{db_name}" IS
        'Community Platform - Extensions: uuid-ossp, postgis';
    """)


def downgrade() -> None:
    """
    Drop extensions.
    
    WARNING: This will drop all spatial indexes and hypertables!
    Make sure to backup your data before running this.
    """
    
    # Drop extensions in reverse order
    # try:
    #     op.execute('DROP EXTENSION IF EXISTS timescaledb CASCADE')
    #     print("✓ TimescaleDB extension dropped")
    # except Exception as e:
    #     print(f"⚠ Warning: {e}")
    
    try:
        op.execute('DROP EXTENSION IF EXISTS postgis CASCADE')
        print("✓ PostGIS extension dropped")
    except Exception as e:
        print(f"⚠ Warning: {e}")
    
    try:
        op.execute('DROP EXTENSION IF EXISTS "uuid-ossp" CASCADE')
        print("✓ UUID extension dropped")
    except Exception as e:
        print(f"⚠ Warning: {e}")