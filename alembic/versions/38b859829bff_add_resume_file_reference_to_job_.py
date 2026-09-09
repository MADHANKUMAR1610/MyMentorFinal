"""add resume file reference to job applications

Revision ID: 38b859829bff
Revises: 31477cb46789
Create Date: 2026-09-08 11:22:09.088069

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38b859829bff'
down_revision: Union[str, Sequence[str], None] = '31477cb46789'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "job_applications",
        sa.Column(
            "resume_file_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.add_column(
        "job_applications",
        sa.Column(
            "resume_source",
            sa.String(length=30),
            nullable=True,
        ),
    )

    op.create_index(
        op.f("ix_job_applications_resume_file_id"),
        "job_applications",
        ["resume_file_id"],
        unique=False,
    )

    op.create_foreign_key(
        None,
        "job_applications",
        "files",
        ["resume_file_id"],
        ["id"],
        ondelete="SET NULL",
    )
def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        None,
        "job_applications",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_job_applications_resume_file_id"),
        table_name="job_applications",
    )

    op.drop_column(
        "job_applications",
        "resume_source",
    )

    op.drop_column(
        "job_applications",
        "resume_file_id",
    )