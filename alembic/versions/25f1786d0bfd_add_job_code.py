"""add job code

Revision ID: 25f1786d0bfd
Revises: 1c394b4b451b
Create Date: 2026-09-02 17:01:27.756954

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "25f1786d0bfd"
down_revision: Union[str, Sequence[str], None] = "1c394b4b451b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ============================================================
    # 1. Create sequence for Job Code
    # ============================================================

    op.execute(
        """
        CREATE SEQUENCE IF NOT EXISTS job_code_seq
        START WITH 1001
        INCREMENT BY 1
        """
    )

    # ============================================================
    # 2. Add job_code column temporarily as nullable
    # ============================================================

    op.add_column(
        "jobs",
        sa.Column(
            "job_code",
            sa.String(length=20),
            nullable=True,
        ),
    )

    # ============================================================
    # 3. Generate Job Codes for existing jobs
    #
    # JOB-1001
    # JOB-1002
    # JOB-1003
    # ...
    # ============================================================

    op.execute(
        """
        WITH numbered_jobs AS (
            SELECT
                id,
                ROW_NUMBER() OVER (
                    ORDER BY created_at ASC, id ASC
                ) AS row_number
            FROM jobs
        )
        UPDATE jobs
        SET job_code =
            'JOB-' ||
            (1000 + numbered_jobs.row_number)::text
        FROM numbered_jobs
        WHERE jobs.id = numbered_jobs.id
        """
    )

    # ============================================================
    # 4. Move sequence to the latest existing Job Code
    # ============================================================

    op.execute(
        """
        SELECT setval(
            'job_code_seq',
            COALESCE(
                (
                    SELECT MAX(
                        CAST(
                            SUBSTRING(job_code FROM 5)
                            AS INTEGER
                        )
                    )
                    FROM jobs
                    WHERE job_code IS NOT NULL
                ),
                1000
            )
        )
        """
    )

    # ============================================================
    # 5. Automatically generate Job Code for new jobs
    # ============================================================

    op.alter_column(
        "jobs",
        "job_code",
        server_default=sa.text(
            "'JOB-' || nextval('job_code_seq')::text"
        ),
        nullable=False,
    )

    # ============================================================
    # 6. Make Job Code unique
    # ============================================================

    op.create_index(
        "uq_jobs_job_code",
        "jobs",
        ["job_code"],
        unique=True,
    )


def downgrade() -> None:

    # ============================================================
    # 1. Remove unique index
    # ============================================================

    op.drop_index(
        "uq_jobs_job_code",
        table_name="jobs",
    )

    # ============================================================
    # 2. Remove job_code column
    # ============================================================

    op.drop_column(
        "jobs",
        "job_code",
    )

    # ============================================================
    # 3. Remove sequence
    # ============================================================

    op.execute(
        "DROP SEQUENCE IF EXISTS job_code_seq"
    )