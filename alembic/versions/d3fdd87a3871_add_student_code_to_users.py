"""add student code to users

Revision ID: d3fdd87a3871
Revises: 80c243ff6037
Create Date: 2026-09-21 13:17:27.504788

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3fdd87a3871'
down_revision: Union[str, Sequence[str], None] = '80c243ff6037'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "student_code",
            sa.String(length=50),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_users_student_code",
        "users",
        ["student_code"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_users_student_code",
        table_name="users",
    )

    op.drop_column(
        "users",
        "student_code",
    )