"""add profile visibility to career persona

Revision ID: 49c72d6f2adf
Revises: b1cda0396057
Create Date: 2026-08-27 10:29:12.262623

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "49c72d6f2adf"

down_revision: Union[str, Sequence[str], None] = "b1cda0396057"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "career_personas",
        sa.Column(
            "is_profile_visible",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "career_personas",
        "is_profile_visible",
    )