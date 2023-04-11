"""initial

Revision ID: e10c2de9e02a
Revises: 
Create Date: 2023-03-17 16:39:34.750781

"""
import uuid
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e10c2de9e02a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'person',
        sa.Column('id', sa.UUID(as_uuid=True), default=uuid.uuid4, primary_key=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                  default=sa.func.timezone('UTC', sa.func.current_timestamp()), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True),
                  default=sa.func.timezone('UTC', sa.func.current_timestamp()),
                  onupdate=sa.func.timezone('UTC', sa.func.current_timestamp()), nullable=False),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('email', sa.String(50), nullable=False, unique=True),
        sa.Column('password', sa.String(256), nullable=False),
        sa.Column('password_updated_at', sa.TIMESTAMP(timezone=True),
                  default=sa.func.timezone('UTC', sa.func.current_timestamp()), nullable=False),
    )
    op.create_table(
        'post',
        sa.Column('id', sa.UUID(as_uuid=True), default=uuid.uuid4, primary_key=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                  default=sa.func.timezone('UTC', sa.func.current_timestamp()), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True),
                  default=sa.func.timezone('UTC', sa.func.current_timestamp()),
                  onupdate=sa.func.timezone('UTC', sa.func.current_timestamp()), nullable=False),
        sa.Column('person', sa.UUID, sa.ForeignKey('person.id'), nullable=False),
        sa.Column('text', sa.String(1000), nullable=False)
    )
    op.create_table(
        'post_comment',
        sa.Column('id', sa.UUID(as_uuid=True), default=uuid.uuid4, primary_key=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True),
                  default=sa.func.timezone('UTC', sa.func.current_timestamp()), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True),
                  default=sa.func.timezone('UTC', sa.func.current_timestamp()),
                  onupdate=sa.func.timezone('UTC', sa.func.current_timestamp()), nullable=False),
        sa.Column('post', sa.UUID, sa.ForeignKey('post.id'), nullable=False),
        sa.Column('person', sa.UUID, sa.ForeignKey('person.id'), nullable=False),
        sa.Column('text', sa.String(250), nullable=False)
    )


def downgrade() -> None:
    op.drop_table('post_comment')
    op.drop_table('post')
    op.drop_table('person')
