
"""add mentor application session fields

Revision ID: 2384174ec8c4
Revises: 43b90d5249db
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2384174ec8c4"
down_revision: Union[str, Sequence[str], None] = "43b90d5249db"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Preserve the existing jobs.job_code change.
    op.alter_column(
        "jobs",
        "job_code",
        existing_type=sa.VARCHAR(length=20),
        server_default=sa.text(
            "'JOB-' || nextval('public.job_code_seq')::text"
        ),
        existing_nullable=False,
    )

    # Add fields to the existing mentor_applications table.
    op.add_column(
        "mentor_applications",
        sa.Column(
            "price_per_session",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1000"),
        ),
    )

    op.add_column(
        "mentor_applications",
        sa.Column(
            "availability",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text("'Flexible'"),
        ),
    )

    op.add_column(
        "mentor_applications",
        sa.Column(
            "start_time",
            sa.Time(),
            nullable=False,
            server_default=sa.text("'09:00:00'"),
        ),
    )

    op.add_column(
        "mentor_applications",
        sa.Column(
            "end_time",
            sa.Time(),
            nullable=False,
            server_default=sa.text("'17:00:00'"),
        ),
    )


def downgrade() -> None:
    op.drop_column("mentor_applications", "end_time")
    op.drop_column("mentor_applications", "start_time")
    op.drop_column("mentor_applications", "availability")
    op.drop_column("mentor_applications", "price_per_session")

    # Restore the previous job_code default.
    op.alter_column(
        "jobs",
        "job_code",
        existing_type=sa.VARCHAR(length=20),
        server_default=sa.text(
            "('JOB-'::text || (nextval('job_code_seq'::regclass))::text)"
        ),
        existing_nullable=False,
    )
