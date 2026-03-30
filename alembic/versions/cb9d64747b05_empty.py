"""empty

Revision ID: cb9d64747b05
Revises: 0f8414284f74
Create Date: 2025-11-28 16:16:39.815858

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb9d64747b05'
down_revision: Union[str, None] = '0f8414284f74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
