"""add department and designation to users

Revision ID: 0beb23c02df9
Revises: 320ac5353056
Create Date: 2026-09-01 17:51:44.335133

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0beb23c02df9"
down_revision: Union[str, Sequence[str], None] = "320ac5353056"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.alter_column(
        "users",
        "department",
        existing_type=sa.VARCHAR(length=150),
        type_=sa.String(length=100),
        existing_nullable=True,
    )

    op.alter_column(
        "users",
        "designation",
        existing_type=sa.VARCHAR(length=150),
        type_=sa.String(length=100),
        existing_nullable=True,
    )


def downgrade() -> None:

    op.alter_column(
        "users",
        "department",
        existing_type=sa.String(length=100),
        type_=sa.VARCHAR(length=150),
        existing_nullable=True,
    )

    op.alter_column(
        "users",
        "designation",
        existing_type=sa.String(length=100),
        type_=sa.VARCHAR(length=150),
        existing_nullable=True,
    )