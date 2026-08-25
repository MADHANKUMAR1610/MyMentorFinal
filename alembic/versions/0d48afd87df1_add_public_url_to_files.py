"""add public url to files

Revision ID: 0d48afd87df1
Revises: 1ee99a400a40
Create Date: 2026-08-25 13:06:37.930190

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0d48afd87df1"
down_revision: Union[str, Sequence[str], None] = "1ee99a400a40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "files",
        sa.Column(
            "public_url",
            sa.Text(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "files",
        "public_url",
    )