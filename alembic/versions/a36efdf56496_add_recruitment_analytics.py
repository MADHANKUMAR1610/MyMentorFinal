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

    connection = op.get_bind()
    inspector = sa.inspect(connection)

    # ========================================================
    # JOB APPLICATION ANALYTICS
    # ========================================================

    job_application_columns = {
        column["name"]
        for column in inspector.get_columns("job_applications")
    }

    # recruiter_id
    # This column may already exist in the database.
    if "recruiter_id" not in job_application_columns:
        op.add_column(
            "job_applications",
            sa.Column(
                "recruiter_id",
                sa.UUID(),
                nullable=True,
            ),
        )

    # source
    if "source" not in job_application_columns:
        op.add_column(
            "job_applications",
            sa.Column(
                "source",
                sa.String(length=100),
                nullable=True,
            ),
        )

    # ats_score
    if "ats_score" not in job_application_columns:
        op.add_column(
            "job_applications",
            sa.Column(
                "ats_score",
                sa.Float(),
                nullable=True,
            ),
        )

    # match_score
    if "match_score" not in job_application_columns:
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

    # Refresh columns after possible additions above.
    inspector = sa.inspect(connection)

    job_application_columns = {
        column["name"]
        for column in inspector.get_columns("job_applications")
    }

    # screened_at
    if "screened_at" not in job_application_columns:
        op.add_column(
            "job_applications",
            sa.Column(
                "screened_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )

    # shortlisted_at
    if "shortlisted_at" not in job_application_columns:
        op.add_column(
            "job_applications",
            sa.Column(
                "shortlisted_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )

    # interviewed_at
    if "interviewed_at" not in job_application_columns:
        op.add_column(
            "job_applications",
            sa.Column(
                "interviewed_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )

    # finalist_at
    if "finalist_at" not in job_application_columns:
        op.add_column(
            "job_applications",
            sa.Column(
                "finalist_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )

    # selected_at
    if "selected_at" not in job_application_columns:
        op.add_column(
            "job_applications",
            sa.Column(
                "selected_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )

    # rejected_at
    if "rejected_at" not in job_application_columns:
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

    inspector = sa.inspect(connection)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes("job_applications")
    }

    # recruiter_id index
    if "ix_job_applications_recruiter_id" not in existing_indexes:
        op.create_index(
            "ix_job_applications_recruiter_id",
            "job_applications",
            ["recruiter_id"],
            unique=False,
        )

    # source index
    if "ix_job_applications_source" not in existing_indexes:
        op.create_index(
            "ix_job_applications_source",
            "job_applications",
            ["source"],
            unique=False,
        )

    # ats_score index
    if "ix_job_applications_ats_score" not in existing_indexes:
        op.create_index(
            "ix_job_applications_ats_score",
            "job_applications",
            ["ats_score"],
            unique=False,
        )

    # match_score index
    if "ix_job_applications_match_score" not in existing_indexes:
        op.create_index(
            "ix_job_applications_match_score",
            "job_applications",
            ["match_score"],
            unique=False,
        )

    # ========================================================
    # RECRUITER FOREIGN KEY
    # ========================================================

    inspector = sa.inspect(connection)

    existing_foreign_keys = {
        fk["name"]
        for fk in inspector.get_foreign_keys("job_applications")
    }

    if "fk_job_applications_recruiter_id_users" not in existing_foreign_keys:
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

    inspector = sa.inspect(connection)

    job_columns = {
        column["name"]
        for column in inspector.get_columns("jobs")
    }

    # opened_at
    if "opened_at" not in job_columns:
        op.add_column(
            "jobs",
            sa.Column(
                "opened_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )

    # closed_at
    if "closed_at" not in job_columns:
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

    inspector = sa.inspect(connection)

    existing_job_indexes = {
        index["name"]
        for index in inspector.get_indexes("jobs")
    }

    if "ix_jobs_opened_at" not in existing_job_indexes:
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

    connection = op.get_bind()
    inspector = sa.inspect(connection)

    # ========================================================
    # JOB ANALYTICS INDEX
    # ========================================================

    existing_job_indexes = {
        index["name"]
        for index in inspector.get_indexes("jobs")
    }

    if "ix_jobs_opened_at" in existing_job_indexes:
        op.drop_index(
            "ix_jobs_opened_at",
            table_name="jobs",
        )

    # ========================================================
    # JOB OPEN / CLOSE
    # ========================================================

    inspector = sa.inspect(connection)

    job_columns = {
        column["name"]
        for column in inspector.get_columns("jobs")
    }

    if "closed_at" in job_columns:
        op.drop_column(
            "jobs",
            "closed_at",
        )

    if "opened_at" in job_columns:
        op.drop_column(
            "jobs",
            "opened_at",
        )

    # ========================================================
    # RECRUITER FOREIGN KEY
    # ========================================================

    inspector = sa.inspect(connection)

    existing_foreign_keys = {
        fk["name"]
        for fk in inspector.get_foreign_keys("job_applications")
    }

    if "fk_job_applications_recruiter_id_users" in existing_foreign_keys:
        op.drop_constraint(
            "fk_job_applications_recruiter_id_users",
            "job_applications",
            type_="foreignkey",
        )

    # ========================================================
    # APPLICATION ANALYTICS INDEXES
    # ========================================================

    inspector = sa.inspect(connection)

    existing_indexes = {
        index["name"]
        for index in inspector.get_indexes("job_applications")
    }

    if "ix_job_applications_match_score" in existing_indexes:
        op.drop_index(
            "ix_job_applications_match_score",
            table_name="job_applications",
        )

    if "ix_job_applications_ats_score" in existing_indexes:
        op.drop_index(
            "ix_job_applications_ats_score",
            table_name="job_applications",
        )

    if "ix_job_applications_source" in existing_indexes:
        op.drop_index(
            "ix_job_applications_source",
            table_name="job_applications",
        )

    if "ix_job_applications_recruiter_id" in existing_indexes:
        op.drop_index(
            "ix_job_applications_recruiter_id",
            table_name="job_applications",
        )

    # ========================================================
    # APPLICATION FUNNEL TIMESTAMPS
    # ========================================================

    inspector = sa.inspect(connection)

    job_application_columns = {
        column["name"]
        for column in inspector.get_columns("job_applications")
    }

    if "rejected_at" in job_application_columns:
        op.drop_column(
            "job_applications",
            "rejected_at",
        )

    if "selected_at" in job_application_columns:
        op.drop_column(
            "job_applications",
            "selected_at",
        )

    if "finalist_at" in job_application_columns:
        op.drop_column(
            "job_applications",
            "finalist_at",
        )

    if "interviewed_at" in job_application_columns:
        op.drop_column(
            "job_applications",
            "interviewed_at",
        )

    if "shortlisted_at" in job_application_columns:
        op.drop_column(
            "job_applications",
            "shortlisted_at",
        )

    if "screened_at" in job_application_columns:
        op.drop_column(
            "job_applications",
            "screened_at",
        )

    # ========================================================
    # APPLICATION ANALYTICS
    # ========================================================

    inspector = sa.inspect(connection)

    job_application_columns = {
        column["name"]
        for column in inspector.get_columns("job_applications")
    }

    if "match_score" in job_application_columns:
        op.drop_column(
            "job_applications",
            "match_score",
        )

    if "ats_score" in job_application_columns:
        op.drop_column(
            "job_applications",
            "ats_score",
        )

    if "source" in job_application_columns:
        op.drop_column(
            "job_applications",
            "source",
        )

    if "recruiter_id" in job_application_columns:
        op.drop_column(
            "job_applications",
            "recruiter_id",
        )