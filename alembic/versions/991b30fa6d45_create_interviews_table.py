"""create interviews table

Revision ID: 991b30fa6d45
Revises: f4571ac003bd
Create Date: 2026-08-28 17:38:44.247183

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "991b30fa6d45"
down_revision: Union[str, Sequence[str], None] = "f4571ac003bd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create interviews table."""

    op.create_table(
        "interviews",

        sa.Column(
            "company_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "application_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "interviewer_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.String(length=200),
            nullable=False,
        ),

        sa.Column(
            "interview_type",
            sa.String(length=30),
            nullable=False,
        ),

        sa.Column(
            "scheduled_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "duration_minutes",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "mode",
            sa.String(length=30),
            nullable=False,
        ),

        sa.Column(
            "meeting_link",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "location",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
        ),

        sa.Column(
            "rating",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "feedback",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "recommendation",
            sa.String(length=30),
            nullable=True,
        ),

        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),

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

        sa.ForeignKeyConstraint(
            ["application_id"],
            ["job_applications.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["interviewer_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_interviews_application_id",
        "interviews",
        ["application_id"],
        unique=False,
    )

    op.create_index(
        "ix_interviews_company_id",
        "interviews",
        ["company_id"],
        unique=False,
    )

    op.create_index(
        "ix_interviews_interviewer_id",
        "interviews",
        ["interviewer_id"],
        unique=False,
    )

    op.create_index(
        "ix_interviews_scheduled_at",
        "interviews",
        ["scheduled_at"],
        unique=False,
    )

    op.create_index(
        "ix_interviews_status",
        "interviews",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    """Drop interviews table."""

    op.drop_index(
        "ix_interviews_status",
        table_name="interviews",
    )

    op.drop_index(
        "ix_interviews_scheduled_at",
        table_name="interviews",
    )

    op.drop_index(
        "ix_interviews_interviewer_id",
        table_name="interviews",
    )

    op.drop_index(
        "ix_interviews_company_id",
        table_name="interviews",
    )

    op.drop_index(
        "ix_interviews_application_id",
        table_name="interviews",
    )

    op.drop_table("interviews")