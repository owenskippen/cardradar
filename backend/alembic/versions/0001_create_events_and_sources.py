from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_create_events_and_sources"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, index=True),
        sa.Column("date", sa.Date(), nullable=True, index=True),
        sa.Column("start_time", sa.Time(), nullable=True),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("venue", sa.String(length=255), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True, index=True),
        sa.Column("province", sa.String(length=10), nullable=False, server_default="BC"),
        sa.Column("postal_code", sa.String(length=20), nullable=True),
        sa.Column("organizer", sa.String(length=255), nullable=True),
        sa.Column("website_url", sa.String(length=500), nullable=True),
        sa.Column("source_url_primary", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "tags",
            postgresql.ARRAY(sa.String()),
            nullable=True,
            server_default=sa.text("ARRAY[]::varchar[]"),
        ),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("is_hidden", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("source_confidence", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id"), nullable=False),
        sa.Column(
            "platform",
            sa.Enum(
                "instagram",
                "website",
                "facebook",
                "google_events",
                "shop",
                "convention_center",
                "manual",
                name="source_platform_enum",
            ),
            nullable=False,
        ),
        sa.Column("source_url", sa.String(length=500), nullable=False),
        sa.Column(
            "scraped_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("raw_payload", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade() -> None:
    op.drop_table("sources")
    op.drop_table("events")
    op.execute("DROP TYPE IF EXISTS source_platform_enum")

