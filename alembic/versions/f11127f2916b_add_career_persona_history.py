"""add career persona history

Revision ID: f11127f2916b
Revises: 7a18326beb94
Create Date: 2026-09-10 12:49:49.116830

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f11127f2916b"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "7a18326beb94"

branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None

depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:

    op.alter_column(
        "jobs",
        "job_code",
        existing_type=sa.VARCHAR(length=20),
        server_default=sa.text(
            "'JOB-' || nextval('public.job_code_seq')::text"
        ),
        existing_nullable=False,
    )

    op.alter_column(
        "user_profiles",
        "profile_category",
        existing_type=sa.VARCHAR(length=50),
        type_=sa.String(length=100),
        existing_nullable=True,
    )

    op.alter_column(
        "user_profiles",
        "education",
        existing_type=sa.VARCHAR(length=255),
        type_=sa.Text(),
        existing_nullable=True,
    )

    op.alter_column(
        "user_profiles",
        "class_year",
        existing_type=sa.VARCHAR(length=50),
        type_=sa.String(length=20),
        existing_nullable=True,
    )

    op.alter_column(
        "user_profiles",
        "institution",
        existing_type=sa.VARCHAR(length=255),
        type_=sa.Text(),
        existing_nullable=True,
    )

    op.alter_column(
        "user_profiles",
        "career_goal",
        existing_type=sa.VARCHAR(length=255),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:

    op.alter_column(
        "user_profiles",
        "career_goal",
        existing_type=sa.Text(),
        type_=sa.VARCHAR(length=255),
        existing_nullable=True,
    )

    op.alter_column(
        "user_profiles",
        "institution",
        existing_type=sa.Text(),
        type_=sa.VARCHAR(length=255),
        existing_nullable=True,
    )

    op.alter_column(
        "user_profiles",
        "class_year",
        existing_type=sa.String(length=20),
        type_=sa.VARCHAR(length=50),
        existing_nullable=True,
    )

    op.alter_column(
        "user_profiles",
        "education",
        existing_type=sa.Text(),
        type_=sa.VARCHAR(length=255),
        existing_nullable=True,
    )

    op.alter_column(
        "user_profiles",
        "profile_category",
        existing_type=sa.String(length=100),
        type_=sa.VARCHAR(length=50),
        existing_nullable=True,
    )

    op.alter_column(
        "jobs",
        "job_code",
        existing_type=sa.VARCHAR(length=20),
        server_default=sa.text(
            "('JOB-'::text || "
            "(nextval('job_code_seq'::regclass))::text)"
        ),
        existing_nullable=False,
    )