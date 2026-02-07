"""merge_heads

Revision ID: 6a66b22ee2e0
Revises: 004, 002_editor_projects
Create Date: 2026-02-07 00:15:09.811319+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a66b22ee2e0'
down_revision: Union[str, None] = ('004', '002_editor_projects')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
