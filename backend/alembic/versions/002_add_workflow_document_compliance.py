"""Add workflow, document, and compliance tables

Revision ID: 002_workflow_docs_comp
Revises: 001_initial
Create Date: 2025-01-XX

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_workflow_docs_comp'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create workflows table
    op.create_table(
        'workflows',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='Draft'),
        sa.Column('plant_id', sa.Integer(), sa.ForeignKey('plants.id'), nullable=True),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True)),
        sa.Column('due_date', sa.DateTime(timezone=True)),
        sa.Column('completed_date', sa.DateTime(timezone=True)),
        sa.Column('progress_percentage', sa.Integer(), default=0),
        sa.Column('current_phase', sa.String(200)),
        sa.Column('workflow_data', sa.JSON(), default={}),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('created_by', sa.Integer()),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', sa.Integer()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
    )
    
    # Create workflow_phases table
    op.create_table(
        'workflow_phases',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('workflow_id', sa.Integer(), sa.ForeignKey('workflows.id'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('due_date', sa.DateTime(timezone=True)),
        sa.Column('completed_date', sa.DateTime(timezone=True)),
        sa.Column('phase_data', sa.JSON(), default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('created_by', sa.Integer()),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', sa.Integer()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
    )
    
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), default='Draft'),
        sa.Column('file_name', sa.String(500), nullable=False),
        sa.Column('file_path', sa.String(1000), nullable=False),
        sa.Column('file_size', sa.Integer()),
        sa.Column('mime_type', sa.String(100)),
        sa.Column('plant_id', sa.Integer(), sa.ForeignKey('plants.id'), nullable=True),
        sa.Column('issue_date', sa.DateTime(timezone=True)),
        sa.Column('expiry_date', sa.DateTime(timezone=True)),
        sa.Column('upload_date', sa.DateTime(timezone=True)),
        sa.Column('metadata', sa.JSON(), default={}),
        sa.Column('tags', sa.JSON(), default=[]),
        sa.Column('version', sa.Integer(), default=1),
        sa.Column('parent_document_id', sa.Integer(), sa.ForeignKey('documents.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('created_by', sa.Integer()),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', sa.Integer()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
    )
    
    # Create compliance_requirements table
    op.create_table(
        'compliance_requirements',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('frequency_days', sa.Integer()),
        sa.Column('due_date_offset', sa.Integer(), default=0),
        sa.Column('authority', sa.String(100)),
        sa.Column('portal_name', sa.String(100)),
        sa.Column('plant_id', sa.Integer(), sa.ForeignKey('plants.id'), nullable=True),
        sa.Column('requirement_data', sa.JSON(), default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('created_by', sa.Integer()),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', sa.Integer()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
    )
    
    # Create compliance_records table
    op.create_table(
        'compliance_records',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('requirement_id', sa.Integer(), sa.ForeignKey('compliance_requirements.id'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='Pending'),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_date', sa.DateTime(timezone=True)),
        sa.Column('submitted_date', sa.DateTime(timezone=True)),
        sa.Column('penalty_amount', sa.Float(), default=0.0),
        sa.Column('penalty_applied', sa.Boolean(), default=False),
        sa.Column('notes', sa.Text()),
        sa.Column('record_data', sa.JSON(), default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('created_by', sa.Integer()),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', sa.Integer()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
    )
    
    # Create asset_maintenance table
    op.create_table(
        'asset_maintenance',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('asset_id', sa.Integer(), sa.ForeignKey('assets.id'), nullable=False),
        sa.Column('maintenance_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('performed_by', sa.String(200)),
        sa.Column('scheduled_date', sa.DateTime(timezone=True)),
        sa.Column('performed_date', sa.DateTime(timezone=True)),
        sa.Column('next_maintenance_date', sa.DateTime(timezone=True)),
        sa.Column('status', sa.String(50), default='planned'),
        sa.Column('findings', sa.Text()),
        sa.Column('actions_taken', sa.Text()),
        sa.Column('cost', sa.Float()),
        sa.Column('documents', sa.JSON(), default=[]),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('created_by', sa.Integer()),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', sa.Integer()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
    )
    
    # Create cer_participation_requests table
    op.create_table(
        'cer_participation_requests',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.String(50), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('cer_id', sa.Integer(), sa.ForeignKey('cer_configuration.id'), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),
        sa.Column('request_date', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('processed_date', sa.DateTime(timezone=True)),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
        sa.Column('created_by', sa.Integer()),
        sa.Column('updated_by', sa.Integer()),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_by', sa.Integer()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
    )
    
    # Create indexes
    op.create_index('idx_workflows_plant', 'workflows', ['plant_id'])
    op.create_index('idx_workflows_tenant', 'workflows', ['tenant_id'])
    op.create_index('idx_documents_plant', 'documents', ['plant_id'])
    op.create_index('idx_documents_tenant', 'documents', ['tenant_id'])
    op.create_index('idx_compliance_plant', 'compliance_requirements', ['plant_id'])
    op.create_index('idx_compliance_tenant', 'compliance_requirements', ['tenant_id'])


def downgrade() -> None:
    op.drop_index('idx_compliance_tenant', 'compliance_requirements')
    op.drop_index('idx_compliance_plant', 'compliance_requirements')
    op.drop_index('idx_documents_tenant', 'documents')
    op.drop_index('idx_documents_plant', 'documents')
    op.drop_index('idx_workflows_tenant', 'workflows')
    op.drop_index('idx_workflows_plant', 'workflows')
    
    op.drop_table('cer_participation_requests')
    op.drop_table('asset_maintenance')
    op.drop_table('compliance_records')
    op.drop_table('compliance_requirements')
    op.drop_table('documents')
    op.drop_table('workflow_phases')
    op.drop_table('workflows')

