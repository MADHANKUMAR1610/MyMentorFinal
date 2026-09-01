"""add organization member fields

Revision ID: 320ac5353056
Revises: 626e008ca83e
Create Date: 2026-09-01 10:59:39
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "320ac5353056"

down_revision: Union[str, Sequence[str], None] = "626e008ca83e"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add organization member fields to users table."""

    op.add_column(
        "users",
        sa.Column(
            "department",
            sa.String(length=150),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "designation",
            sa.String(length=150),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove organization member fields from users table."""

    op.drop_column(
        "users",
        "designation",
    )

    op.drop_column(
        "users",
        "department",
    )