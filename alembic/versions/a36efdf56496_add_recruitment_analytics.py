"""add recruitment analytics

Revision ID: a36efdf56496
Revises: 626e008ca83e
Create Date: 2026-09-01
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# ============================================================
# REVISION
# ============================================================

revision: str = "a36efdf56496"

down_revision: Union[str, Sequence[str], None] = "626e008ca83e"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


# ============================================================
# UPGRADE
# ============================================================

def upgrade() -> None:

    # ========================================================
    # JOB APPLICATION ANALYTICS
    # ========================================================

    op.add_column(
        "job_applications",
        sa.Column(
            "recruiter_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.add_column(
        "job_applications",
        sa.Column(
            "source",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "job_applications",
        sa.Column(
            "ats_score",
            sa.Float(),
            nullable=True,
        ),
    )

    op.add_column(
        "job_applications",
        sa.Column(
            "match_score",
            sa.Float(),
            nullable=True,
        ),
    )

    # ========================================================
    # APPLICATION FUNNEL TIMESTAMPS
    # ========================================================

    op.add_column(
        "job_applications",
        sa.Column(
            "screened_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "job_applications",
        sa.Column(
            "shortlisted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "job_applications",
        sa.Column(
            "interviewed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "job_applications",
        sa.Column(
            "finalist_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "job_applications",
        sa.Column(
            "selected_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "job_applications",
        sa.Column(
            "rejected_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # ========================================================
    # APPLICATION ANALYTICS INDEXES
    # ========================================================

    op.create_index(
        "ix_job_applications_recruiter_id",
        "job_applications",
        ["recruiter_id"],
        unique=False,
    )

    op.create_index(
        "ix_job_applications_source",
        "job_applications",
        ["source"],
        unique=False,
    )

    op.create_index(
        "ix_job_applications_ats_score",
        "job_applications",
        ["ats_score"],
        unique=False,
    )

    op.create_index(
        "ix_job_applications_match_score",
        "job_applications",
        ["match_score"],
        unique=False,
    )

    # ========================================================
    # RECRUITER FOREIGN KEY
    # ========================================================

    op.create_foreign_key(
        "fk_job_applications_recruiter_id_users",
        "job_applications",
        "users",
        ["recruiter_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # ========================================================
    # JOB OPEN / CLOSE ANALYTICS
    # ========================================================

    op.add_column(
        "jobs",
        sa.Column(
            "opened_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "jobs",
        sa.Column(
            "closed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # ========================================================
    # JOB ANALYTICS INDEXES
    # ========================================================

    op.create_index(
        "ix_jobs_opened_at",
        "jobs",
        ["opened_at"],
        unique=False,
    )


# ============================================================
# DOWNGRADE
# ============================================================

def downgrade() -> None:

    # ========================================================
    # JOB ANALYTICS INDEX
    # ========================================================

    op.drop_index(
        "ix_jobs_opened_at",
        table_name="jobs",
    )

    # ========================================================
    # JOB OPEN / CLOSE
    # ========================================================

    op.drop_column(
        "jobs",
        "closed_at",
    )

    op.drop_column(
        "jobs",
        "opened_at",
    )

    # ========================================================
    # RECRUITER FOREIGN KEY
    # ========================================================

    op.drop_constraint(
        "fk_job_applications_recruiter_id_users",
        "job_applications",
        type_="foreignkey",
    )

    # ========================================================
    # APPLICATION ANALYTICS INDEXES
    # ========================================================

    op.drop_index(
        "ix_job_applications_match_score",
        table_name="job_applications",
    )

    op.drop_index(
        "ix_job_applications_ats_score",
        table_name="job_applications",
    )

    op.drop_index(
        "ix_job_applications_source",
        table_name="job_applications",
    )

    op.drop_index(
        "ix_job_applications_recruiter_id",
        table_name="job_applications",
    )

    # ========================================================
    # APPLICATION FUNNEL TIMESTAMPS
    # ========================================================

    op.drop_column(
        "job_applications",
        "rejected_at",
    )

    op.drop_column(
        "job_applications",
        "selected_at",
    )

    op.drop_column(
        "job_applications",
        "finalist_at",
    )

    op.drop_column(
        "job_applications",
        "interviewed_at",
    )

    op.drop_column(
        "job_applications",
        "shortlisted_at",
    )

    op.drop_column(
        "job_applications",
        "screened_at",
    )

    # ========================================================
    # APPLICATION ANALYTICS
    # ========================================================

    op.drop_column(
        "job_applications",
        "match_score",
    )

    op.drop_column(
        "job_applications",
        "ats_score",
    )

    op.drop_column(
        "job_applications",
        "source",
    )

    op.drop_column(
        "job_applications",
        "recruiter_id",
    )