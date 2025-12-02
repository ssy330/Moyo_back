"""add thumbnail_url_to_posts

Revision ID: 00ea24364b3c
Revises: 2fdf051de650
Create Date: 2025-12-01 22:50:13.127282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00ea24364b3c'
down_revision: Union[str, Sequence[str], None] = '2fdf051de650'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "posts",
        sa.Column("thumbnail_url", sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("posts", "thumbnail_url")
