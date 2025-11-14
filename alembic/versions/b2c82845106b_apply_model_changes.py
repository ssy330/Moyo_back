"""apply model changes

Revision ID: b2c82845106b
Revises: f0fe6a557071
Create Date: 2025-11-12 18:00:30.656684

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c82845106b'
down_revision: Union[str, Sequence[str], None] = 'f0fe6a557071'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
