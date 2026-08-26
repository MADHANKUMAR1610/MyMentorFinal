"""add category to courses

Revision ID: e6302779b353
Revises: e38b89e86f59
Create Date: 2026-08-26 21:11:12.992700

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e6302779b353"
down_revision: Union[str, Sequence[str], None] = "e38b89e86f59"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. Add category temporarily as nullable
    op.add_column(
        "courses",
        sa.Column(
            "category",
            sa.String(length=50),
            nullable=True,
        ),
    )

    # 2. Give existing courses a category
    op.execute(
        "UPDATE courses SET category = 'Other' WHERE category IS NULL"
    )

    # 3. Make category required
    op.alter_column(
        "courses",
        "category",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    # 4. Add index
    op.create_index(
        op.f("ix_courses_category"),
        "courses",
        ["category"],
        unique=False,
    )

def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_courses_category"),
        table_name="courses",
    )

    op.drop_column(
        "courses",
        "category",
    )