"""add comments tables

Revision ID: 012_comments
Revises: 011_notifications_and_types
Create Date: 2026-02-16 14:14:43.458399

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '012_comments'
down_revision: Union[str, Sequence[str], None] = '011_notifications_and_types'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========== COMMENTS TABLE ==========
    op.create_table('comments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('commentable_type', sa.String(length=50), nullable=False),
        sa.Column('commentable_id', sa.UUID(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('parent_comment_id', sa.UUID(), nullable=True),
        sa.Column('attachments', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_edited', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        
        sa.ForeignKeyConstraint(['parent_comment_id'], ['comments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indexes
    op.create_index('ix_comments_user_id', 'comments', ['user_id'])
    op.create_index('ix_comments_commentable_type', 'comments', ['commentable_type'])
    op.create_index('ix_comments_commentable_id', 'comments', ['commentable_id'])
    op.create_index('ix_comments_parent_comment_id', 'comments', ['parent_comment_id'])
    op.create_index('ix_comments_created_at', 'comments', ['created_at'])
    op.create_index('idx_comment_commentable', 'comments', ['commentable_type', 'commentable_id', 'created_at'])
    op.create_index('idx_comment_user', 'comments', ['user_id', 'created_at'])


def downgrade() -> None:
    op.drop_table('comments')