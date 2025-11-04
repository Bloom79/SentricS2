"""Add CER member assets and plant linking

Revision ID: 006
Revises: 005
Create Date: 2025-01-31
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add plant_id to cer_members for member-plant linking
    op.add_column('cer_members', sa.Column('plant_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_cer_members_plant_id',
        'cer_members', 'plants',
        ['plant_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_cer_members_plant_id', 'cer_members', ['plant_id'])
    
    # Create cer_member_assets table
    op.create_table(
        'cer_member_assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('asset_type', sa.String(length=50), nullable=False),
        sa.Column('member_id', sa.Integer(), nullable=False),
        sa.Column('cer_id', sa.Integer(), nullable=False),
        sa.Column('capacity', sa.Float(), nullable=False),
        sa.Column('installation_date', sa.Date(), nullable=False),
        sa.Column('gse_registration_id', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('asset_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('deleted_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['cer_id'], ['cer_configuration.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['member_id'], ['cer_members.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_cer_member_assets_member_id', 'cer_member_assets', ['member_id'])
    op.create_index('ix_cer_member_assets_cer_id', 'cer_member_assets', ['cer_id'])
    op.create_index('ix_cer_member_assets_tenant_id', 'cer_member_assets', ['tenant_id'])


def downgrade() -> None:
    # Drop cer_member_assets table
    op.drop_index('ix_cer_member_assets_tenant_id', table_name='cer_member_assets')
    op.drop_index('ix_cer_member_assets_cer_id', table_name='cer_member_assets')
    op.drop_index('ix_cer_member_assets_member_id', table_name='cer_member_assets')
    op.drop_table('cer_member_assets')
    
    # Remove plant_id from cer_members
    op.drop_index('ix_cer_members_plant_id', table_name='cer_members')
    op.drop_constraint('fk_cer_members_plant_id', 'cer_members', type_='foreignkey')
    op.drop_column('cer_members', 'plant_id')

