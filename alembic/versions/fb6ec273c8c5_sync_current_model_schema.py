"""sync current model schema

Revision ID: fb6ec273c8c5
Revises: 7434aef06209
Create Date: 2026-09-18 10:59:29.125911

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "fb6ec273c8c5"
down_revision: Union[str, Sequence[str], None] = "7434aef06209"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =========================================================
    # MASTER DATA
    # =========================================================

    op.create_table(
        "master_data",
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_master_data_type",
        "master_data",
        ["type"],
        unique=False,
    )

    op.create_index(
        "ix_master_data_year",
        "master_data",
        ["year"],
        unique=False,
    )

    op.create_index(
        "ix_master_data_is_active",
        "master_data",
        ["is_active"],
        unique=False,
    )

    # =========================================================
    # USER PROFILE - SKILLS
    # =========================================================

    op.add_column(
        "user_profiles",
        sa.Column(
            "skills",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default=sa.text("'{}'::character varying[]"),
        ),
    )

    op.alter_column(
        "user_profiles",
        "skills",
        server_default=None,
        existing_type=postgresql.ARRAY(sa.String()),
        existing_nullable=False,
    )

    # =========================================================
    # COLLEGE CODE
    # =========================================================

    op.drop_constraint(
        "uq_colleges_code",
        "colleges",
        type_="unique",
    )

    op.drop_index(
        "ix_colleges_code",
        table_name="colleges",
    )

    op.create_index(
        "ix_colleges_code",
        "colleges",
        ["code"],
        unique=True,
    )

    # =========================================================
    # JOB APPLICATION STATUS CHECK
    # =========================================================

    op.create_check_constraint(
        "ck_job_application_status",
        "job_applications",
        """
        status IN (
            'submitted',
            'screening',
            'shortlisted',
            'interview',
            'finalist',
            'selected',
            'rejected',
            'withdrawn'
        )
        """,
    )


def downgrade() -> None:
    # =========================================================
    # JOB APPLICATION STATUS CHECK
    # =========================================================

    op.drop_constraint(
        "ck_job_application_status",
        "job_applications",
        type_="check",
    )

    # =========================================================
    # COLLEGE CODE
    # =========================================================

    op.drop_index(
        "ix_colleges_code",
        table_name="colleges",
    )

    op.create_index(
        "ix_colleges_code",
        "colleges",
        ["code"],
        unique=False,
    )

    op.create_unique_constraint(
        "uq_colleges_code",
        "colleges",
        ["code"],
    )

    # =========================================================
    # USER PROFILE - SKILLS
    # =========================================================

    op.drop_column(
        "user_profiles",
        "skills",
    )

    # =========================================================
    # MASTER DATA
    # =========================================================

    op.drop_index(
        "ix_master_data_is_active",
        table_name="master_data",
    )

    op.drop_index(
        "ix_master_data_year",
        table_name="master_data",
    )

    op.drop_index(
        "ix_master_data_type",
        table_name="master_data",
    )

    op.drop_table("master_data")