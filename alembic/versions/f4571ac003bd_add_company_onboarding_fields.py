"""add company onboarding fields

Revision ID: f4571ac003bd
Revises: 49c72d6f2adf
Create Date: 2026-08-27 15:11:02.074217

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# ============================================================
# REVISION IDENTIFIERS
# ============================================================

revision: str = "f4571ac003bd"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "49c72d6f2adf"

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


# ============================================================
# UPGRADE
# ============================================================

def upgrade() -> None:
    """
    Add company onboarding fields.

    Changes:

    companies:
        - contact_person_name
        - contact_email
        - contact_phone
        - contact_role
        - admin_user_id

    users:
        - company_id
    """

    # ========================================================
    # COMPANIES - CONTACT PERSON
    # ========================================================

    op.add_column(
        "companies",
        sa.Column(
            "contact_person_name",
            sa.String(length=150),
            nullable=True,
        ),
    )

    op.add_column(
        "companies",
        sa.Column(
            "contact_email",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "companies",
        sa.Column(
            "contact_phone",
            sa.String(length=20),
            nullable=True,
        ),
    )

    op.add_column(
        "companies",
        sa.Column(
            "contact_role",
            sa.String(length=100),
            nullable=True,
        ),
    )

    # ========================================================
    # COMPANIES - ADMIN USER
    # ========================================================

    op.add_column(
        "companies",
        sa.Column(
            "admin_user_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.create_unique_constraint(
        "uq_companies_admin_user_id",
        "companies",
        ["admin_user_id"],
    )

    # ========================================================
    # USERS - COMPANY
    # ========================================================

    op.add_column(
        "users",
        sa.Column(
            "company_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_users_company_id",
        "users",
        ["company_id"],
        unique=False,
    )

    # ========================================================
    # FOREIGN KEYS
    # ========================================================
    #
    # Both columns now exist, so we can safely create
    # the circular foreign-key relationships.
    #

    op.create_foreign_key(
        "fk_companies_admin_user_id_users",
        "companies",
        "users",
        ["admin_user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_foreign_key(
        "fk_users_company_id_companies",
        "users",
        "companies",
        ["company_id"],
        ["id"],
        ondelete="SET NULL",
    )


# ============================================================
# DOWNGRADE
# ============================================================

def downgrade() -> None:
    """
    Remove company onboarding fields.
    """

    # ========================================================
    # DROP USERS -> COMPANIES FOREIGN KEY
    # ========================================================

    op.drop_constraint(
        "fk_users_company_id_companies",
        "users",
        type_="foreignkey",
    )

    # ========================================================
    # DROP USERS COMPANY INDEX
    # ========================================================

    op.drop_index(
        "ix_users_company_id",
        table_name="users",
    )

    # ========================================================
    # DROP USERS COMPANY COLUMN
    # ========================================================

    op.drop_column(
        "users",
        "company_id",
    )

    # ========================================================
    # DROP COMPANIES -> USERS FOREIGN KEY
    # ========================================================

    op.drop_constraint(
        "fk_companies_admin_user_id_users",
        "companies",
        type_="foreignkey",
    )

    # ========================================================
    # DROP UNIQUE CONSTRAINT
    # ========================================================

    op.drop_constraint(
        "uq_companies_admin_user_id",
        "companies",
        type_="unique",
    )

    # ========================================================
    # DROP ADMIN USER COLUMN
    # ========================================================

    op.drop_column(
        "companies",
        "admin_user_id",
    )

    # ========================================================
    # DROP CONTACT FIELDS
    # ========================================================

    op.drop_column(
        "companies",
        "contact_role",
    )

    op.drop_column(
        "companies",
        "contact_phone",
    )

    op.drop_column(
        "companies",
        "contact_email",
    )

    op.drop_column(
        "companies",
        "contact_person_name",
    )