"""Add exclusion constraint to prevent overlapping bookings

Revision ID: 004
Revises: 003
Create Date: 2026-06-18
"""

from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE bookings
        ADD CONSTRAINT overlapping_bookings_excl
        EXCLUDE USING gist (
            vehicle_id WITH =,
            daterange(start_date, end_date, '[)') WITH &&
        )
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE bookings DROP CONSTRAINT overlapping_bookings_excl")
