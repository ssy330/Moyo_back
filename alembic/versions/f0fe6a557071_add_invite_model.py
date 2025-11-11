"""add invite model

Revision ID: f0fe6a557071
Revises: 115441a57037
Create Date: 2025-11-11 03:39:51.728181

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0fe6a557071'
down_revision: Union[str, Sequence[str], None] = '115441a57037'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
