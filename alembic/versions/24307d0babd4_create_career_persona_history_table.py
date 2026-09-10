"""create career persona history table

Revision ID: 24307d0babd4
Revises: f11127f2916b
Create Date: 2026-09-10 13:18:55.815277

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "24307d0babd4"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "f11127f2916b"

branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None

depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:

    # ========================================================
    # CREATE CAREER PERSONA HISTORY TABLE
    # ========================================================

    op.create_table(
        "career_persona_history",

        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "career_persona_id",
            sa.UUID(),
            nullable=True,
        ),

        sa.Column(
            "goal",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "profile",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            nullable=False,
        ),

        sa.Column(
            "answers",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            nullable=False,
        ),

        sa.Column(
            "result",
            postgresql.JSONB(
                astext_type=sa.Text()
            ),
            nullable=False,
        ),

        sa.Column(
            "is_profile_visible",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["career_persona_id"],
            ["career_personas.id"],
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),

        sa.PrimaryKeyConstraint(
            "id"
        ),
    )


def downgrade() -> None:

    # ========================================================
    # DROP CAREER PERSONA HISTORY TABLE
    # ========================================================

    op.drop_table(
        "career_persona_history"
    )