"""util_function_udpate_updated_at_col

Revision ID: e56c093e3b42
Revises: 615e2934f431
Create Date: 2026-02-15 13:03:46.602382

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e56c093e3b42'
down_revision: Union[str, Sequence[str], None] = '615e2934f431'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Define the shared function once for the entire database
        TRIGGER to return now()
    """
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
