"""add work experiences

Revision ID: 3c48b59b9cc8
Revises: e38b89e86f59
Create Date: 2026-08-26 17:37:17.846952

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3c48b59b9cc8"
down_revision: Union[str, Sequence[str], None] = "e38b89e86f59"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ---------------------------------------------------------
    # Fix existing NULL public_url values first
    # ---------------------------------------------------------

    op.execute(
        """
        UPDATE files
        SET public_url = ''
        WHERE public_url IS NULL
        """
    )

    # ---------------------------------------------------------
    # Now make public_url NOT NULL
    # ---------------------------------------------------------

    op.alter_column(
        "files",
        "public_url",
        existing_type=sa.TEXT(),
        nullable=False,
    )

    # ---------------------------------------------------------
    # Add your work experience table changes here
    # ---------------------------------------------------------

    # No work_experiences table was generated in the
    # migration you currently have.


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "files",
        "public_url",
        existing_type=sa.TEXT(),
        nullable=True,
    )