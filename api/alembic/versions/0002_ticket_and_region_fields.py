from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_ticket_and_region_fields"
down_revision = "0001_create_events_and_sources"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("events", sa.Column("end_date", sa.Date(), nullable=True))
    op.add_column(
        "events",
        sa.Column("country", sa.String(length=2), nullable=False, server_default=sa.text("'CA'")),
    )
    op.create_index("ix_events_country", "events", ["country"])
    op.add_column("events", sa.Column("ticket_url", sa.String(length=500), nullable=True))
    op.add_column("events", sa.Column("admission", sa.String(length=100), nullable=True))
    op.add_column("events", sa.Column("table_count", sa.Integer(), nullable=True))
    op.add_column("events", sa.Column("image_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("events", "image_url")
    op.drop_column("events", "table_count")
    op.drop_column("events", "admission")
    op.drop_column("events", "ticket_url")
    op.drop_index("ix_events_country", table_name="events")
    op.drop_column("events", "country")
    op.drop_column("events", "end_date")
