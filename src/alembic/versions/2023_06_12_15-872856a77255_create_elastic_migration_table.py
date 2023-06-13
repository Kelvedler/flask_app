"""create_elastic_migration_table

Revision ID: 872856a77255
Revises: 1e7f51bc0835
Create Date: 2023-06-12 15:02:19.403041

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '872856a77255'
down_revision = '1e7f51bc0835'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'elastic_version',
        sa.Column('version_num', sa.String(50))
    )


def downgrade() -> None:
    op.drop_table('elastic_version')
