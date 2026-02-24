"""Add editor_engine column to projects

Revision ID: 007_project_editor_engine
Revises: 006_editor_jobs_v2
Create Date: 2026-02-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "007_project_editor_engine"
down_revision: Union[str, None] = "006_editor_jobs_v2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_columns = {column["name"] for column in inspector.get_columns("projects")}
    if "editor_engine" not in existing_columns:
        op.add_column(
            "projects",
            sa.Column("editor_engine", sa.String(length=32), nullable=False, server_default="legacy"),
        )

    inspector = sa.inspect(bind)
    existing_indexes = {index["name"] for index in inspector.get_indexes("projects")}
    if "ix_projects_editor_engine" not in existing_indexes:
        op.create_index("ix_projects_editor_engine", "projects", ["editor_engine"])

    op.execute("UPDATE projects SET editor_engine = 'legacy' WHERE editor_engine IS NULL")
    op.alter_column("projects", "editor_engine", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_indexes = {index["name"] for index in inspector.get_indexes("projects")}
    if "ix_projects_editor_engine" in existing_indexes:
        op.drop_index("ix_projects_editor_engine", table_name="projects")

    existing_columns = {column["name"] for column in inspector.get_columns("projects")}
    if "editor_engine" in existing_columns:
        op.drop_column("projects", "editor_engine")
