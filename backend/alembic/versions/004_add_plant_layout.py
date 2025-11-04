"""Add Plant Layout model for Visual Designer

Revision ID: 004_add_plant_layout
Revises: 003_add_sites
Create Date: 2025-01-XX

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004_add_plant_layout'
down_revision: Union[str, None] = '003_add_sites'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    # Create plant_layouts table
    op.create_table(
        'plant_layouts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('plant_id', sa.Integer(), nullable=False, unique=True, index=True),
        sa.Column('nodes', sa.JSON(), nullable=False, default=[]),
        sa.Column('edges', sa.JSON(), nullable=False, default=[]),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['plant_id'], ['plants.id']),
        sa.PrimaryKeyConstraint('id')
    )



def downgrade() -> None:
    op.drop_table('plant_layouts')

