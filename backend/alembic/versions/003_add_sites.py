"""Add Sites model and relationships

Revision ID: 002_add_sites
Revises: 001_initial
Create Date: 2025-01-XX

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_add_sites'
down_revision: Union[str, None] = '002_workflow_docs_comp'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    # Create sites table
    op.create_table(
        'sites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('name', sa.String(200), nullable=False, index=True),
        sa.Column('code', sa.String(50), nullable=True, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('site_type', sa.String(50), nullable=False, default='industrial', index=True),
        sa.Column('status', sa.String(50), nullable=False, default='active', index=True),
        sa.Column('operational_status', sa.String(50), nullable=True),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('address', sa.String(500), nullable=True),
        sa.Column('street_address', sa.String(500), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('postal_code', sa.String(20), nullable=True),
        sa.Column('province', sa.String(10), nullable=True),
        sa.Column('region', sa.String(50), nullable=True, index=True),
        sa.Column('country', sa.String(100), nullable=True, default='Italy'),
        sa.Column('latitude', sa.Numeric(10, 8), nullable=True),
        sa.Column('longitude', sa.Numeric(11, 8), nullable=True),
        sa.Column('capacity', sa.Float(), nullable=True, default=0.0),
        sa.Column('efficiency', sa.Float(), nullable=True, default=0.0),
        sa.Column('available_area', sa.Float(), nullable=True),
        sa.Column('reserved_area', sa.Float(), nullable=True),
        sa.Column('commissioning_date', sa.DateTime(), nullable=True),
        sa.Column('decommissioning_date', sa.DateTime(), nullable=True),
        sa.Column('owner', sa.String(200), nullable=True),
        sa.Column('operator', sa.String(200), nullable=True),
        sa.Column('maintenance_provider', sa.String(200), nullable=True),
        sa.Column('environmental_impact_rating', sa.Integer(), nullable=True),
        sa.Column('grid_connection_status', sa.String(50), nullable=True, default='connected'),
        sa.Column('grid_capacity', sa.Float(), nullable=True),
        sa.Column('tags', sa.JSON(), default=[]),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create storage_units table
    op.create_table(
        'storage_units',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('site_id', sa.Integer(), nullable=False, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('code', sa.String(50), nullable=True),
        sa.Column('capacity_kwh', sa.Float(), nullable=False),
        sa.Column('rated_power_kw', sa.Float(), nullable=False),
        sa.Column('chemistry_type', sa.String(50), nullable=True),
        sa.Column('efficiency', sa.Float(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='operational'),
        sa.Column('state_of_charge', sa.Float(), nullable=True),
        sa.Column('state_of_health', sa.Float(), nullable=True),
        sa.Column('total_cycles', sa.Integer(), nullable=True, default=0),
        sa.Column('cycle_life', sa.Integer(), nullable=True),
        sa.Column('manufacturer', sa.String(200), nullable=True),
        sa.Column('model', sa.String(200), nullable=True),
        sa.Column('installation_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create consumers table
    op.create_table(
        'consumers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('site_id', sa.Integer(), nullable=False, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('code', sa.String(50), nullable=True),
        sa.Column('consumer_type', sa.String(50), nullable=False),
        sa.Column('average_consumption_kw', sa.Float(), nullable=True),
        sa.Column('peak_consumption_kw', sa.Float(), nullable=True),
        sa.Column('pod_id', sa.String(100), nullable=True, index=True),
        sa.Column('smart_meter_id', sa.String(100), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='active'),
        sa.Column('activation_date', sa.DateTime(), nullable=True),
        sa.Column('address', sa.String(500), nullable=True),
        sa.Column('latitude', sa.Numeric(10, 8), nullable=True),
        sa.Column('longitude', sa.Numeric(11, 8), nullable=True),
        sa.Column('load_profile', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create energy_flows table
    op.create_table(
        'energy_flows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('site_id', sa.Integer(), nullable=True, index=True),
        sa.Column('plant_id', sa.Integer(), nullable=True, index=True),
        sa.Column('nodes', sa.JSON(), nullable=False),
        sa.Column('edges', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True, index=True),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id']),
        sa.ForeignKeyConstraint(['plant_id'], ['plants.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Add site_id to plants table
    op.add_column('plants', sa.Column('site_id', sa.Integer(), nullable=True, index=True))
    op.create_foreign_key('fk_plants_site_id', 'plants', 'sites', ['site_id'], ['id'])


def downgrade() -> None:
    # Remove site_id from plants
    op.drop_constraint('fk_plants_site_id', 'plants', type_='foreignkey')
    op.drop_column('plants', 'site_id')

    # Drop energy_flows table
    op.drop_table('energy_flows')

    # Drop consumers table
    op.drop_table('consumers')

    # Drop storage_units table
    op.drop_table('storage_units')

    # Drop sites table
    op.drop_table('sites')

