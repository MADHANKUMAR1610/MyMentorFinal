"""create organization ats config

Revision ID: cb1145ad8c48
Revises: 20b7ff929d47
Create Date: 2026-09-02 10:40:32.118347

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# ============================================================
# REVISION
# ============================================================

revision: str = "cb1145ad8c48"

down_revision: Union[str, Sequence[str], None] = "20b7ff929d47"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


# ============================================================
# UPGRADE
# ============================================================

def upgrade() -> None:
    """Create organization ATS configuration table."""

    op.create_table(
        "organization_ats_config",

        # ====================================================
        # PRIMARY KEY
        # ====================================================

        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),

        # ====================================================
        # COMPANY
        # ====================================================

        sa.Column(
            "company_id",
            sa.UUID(),
            nullable=False,
        ),

        # ====================================================
        # ATS WEIGHTS
        # ====================================================

        sa.Column(
            "skills",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "experience",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "education",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "role_relevance",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "screening_questions",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "certifications",
            sa.Integer(),
            nullable=False,
        ),

        # ====================================================
        # CONSTRAINTS
        # ====================================================

        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "id",
        ),
    )

    # ========================================================
    # COMPANY UNIQUE INDEX
    # ========================================================

    op.create_index(
        "ix_organization_ats_config_company_id",
        "organization_ats_config",
        ["company_id"],
        unique=True,
    )


# ============================================================
# DOWNGRADE
# ============================================================

def downgrade() -> None:
    """Remove organization ATS configuration table."""

    op.drop_index(
        "ix_organization_ats_config_company_id",
        table_name="organization_ats_config",
    )

    op.drop_table(
        "organization_ats_config",
    )