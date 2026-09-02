"""merge migration heads

Revision ID: 20b7ff929d47
Revises: 0beb23c02df9, a36efdf56496
Create Date: 2026-09-02 10:33:24.098848

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20b7ff929d47'
down_revision: Union[str, Sequence[str], None] = ('0beb23c02df9', 'a36efdf56496')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
