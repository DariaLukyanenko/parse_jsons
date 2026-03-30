"""empty

Revision ID: e852f8731fd5
Revises: b50665aba7d8
Create Date: 2025-12-01 15:21:12.969738

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e852f8731fd5'
down_revision: Union[str, None] = 'b50665aba7d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
