from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0003_ingested_posts"
down_revision = "0002_ticket_and_region_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ingested_posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("platform", sa.String(length=32), nullable=False),
        sa.Column("outcome", sa.String(length=20), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("first_checked_at", sa.DateTime(), nullable=False),
        sa.Column("last_checked_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_ingested_posts_url", "ingested_posts", ["url"], unique=True)
    op.create_index("ix_ingested_posts_outcome", "ingested_posts", ["outcome"])


def downgrade() -> None:
    op.drop_index("ix_ingested_posts_outcome", table_name="ingested_posts")
    op.drop_index("ix_ingested_posts_url", table_name="ingested_posts")
    op.drop_table("ingested_posts")
