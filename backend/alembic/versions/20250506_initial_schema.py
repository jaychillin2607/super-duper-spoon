import alembic.op as op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = "0e5f3c7d3a1b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create leads table
    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        # Step 1: Personal information
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("last_name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=False),
        # Step 2: Business information
        sa.Column("business_name", sa.String(), nullable=False),
        sa.Column("tin", sa.String(), nullable=False),
        sa.Column("zip_code", sa.String(), nullable=False),
        # Step 3: Business details
        sa.Column("monthly_revenue", sa.Float(), nullable=False),
        sa.Column("years_in_business", sa.Float(), nullable=False),
        # Enrichment data from TIB API
        sa.Column(
            "enrichment_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        # Timestamps
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        # Primary key
        sa.PrimaryKeyConstraint("id"),
        # Composite unique constraint
        sa.UniqueConstraint("email", "business_name",
                            name="uq_lead_email_business"),
    )

    # Create indexes
    op.create_index(op.f("ix_leads_id"), "leads", ["id"], unique=False)
    op.create_index(op.f("ix_leads_email"), "leads", ["email"], unique=False)
    op.create_index(
        op.f("ix_leads_business_name"), "leads", ["business_name"], unique=False
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f("ix_leads_business_name"), table_name="leads")
    op.drop_index(op.f("ix_leads_email"), table_name="leads")
    op.drop_index(op.f("ix_leads_id"), table_name="leads")

    # Drop leads table
    op.drop_table("leads")
