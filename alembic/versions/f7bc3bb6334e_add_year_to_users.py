"""add year to users

Revision ID: f7bc3bb6334e
Revises: d3fdd87a3871
Create Date: 2026-09-21 13:36:13.616476

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7bc3bb6334e'
down_revision: Union[str, Sequence[str], None] = 'd3fdd87a3871'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "year",
            sa.String(length=30),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "users",
        "year",
    )