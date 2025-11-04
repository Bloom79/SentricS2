"""Add billing tables for CER financial management

Revision ID: 005_add_billing_tables
Revises: 004_add_plant_layout
Create Date: 2025-10-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004_add_plant_layout"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()

    # Settlements table (must be created before statements referencing it)
    # Note: Using VARCHAR for enum columns - SQLAlchemy will create enum types automatically
    op.create_table(
        "settlements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("cer_id", sa.Integer(), sa.ForeignKey("cer_configuration.id"), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("settlement_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("total_production", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_consumption", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_shared_energy", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_self_consumed", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_grid_export", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_grid_import", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_incentivized_energy", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_incentives", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_grid_fees", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_community_fund", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_energy_cost", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_amount", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("incentive_rate", sa.Float(), nullable=True),
        sa.Column("member_allocation", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column("calculation_data", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column("calculation_method", sa.String(length=50), nullable=False, server_default=sa.text("'standard'")),
        sa.Column("validated_by", sa.Integer(), nullable=True),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    op.create_index("ix_settlements_tenant_id", "settlements", ["tenant_id"])
    op.create_index("idx_settlements_cer_period", "settlements", ["cer_id", "period_start", "period_end"])
    op.create_index("idx_settlements_status_date", "settlements", ["status", "settlement_date"])

    # Billing statements
    op.create_table(
        "billing_statements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("cer_id", sa.Integer(), sa.ForeignKey("cer_configuration.id"), nullable=False),
        sa.Column("member_id", sa.Integer(), sa.ForeignKey("cer_members.id"), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("billing_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("energy_shared", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("energy_consumed", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("energy_produced", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_amount", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("incentives", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("grid_fees", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("community_fund", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("energy_cost", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("shared_energy_value", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("amount_paid", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("balance", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("settlement_id", sa.Integer(), sa.ForeignKey("settlements.id"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("extra_metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True),
    )

    op.create_index("ix_billing_statements_tenant_id", "billing_statements", ["tenant_id"])
    op.create_index("idx_billing_statements_cer_period", "billing_statements", ["cer_id", "period_start", "period_end"])
    op.create_index("idx_billing_statements_member_period", "billing_statements", ["member_id", "period_start", "period_end"])
    op.create_index("idx_billing_statements_status_due_date", "billing_statements", ["status", "due_date"])

    # Invoices
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("statement_id", sa.Integer(), sa.ForeignKey("billing_statements.id"), nullable=False, unique=True),
        sa.Column("cer_id", sa.Integer(), sa.ForeignKey("cer_configuration.id"), nullable=False),
        sa.Column("member_id", sa.Integer(), sa.ForeignKey("cer_members.id"), nullable=False),
        sa.Column("invoice_number", sa.String(length=100), nullable=False),
        sa.Column("invoice_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("subtotal", sa.Float(), nullable=False),
        sa.Column("tax_amount", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("amount_paid", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("balance", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("is_paid", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("paid_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("line_items", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb"), nullable=True),
        sa.Column("payment_method", sa.String(length=50), nullable=True),
        sa.Column("payment_reference", sa.String(length=200), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("extra_metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.UniqueConstraint("invoice_number", name="uq_invoices_invoice_number"),
    )

    op.create_index("ix_invoices_tenant_id", "invoices", ["tenant_id"])
    op.create_index("ix_invoices_cer_id", "invoices", ["cer_id"])
    op.create_index("ix_invoices_member_id", "invoices", ["member_id"])

    # Billing transactions
    op.create_table(
        "billing_transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("cer_id", sa.Integer(), sa.ForeignKey("cer_configuration.id"), nullable=False),
        sa.Column("member_id", sa.Integer(), sa.ForeignKey("cer_members.id"), nullable=False),
        sa.Column("statement_id", sa.Integer(), sa.ForeignKey("billing_statements.id"), nullable=True),
        sa.Column("invoice_id", sa.Integer(), sa.ForeignKey("invoices.id"), nullable=True),
        sa.Column("transaction_type", sa.String(length=50), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default=sa.text("'EUR'")),
        sa.Column("payment_method", sa.String(length=50), nullable=True),
        sa.Column("payment_reference", sa.String(length=200), nullable=True),
        sa.Column("payment_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("extra_metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=True),
    )

    op.create_index("ix_billing_transactions_tenant_id", "billing_transactions", ["tenant_id"])
    op.create_index("idx_billing_transactions_member_date", "billing_transactions", ["member_id", "created_at"])
    op.create_index("idx_billing_transactions_cer_date", "billing_transactions", ["cer_id", "created_at"])
    op.create_index("idx_billing_transactions_status_date", "billing_transactions", ["status", "created_at"])


def downgrade() -> None:
    bind = op.get_bind()

    op.drop_index("idx_billing_transactions_status_date", table_name="billing_transactions")
    op.drop_index("idx_billing_transactions_cer_date", table_name="billing_transactions")
    op.drop_index("idx_billing_transactions_member_date", table_name="billing_transactions")
    op.drop_index("ix_billing_transactions_tenant_id", table_name="billing_transactions")
    op.drop_table("billing_transactions")

    op.drop_index("ix_invoices_member_id", table_name="invoices")
    op.drop_index("ix_invoices_cer_id", table_name="invoices")
    op.drop_index("ix_invoices_tenant_id", table_name="invoices")
    op.drop_table("invoices")

    op.drop_index("idx_billing_statements_status_due_date", table_name="billing_statements")
    op.drop_index("idx_billing_statements_member_period", table_name="billing_statements")
    op.drop_index("idx_billing_statements_cer_period", table_name="billing_statements")
    op.drop_index("ix_billing_statements_tenant_id", table_name="billing_statements")
    op.drop_table("billing_statements")

    op.drop_index("idx_settlements_status_date", table_name="settlements")
    op.drop_index("idx_settlements_cer_period", table_name="settlements")
    op.drop_index("ix_settlements_tenant_id", table_name="settlements")
    op.drop_table("settlements")

    # Note: Enum types are created automatically by SQLAlchemy, no need to drop them here

