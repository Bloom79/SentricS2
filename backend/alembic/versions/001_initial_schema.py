"""Initial consolidated schema

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-XX

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geography

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable PostGIS extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis;')
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis_topology;')
    
    # Create tenants table
    op.create_table(
        'tenants',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('plan', sa.String(50), default='free'),
        sa.Column('plan_expiry', sa.DateTime()),
        sa.Column('settings', sa.JSON(), default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('permissions', sa.JSON(), default=[]),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('email_verified', sa.Boolean(), default=False),
        sa.Column('last_access', sa.DateTime()),
        sa.Column('failed_login_attempts', sa.Integer(), default=0),
        sa.Column('locked_until', sa.DateTime()),
        sa.Column('mfa_enabled', sa.Boolean(), default=False),
        sa.Column('mfa_secret', sa.String(100)),
        sa.Column('phone', sa.String(50)),
        sa.Column('avatar_url', sa.String(500)),
        sa.Column('language', sa.String(10), default='en'),
        sa.Column('timezone', sa.String(50), default='Europe/Rome'),
        sa.Column('authorized_plants', sa.JSON(), default=[]),
        sa.Column('preferences', sa.JSON(), default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('created_by', sa.Integer()),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', sa.Integer()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
    )
    
    # Create plants table
    op.create_table(
        'plants',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('code', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('power', sa.String(50), nullable=False),
        sa.Column('power_kw', sa.Float(), nullable=False, index=True),
        sa.Column('status', sa.String(50), nullable=False, index=True),
        sa.Column('type', sa.String(50), nullable=False, index=True),
        sa.Column('location', sa.String(200), nullable=False),
        sa.Column('address', sa.String(500)),
        sa.Column('municipality', sa.String(100)),
        sa.Column('province', sa.String(10)),
        sa.Column('region', sa.String(50), index=True),
        sa.Column('latitude', sa.Float()),
        sa.Column('longitude', sa.Float()),
        sa.Column('cer_id', sa.Integer(), index=True),
        sa.Column('next_deadline', sa.DateTime(), index=True),
        sa.Column('next_deadline_type', sa.String(100)),
        sa.Column('deadline_color', sa.String(20)),
        sa.Column('gse_integration', sa.Boolean(), default=False),
        sa.Column('terna_integration', sa.Boolean(), default=False),
        sa.Column('customs_integration', sa.Boolean(), default=False),
        sa.Column('dso_integration', sa.Boolean(), default=False),
        sa.Column('tags', sa.JSON(), default=[]),
        sa.Column('notes', sa.Text()),
        sa.Column('custom_fields', sa.JSON(), default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('created_by', sa.Integer()),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', sa.Integer()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
    )
    
    # Create CER configuration table
    op.create_table(
        'cer_configuration',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('legal_type', sa.String(50), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('address', sa.String(500), nullable=False),
        sa.Column('location', Geography('POINT'), nullable=True),
        sa.Column('boundary', Geography('POLYGON'), nullable=True),
        sa.Column('region', sa.String(50), nullable=False),
        sa.Column('province', sa.String(10)),
        sa.Column('municipality', sa.String(100)),
        sa.Column('primary_substation_id', sa.String(100), nullable=False),
        sa.Column('total_capacity', sa.Float(), default=0.0),
        sa.Column('energy_source', sa.String(50)),
        sa.Column('technical_info', sa.JSON(), default={}),
        sa.Column('gse_compliance', sa.JSON(), default={}),
        sa.Column('gse_compliance_status', sa.String(50), default='pending'),
        sa.Column('simulation_settings', sa.JSON()),
        sa.Column('billing_settings', sa.JSON()),
        sa.Column('member_limits', sa.JSON(), default={}),
        sa.Column('pnrr_funding_applied', sa.Boolean(), default=False),
        sa.Column('pnrr_funding_amount', sa.Float()),
        sa.Column('pnrr_funding_status', sa.String(50)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('created_by', sa.Integer()),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', sa.Integer()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
    )
    
    # Create CER members table
    op.create_table(
        'cer_members',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('cer_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer()),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('address', sa.String(500), nullable=False),
        sa.Column('member_type', sa.String(50), nullable=False),
        sa.Column('user_type', sa.String(50), default='real'),
        sa.Column('status', sa.String(50), default='active'),
        sa.Column('pod_id', sa.String(100), unique=True, index=True),
        sa.Column('smart_meter_id', sa.String(100)),
        sa.Column('meter_type', sa.String(50)),
        sa.Column('load_profile_type', sa.String(50), nullable=False),
        sa.Column('load_profile_data', sa.JSON()),
        sa.Column('contracted_power', sa.Float()),
        sa.Column('voltage_level', sa.String(50)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('activation_date', sa.DateTime(timezone=True)),
        sa.Column('deactivation_date', sa.DateTime(timezone=True)),
        sa.Column('verification_status', sa.String(50)),
        sa.Column('technical_info', sa.JSON(), default={}),
        sa.Column('device_info', sa.JSON(), default={}),
        sa.Column('energy_sharing_preferences', sa.JSON(), default={}),
        sa.Column('fiscal_code', sa.String(50)),
        sa.Column('vat_number', sa.String(50)),
        sa.Column('billing_address', sa.String(500)),
        sa.Column('billing_preferences', sa.JSON(), default={}),
        sa.Column('energy_produced', sa.Float(), default=0.0),
        sa.Column('energy_consumed', sa.Float(), default=0.0),
        sa.Column('energy_shared', sa.Float(), default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('created_by', sa.Integer()),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', sa.Integer()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['cer_id'], ['cer_configuration.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )
    
    # Create asset types table
    op.create_table(
        'asset_types',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('normalized_name', sa.String(100), index=True),
        sa.Column('attributes', sa.JSON(), default={}),
        sa.Column('default_attributes', sa.JSON(), default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('created_by', sa.Integer()),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', sa.Integer()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
    )
    
    # Create assets table
    op.create_table(
        'assets',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('plant_id', sa.Integer(), nullable=False),
        sa.Column('type_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('model', sa.String(100)),
        sa.Column('manufacturer', sa.String(100)),
        sa.Column('serial_number', sa.String(100), unique=True, index=True),
        sa.Column('component_type', sa.String(50)),
        sa.Column('status', sa.String(50), default='operational'),
        sa.Column('location', sa.String(200)),
        sa.Column('installation_date', sa.DateTime(timezone=True)),
        sa.Column('rated_power', sa.Float()),
        sa.Column('efficiency', sa.Float()),
        sa.Column('voltage', sa.Float()),
        sa.Column('current', sa.Float()),
        sa.Column('dynamic_attributes', sa.JSON(), default={}),
        sa.Column('parent_id', sa.Integer()),
        sa.Column('notes', sa.Text()),
        sa.Column('warranty_expiry', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('created_by', sa.Integer()),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', sa.Integer()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['plant_id'], ['plants.id']),
        sa.ForeignKeyConstraint(['type_id'], ['asset_types.id']),
        sa.ForeignKeyConstraint(['parent_id'], ['assets.id']),
    )
    
    # Create indexes
    op.create_index('idx_plants_tenant', 'plants', ['tenant_id'])
    op.create_index('idx_plants_cer', 'plants', ['cer_id'])
    op.create_index('idx_cer_tenant', 'cer_configuration', ['tenant_id'])
    op.create_index('idx_assets_plant', 'assets', ['plant_id'])
    op.create_index('idx_assets_tenant', 'assets', ['tenant_id'])


def downgrade() -> None:
    op.drop_index('idx_assets_tenant', 'assets')
    op.drop_index('idx_assets_plant', 'assets')
    op.drop_index('idx_cer_tenant', 'cer_configuration')
    op.drop_index('idx_plants_cer', 'plants')
    op.drop_index('idx_plants_tenant', 'plants')
    
    op.drop_table('assets')
    op.drop_table('asset_types')
    op.drop_table('cer_members')
    op.drop_table('cer_configuration')
    op.drop_table('plants')
    op.drop_table('users')
    op.drop_table('tenants')
    
    op.execute('DROP EXTENSION IF EXISTS postgis_topology;')
    op.execute('DROP EXTENSION IF EXISTS postgis;')

