"""create career search knowledge

Revision ID: 7a18326beb94
Revises: 38b859829bff
Create Date: 2026-09-10 11:43:33.645507

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "7a18326beb94"
down_revision: Union[str, Sequence[str], None] = "38b859829bff"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table(
        "career_search_knowledge",

        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),

        sa.Column(
            "query",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "keywords",
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
            "is_active",
            sa.Boolean(),
            server_default="true",
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

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_career_search_knowledge_query",
        "career_search_knowledge",
        ["query"],
        unique=True,
    )


def downgrade() -> None:

    op.drop_index(
        "ix_career_search_knowledge_query",
        table_name="career_search_knowledge",
    )

    op.drop_table(
        "career_search_knowledge"
    )