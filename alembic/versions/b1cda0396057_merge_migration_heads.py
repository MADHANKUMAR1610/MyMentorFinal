"""merge migration heads

Revision ID: b1cda0396057
Revises: 93b80342891b, e6302779b353
Create Date: 2026-08-27 10:27:17.696506

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1cda0396057'
down_revision: Union[str, Sequence[str], None] = ('93b80342891b', 'e6302779b353')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
