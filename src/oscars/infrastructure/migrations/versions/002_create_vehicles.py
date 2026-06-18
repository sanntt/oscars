"""Create vehicles table

Revision ID: 002
Revises: 001
Create Date: 2026-06-18
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vehicles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("dealer", sa.String(), nullable=False),
        sa.Column("daily_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("vehicles")
