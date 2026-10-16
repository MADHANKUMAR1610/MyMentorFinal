
"""add interviewer id to jobs

Revision ID: d5b0566585b6
Revises: 2384174ec8c4
Create Date: 2026-10-16 17:01:12.569047
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "d5b0566585b6"
down_revision: Union[str, Sequence[str], None] = "2384174ec8c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add interviewer_id to jobs."""

    op.add_column(
        "jobs",
        sa.Column(
            "interviewer_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_jobs_interviewer_id_users",
        "jobs",
        "users",
        ["interviewer_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_index(
        "ix_jobs_interviewer_id",
        "jobs",
        ["interviewer_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove interviewer_id from jobs."""

    op.drop_index(
        "ix_jobs_interviewer_id",
        table_name="jobs",
    )

    op.drop_constraint(
        "fk_jobs_interviewer_id_users",
        "jobs",
        type_="foreignkey",
    )

    op.drop_column(
        "jobs",
        "interviewer_id",
    )
