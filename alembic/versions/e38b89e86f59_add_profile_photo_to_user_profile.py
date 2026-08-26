"""add profile photo to user profile

Revision ID: e38b89e86f59
Revises: 0d48afd87df1
Create Date: 2026-08-26 11:56:47.356627

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e38b89e86f59"
down_revision: Union[str, Sequence[str], None] = "0d48afd87df1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # =========================================================
    # ADD PROFILE PHOTO FILE ID
    # =========================================================

    op.add_column(
        "user_profiles",
        sa.Column(
            "profile_photo_file_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    # =========================================================
    # CREATE INDEX
    # =========================================================

    op.create_index(
        op.f("ix_user_profiles_profile_photo_file_id"),
        "user_profiles",
        ["profile_photo_file_id"],
        unique=False,
    )

    # =========================================================
    # CREATE FOREIGN KEY
    # =========================================================

    op.create_foreign_key(
        "fk_user_profiles_profile_photo_file_id_files",
        "user_profiles",
        "files",
        ["profile_photo_file_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""

    # =========================================================
    # DROP FOREIGN KEY
    # =========================================================

    op.drop_constraint(
        "fk_user_profiles_profile_photo_file_id_files",
        "user_profiles",
        type_="foreignkey",
    )

    # =========================================================
    # DROP INDEX
    # =========================================================

    op.drop_index(
        op.f("ix_user_profiles_profile_photo_file_id"),
        table_name="user_profiles",
    )

    # =========================================================
    # DROP COLUMN
    # =========================================================

    op.drop_column(
        "user_profiles",
        "profile_photo_file_id",
    )