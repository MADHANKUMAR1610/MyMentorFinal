
"""add skill assessment submissions

Revision ID: 9ff5a2ced001
Revises: d5b0566585b6
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "9ff5a2ced001"
down_revision: Union[str, Sequence[str], None] = "d5b0566585b6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "skill_assessment_submissions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "question_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "passed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "points_earned",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["skill_assessment_questions.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "user_id",
            "question_id",
            name="uq_skill_assessment_user_question",
        ),
    )


def downgrade() -> None:
    op.drop_table("skill_assessment_submissions")
