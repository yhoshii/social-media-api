"""add content column to posts table

Revision ID: e64ee786a2c6
Revises: a600cc622bad
Create Date: 2026-11-24 13:23:04.702590

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e64ee786a2c6"
down_revision: str | Sequence[str] | None = "a600cc622bad"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("posts", "content")
