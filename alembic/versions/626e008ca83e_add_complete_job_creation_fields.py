"""add complete job creation fields

Revision ID: 626e008ca83e
Revises: 991b30fa6d45
Create Date: 2026-08-31 21:35:53.862920

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "626e008ca83e"
down_revision: Union[str, Sequence[str], None] = "991b30fa6d45"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # JOB BASIC INFORMATION
    # ============================================================

    op.add_column(
        "jobs",
        sa.Column(
            "recruiter_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.add_column(
        "jobs",
        sa.Column(
            "hiring_manager_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.add_column(
        "jobs",
        sa.Column(
            "department",
            sa.String(length=150),
            nullable=True,
        ),
    )

    op.add_column(
        "jobs",
        sa.Column(
            "work_mode",
            sa.String(length=50),
            nullable=True,
        ),
    )

    op.add_column(
        "jobs",
        sa.Column(
            "min_experience",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "jobs",
        sa.Column(
            "max_experience",
            sa.Integer(),
            nullable=True,
        ),
    )

    # Existing jobs need a value.
    op.add_column(
        "jobs",
        sa.Column(
            "openings",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )

    op.add_column(
        "jobs",
        sa.Column(
            "salary_min",
            sa.Numeric(
                precision=12,
                scale=2,
            ),
            nullable=True,
        ),
    )

    op.add_column(
        "jobs",
        sa.Column(
            "salary_max",
            sa.Numeric(
                precision=12,
                scale=2,
            ),
            nullable=True,
        ),
    )

    # ============================================================
    # JOB DESCRIPTION
    # ============================================================

    op.add_column(
        "jobs",
        sa.Column(
            "summary",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "jobs",
        sa.Column(
            "responsibilities",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default=sa.text("'{}'::varchar[]"),
        ),
    )

    op.add_column(
        "jobs",
        sa.Column(
            "required_skills",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default=sa.text("'{}'::varchar[]"),
        ),
    )

    op.add_column(
        "jobs",
        sa.Column(
            "preferred_skills",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default=sa.text("'{}'::varchar[]"),
        ),
    )

    op.add_column(
        "jobs",
        sa.Column(
            "education",
            sa.String(length=150),
            nullable=True,
        ),
    )

    # ============================================================
    # REQUIREMENTS
    # ============================================================

    op.add_column(
        "jobs",
        sa.Column(
            "mandatory_requirements",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default=sa.text("'{}'::varchar[]"),
        ),
    )

    op.add_column(
        "jobs",
        sa.Column(
            "preferred_requirements",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default=sa.text("'{}'::varchar[]"),
        ),
    )

    # ============================================================
    # SCREENING QUESTIONS
    # ============================================================

    op.add_column(
        "jobs",
        sa.Column(
            "screening_questions",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )

    # ============================================================
    # ATS CONFIGURATION
    # ============================================================

    op.add_column(
        "jobs",
        sa.Column(
            "ats_configuration",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text(
                """'{
                    "skills": 30,
                    "experience": 20,
                    "education": 15,
                    "role_relevance": 20,
                    "screening_questions": 10,
                    "certifications": 5
                }'::jsonb"""
            ),
        ),
    )

    # ============================================================
    # DESCRIPTION - ALLOW NULL FOR DRAFTS
    # ============================================================

    op.alter_column(
        "jobs",
        "description",
        existing_type=sa.TEXT(),
        nullable=True,
    )

    # ============================================================
    # INDEXES
    # ============================================================

    op.create_index(
        "ix_jobs_hiring_manager_id",
        "jobs",
        ["hiring_manager_id"],
        unique=False,
    )

    op.create_index(
        "ix_jobs_recruiter_id",
        "jobs",
        ["recruiter_id"],
        unique=False,
    )

    # ============================================================
    # FOREIGN KEYS
    # ============================================================

    op.create_foreign_key(
        "fk_jobs_recruiter_id_users",
        "jobs",
        "users",
        ["recruiter_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_foreign_key(
        "fk_jobs_hiring_manager_id_users",
        "jobs",
        "users",
        ["hiring_manager_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:

    # ============================================================
    # FOREIGN KEYS
    # ============================================================

    op.drop_constraint(
        "fk_jobs_hiring_manager_id_users",
        "jobs",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_jobs_recruiter_id_users",
        "jobs",
        type_="foreignkey",
    )

    # ============================================================
    # INDEXES
    # ============================================================

    op.drop_index(
        "ix_jobs_recruiter_id",
        table_name="jobs",
    )

    op.drop_index(
        "ix_jobs_hiring_manager_id",
        table_name="jobs",
    )

    # ============================================================
    # DESCRIPTION
    # ============================================================

    op.alter_column(
        "jobs",
        "description",
        existing_type=sa.TEXT(),
        nullable=False,
    )

    # ============================================================
    # REMOVE NEW COLUMNS
    # ============================================================

    op.drop_column("jobs", "ats_configuration")
    op.drop_column("jobs", "screening_questions")
    op.drop_column("jobs", "preferred_requirements")
    op.drop_column("jobs", "mandatory_requirements")
    op.drop_column("jobs", "education")
    op.drop_column("jobs", "preferred_skills")
    op.drop_column("jobs", "required_skills")
    op.drop_column("jobs", "responsibilities")
    op.drop_column("jobs", "summary")
    op.drop_column("jobs", "salary_max")
    op.drop_column("jobs", "salary_min")
    op.drop_column("jobs", "openings")
    op.drop_column("jobs", "max_experience")
    op.drop_column("jobs", "min_experience")
    op.drop_column("jobs", "work_mode")
    op.drop_column("jobs", "department")
    op.drop_column("jobs", "hiring_manager_id")
    op.drop_column("jobs", "recruiter_id")