"""Add 'reddit' to source_platform_enum."""

from __future__ import annotations

from alembic import op

revision = "0004_reddit_platform"
down_revision = "0003_ingested_posts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE source_platform_enum ADD VALUE IF NOT EXISTS 'reddit'")


def downgrade() -> None:
    # PostgreSQL can't drop a value from an enum type; leaving 'reddit' in place is harmless.
    pass
