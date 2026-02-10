"""Add source video id to editor projects

Revision ID: 005_add_project_source_video
Revises: 20260207_001509_6a66b22ee2e0_merge_heads
Create Date: 2026-02-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "005_add_project_source_video"
down_revision: Union[str, None] = "20260207_001509_6a66b22ee2e0_merge_heads"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("source_video_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_projects_source_video_id", "projects", ["source_video_id"])
    op.create_foreign_key(
        "fk_projects_source_video_id",
        "projects",
        "videos",
        ["source_video_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_projects_source_video_id", "projects", type_="foreignkey")
    op.drop_index("ix_projects_source_video_id", table_name="projects")
    op.drop_column("projects", "source_video_id")
