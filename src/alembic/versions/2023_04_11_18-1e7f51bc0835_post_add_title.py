"""post_add_title

Revision ID: 1e7f51bc0835
Revises: e10c2de9e02a
Create Date: 2023-04-11 18:44:41.390742

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e7f51bc0835'
down_revision = 'e10c2de9e02a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('post', sa.Column('title', sa.String(150), nullable=False, server_default='title'))
    op.alter_column('post', 'title', server_default=None)


def downgrade() -> None:
    op.drop_column('post', 'title')
