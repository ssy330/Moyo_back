"""initial schema

Revision ID: 2fdf051de650
Revises: b2c82845106b
Create Date: 2025-11-19 18:42:54.500466

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2fdf051de650'
down_revision: Union[str, Sequence[str], None] = 'b2c82845106b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
