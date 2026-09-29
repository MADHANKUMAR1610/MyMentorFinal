"""add mcq progress fields

Revision ID: 95a62d02c051
Revises: 4e3f9cf6127c
Create Date: 2026-09-29 15:52:25.107011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "95a62d02c051"
down_revision: Union[str, Sequence[str], None] = "4e3f9cf6127c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add MCQ progress fields."""

    op.add_column(
        "progress",
        sa.Column(
            "mcqs_answered",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )

    op.add_column(
        "progress",
        sa.Column(
            "mcqs_completed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    """Remove MCQ progress fields."""

    op.drop_column(
        "progress",
        "mcqs_completed",
    )

    op.drop_column(
        "progress",
        "mcqs_answered",
    )