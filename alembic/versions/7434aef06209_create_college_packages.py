"""create college packages

Revision ID: 7434aef06209
Revises: 5c6b1583a829
Create Date: 2026-09-17 11:39:21.778524

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7434aef06209"

down_revision: Union[
    str,
    Sequence[str],
    None
] = "5c6b1583a829"

branch_labels: Union[
    str,
    Sequence[str],
    None
] = None

depends_on: Union[
    str,
    Sequence[str],
    None
] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ========================================================
    # COLLEGE PACKAGES
    # ========================================================

    op.create_table(
        "college_packages",

        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "college_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "package_name",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
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
            ["college_id"],
            ["colleges.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),

        sa.UniqueConstraint(
            "college_id",
            "package_name",
            name="uq_college_package_name",
        ),
    )

    op.create_index(
        "ix_college_packages_college_id",
        "college_packages",
        ["college_id"],
    )

    # ========================================================
    # COLLEGE PACKAGE COURSES
    # ========================================================

    op.create_table(
        "college_package_courses",

        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "package_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "course_id",
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
            ["package_id"],
            ["college_packages.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),

        sa.UniqueConstraint(
            "package_id",
            "course_id",
            name="uq_college_package_course",
        ),
    )

    op.create_index(
        "ix_college_package_courses_package_id",
        "college_package_courses",
        ["package_id"],
    )

    op.create_index(
        "ix_college_package_courses_course_id",
        "college_package_courses",
        ["course_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_college_package_courses_course_id",
        table_name="college_package_courses",
    )

    op.drop_index(
        "ix_college_package_courses_package_id",
        table_name="college_package_courses",
    )

    op.drop_table(
        "college_package_courses"
    )

    op.drop_index(
        "ix_college_packages_college_id",
        table_name="college_packages",
    )

    op.drop_table(
        "college_packages"
    )