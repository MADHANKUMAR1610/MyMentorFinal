"""create colleges table

Revision ID: 5c6b1583a829
Revises: 24307d0babd4
Create Date: 2026-09-17 10:46:15.461456

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5c6b1583a829"
down_revision: Union[str, Sequence[str], None] = "24307d0babd4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create colleges table."""

    op.create_table(
        "colleges",

        # =====================================================
        # PRIMARY KEY
        # =====================================================

        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),

        # =====================================================
        # BASIC COLLEGE DETAILS
        # =====================================================

        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "code",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "college_type",
            sa.String(length=50),
            nullable=True,
        ),

        sa.Column(
            "established_year",
            sa.Integer(),
            nullable=True,
        ),

        sa.Column(
            "university_affiliation",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "accreditation",
            sa.String(length=255),
            nullable=True,
        ),

        # =====================================================
        # CONTACT INFORMATION
        # =====================================================

        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "phone",
            sa.String(length=20),
            nullable=False,
        ),

        sa.Column(
            "website",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "principal_dean_name",
            sa.String(length=150),
            nullable=True,
        ),

        sa.Column(
            "contact_person",
            sa.String(length=150),
            nullable=True,
        ),

        # =====================================================
        # ADDRESS
        # =====================================================

        sa.Column(
            "address",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "city",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "state",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "country",
            sa.String(length=100),
            nullable=False,
            server_default="India",
        ),

        sa.Column(
            "pincode",
            sa.String(length=10),
            nullable=False,
        ),

        # =====================================================
        # ADDITIONAL INFORMATION
        # =====================================================

        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            server_default="active",
        ),

        # =====================================================
        # TIMESTAMPS
        # =====================================================

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),

        # =====================================================
        # CONSTRAINTS
        # =====================================================

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint(
            "code",
            name="uq_colleges_code",
        ),
    )

    # =========================================================
    # INDEXES
    # =========================================================

    op.create_index(
        "ix_colleges_name",
        "colleges",
        ["name"],
    )

    op.create_index(
        "ix_colleges_code",
        "colleges",
        ["code"],
    )

    op.create_index(
        "ix_colleges_college_type",
        "colleges",
        ["college_type"],
    )

    op.create_index(
        "ix_colleges_email",
        "colleges",
        ["email"],
    )

    op.create_index(
        "ix_colleges_city",
        "colleges",
        ["city"],
    )

    op.create_index(
        "ix_colleges_state",
        "colleges",
        ["state"],
    )

    op.create_index(
        "ix_colleges_pincode",
        "colleges",
        ["pincode"],
    )

    op.create_index(
        "ix_colleges_status",
        "colleges",
        ["status"],
    )


def downgrade() -> None:
    """Drop colleges table."""

    op.drop_index(
        "ix_colleges_status",
        table_name="colleges",
    )

    op.drop_index(
        "ix_colleges_pincode",
        table_name="colleges",
    )

    op.drop_index(
        "ix_colleges_state",
        table_name="colleges",
    )

    op.drop_index(
        "ix_colleges_city",
        table_name="colleges",
    )

    op.drop_index(
        "ix_colleges_email",
        table_name="colleges",
    )

    op.drop_index(
        "ix_colleges_college_type",
        table_name="colleges",
    )

    op.drop_index(
        "ix_colleges_code",
        table_name="colleges",
    )

    op.drop_index(
        "ix_colleges_name",
        table_name="colleges",
    )

    op.drop_table("colleges")