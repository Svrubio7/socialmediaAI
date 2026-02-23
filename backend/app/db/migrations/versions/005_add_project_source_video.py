"""Add source video id to editor projects

Revision ID: 005_add_project_source_video
Revises: 6a66b22ee2e0
Create Date: 2026-02-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "005_add_project_source_video"
down_revision: Union[str, None] = "6a66b22ee2e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_columns = {column["name"] for column in inspector.get_columns("projects")}
    if "source_video_id" not in existing_columns:
        op.add_column(
            "projects",
            sa.Column("source_video_id", postgresql.UUID(as_uuid=True), nullable=True),
        )

    inspector = sa.inspect(bind)
    existing_indexes = {index["name"] for index in inspector.get_indexes("projects")}
    if "ix_projects_source_video_id" not in existing_indexes:
        op.create_index("ix_projects_source_video_id", "projects", ["source_video_id"])

    existing_foreign_keys = {
        foreign_key["name"]
        for foreign_key in inspector.get_foreign_keys("projects")
        if foreign_key.get("name")
    }
    if "fk_projects_source_video_id" not in existing_foreign_keys:
        op.create_foreign_key(
            "fk_projects_source_video_id",
            "projects",
            "videos",
            ["source_video_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_foreign_keys = {
        foreign_key["name"]
        for foreign_key in inspector.get_foreign_keys("projects")
        if foreign_key.get("name")
    }
    if "fk_projects_source_video_id" in existing_foreign_keys:
        op.drop_constraint("fk_projects_source_video_id", "projects", type_="foreignkey")

    existing_indexes = {index["name"] for index in inspector.get_indexes("projects")}
    if "ix_projects_source_video_id" in existing_indexes:
        op.drop_index("ix_projects_source_video_id", table_name="projects")

    existing_columns = {column["name"] for column in inspector.get_columns("projects")}
    if "source_video_id" in existing_columns:
        op.drop_column("projects", "source_video_id")
