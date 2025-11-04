"""enhance workflow phases with Italian bureaucratic requirements

Revision ID: 007_enhance_workflow_phases
Revises: 006_add_cer_member_assets_and_plant_link
Create Date: 2025-01-31 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to workflow_phases table
    op.add_column('workflow_phases', sa.Column('required_documents', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='[]'))
    op.add_column('workflow_phases', sa.Column('official_form_fields', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='{}'))
    op.add_column('workflow_phases', sa.Column('portal_url', sa.String(length=500), nullable=True))
    op.add_column('workflow_phases', sa.Column('portal_login_url', sa.String(length=500), nullable=True))
    op.add_column('workflow_phases', sa.Column('required_credentials', sa.String(length=100), nullable=True))
    op.add_column('workflow_phases', sa.Column('submission_method', sa.String(length=100), nullable=True))
    op.add_column('workflow_phases', sa.Column('regulatory_deadline', sa.DateTime(timezone=True), nullable=True))
    op.add_column('workflow_phases', sa.Column('deadline_type', sa.String(length=50), nullable=True))
    op.add_column('workflow_phases', sa.Column('deadline_consequences', sa.Text(), nullable=True))
    op.add_column('workflow_phases', sa.Column('external_protocol_number', sa.String(length=200), nullable=True))
    op.add_column('workflow_phases', sa.Column('submission_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('workflow_phases', sa.Column('response_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('workflow_phases', sa.Column('cost_amount', sa.Float(), nullable=True))
    op.add_column('workflow_phases', sa.Column('cost_description', sa.String(length=500), nullable=True))
    op.add_column('workflow_phases', sa.Column('payment_method', sa.String(length=100), nullable=True))
    op.add_column('workflow_phases', sa.Column('payment_reference', sa.String(length=200), nullable=True))
    op.add_column('workflow_phases', sa.Column('requires_human_auth', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('workflow_phases', sa.Column('requires_physical_signature', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('workflow_phases', sa.Column('requires_site_inspection', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('workflow_phases', sa.Column('human_checkpoint_notes', sa.Text(), nullable=True))
    op.add_column('workflow_phases', sa.Column('checklist_items', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='[]'))
    op.add_column('workflow_phases', sa.Column('instructions', sa.Text(), nullable=True))
    op.add_column('workflow_phases', sa.Column('external_resources', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='[]'))
    op.add_column('workflow_phases', sa.Column('responsible_entity', sa.String(length=100), nullable=True))
    op.add_column('workflow_phases', sa.Column('practice_type', sa.String(length=200), nullable=True))
    op.add_column('workflow_phases', sa.Column('document_templates', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='[]'))
    op.add_column('workflow_phases', sa.Column('estimated_days', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('workflow_phases', 'estimated_days')
    op.drop_column('workflow_phases', 'document_templates')
    op.drop_column('workflow_phases', 'practice_type')
    op.drop_column('workflow_phases', 'responsible_entity')
    op.drop_column('workflow_phases', 'external_resources')
    op.drop_column('workflow_phases', 'instructions')
    op.drop_column('workflow_phases', 'checklist_items')
    op.drop_column('workflow_phases', 'human_checkpoint_notes')
    op.drop_column('workflow_phases', 'requires_site_inspection')
    op.drop_column('workflow_phases', 'requires_physical_signature')
    op.drop_column('workflow_phases', 'requires_human_auth')
    op.drop_column('workflow_phases', 'payment_reference')
    op.drop_column('workflow_phases', 'payment_method')
    op.drop_column('workflow_phases', 'cost_description')
    op.drop_column('workflow_phases', 'cost_amount')
    op.drop_column('workflow_phases', 'response_date')
    op.drop_column('workflow_phases', 'submission_date')
    op.drop_column('workflow_phases', 'external_protocol_number')
    op.drop_column('workflow_phases', 'deadline_consequences')
    op.drop_column('workflow_phases', 'deadline_type')
    op.drop_column('workflow_phases', 'regulatory_deadline')
    op.drop_column('workflow_phases', 'submission_method')
    op.drop_column('workflow_phases', 'required_credentials')
    op.drop_column('workflow_phases', 'portal_login_url')
    op.drop_column('workflow_phases', 'portal_url')
    op.drop_column('workflow_phases', 'official_form_fields')
    op.drop_column('workflow_phases', 'required_documents')

