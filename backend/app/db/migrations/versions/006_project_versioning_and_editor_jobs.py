"""Add project schema/revision and editor_jobs table

Revision ID: 006_editor_jobs_v2
Revises: 005_add_project_source_video
Create Date: 2026-02-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "006_editor_jobs_v2"
down_revision: Union[str, None] = "005_add_project_source_video"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


editor_job_type = postgresql.ENUM(
    "export", "derive", name="editorjobtype", create_type=False
)
editor_job_status = postgresql.ENUM(
    "queued",
    "running",
    "completed",
    "failed",
    "canceled",
    name="editorjobstatus",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_project_columns = {
        column["name"] for column in inspector.get_columns("projects")
    }
    if "schema_version" not in existing_project_columns:
        op.add_column(
            "projects",
            sa.Column(
                "schema_version", sa.SmallInteger(), nullable=False, server_default="2"
            ),
        )
    if "revision" not in existing_project_columns:
        op.add_column(
            "projects",
            sa.Column("revision", sa.BigInteger(), nullable=False, server_default="0"),
        )

    inspector = sa.inspect(bind)
    existing_project_indexes = {
        index["name"] for index in inspector.get_indexes("projects")
    }
    if "ix_projects_schema_version" not in existing_project_indexes:
        op.create_index("ix_projects_schema_version", "projects", ["schema_version"])

    op.execute("UPDATE projects SET schema_version = 2 WHERE schema_version IS NULL")
    op.execute("UPDATE projects SET revision = 0 WHERE revision IS NULL")
    op.alter_column("projects", "schema_version", server_default=None)
    op.alter_column("projects", "revision", server_default=None)

    editor_job_type.create(bind, checkfirst=True)
    editor_job_status.create(bind, checkfirst=True)

    if not inspector.has_table("editor_jobs"):
        op.create_table(
            "editor_jobs",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("job_type", editor_job_type, nullable=False),
            sa.Column(
                "status", editor_job_status, nullable=False, server_default="queued"
            ),
            sa.Column("progress", sa.Float(), nullable=False, server_default="0"),
            sa.Column(
                "cancel_requested",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
            sa.Column(
                "payload",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default=sa.text("'{}'::jsonb"),
            ),
            sa.Column(
                "result",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=True,
                server_default=sa.text("'{}'::jsonb"),
            ),
            sa.Column("error_message", sa.String(length=1000), nullable=True),
            sa.Column("celery_task_id", sa.String(length=255), nullable=True),
            sa.Column("started_at", sa.DateTime(), nullable=True),
            sa.Column("finished_at", sa.DateTime(), nullable=True),
            sa.Column(
                "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
            ),
            sa.Column(
                "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
            ),
            sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    inspector = sa.inspect(bind)
    existing_editor_jobs_indexes = {
        index["name"] for index in inspector.get_indexes("editor_jobs")
    }
    if "ix_editor_jobs_project_id" not in existing_editor_jobs_indexes:
        op.create_index("ix_editor_jobs_project_id", "editor_jobs", ["project_id"])
    if "ix_editor_jobs_user_id" not in existing_editor_jobs_indexes:
        op.create_index("ix_editor_jobs_user_id", "editor_jobs", ["user_id"])
    if "ix_editor_jobs_job_type" not in existing_editor_jobs_indexes:
        op.create_index("ix_editor_jobs_job_type", "editor_jobs", ["job_type"])
    if "ix_editor_jobs_status" not in existing_editor_jobs_indexes:
        op.create_index("ix_editor_jobs_status", "editor_jobs", ["status"])
    if "ix_editor_jobs_celery_task_id" not in existing_editor_jobs_indexes:
        op.create_index(
            "ix_editor_jobs_celery_task_id", "editor_jobs", ["celery_task_id"]
        )

    op.alter_column("editor_jobs", "status", server_default=None)
    op.alter_column("editor_jobs", "progress", server_default=None)
    op.alter_column("editor_jobs", "cancel_requested", server_default=None)
    op.alter_column("editor_jobs", "payload", server_default=None)
    op.alter_column("editor_jobs", "result", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("editor_jobs"):
        existing_editor_jobs_indexes = {
            index["name"] for index in inspector.get_indexes("editor_jobs")
        }
        if "ix_editor_jobs_celery_task_id" in existing_editor_jobs_indexes:
            op.drop_index("ix_editor_jobs_celery_task_id", table_name="editor_jobs")
        if "ix_editor_jobs_status" in existing_editor_jobs_indexes:
            op.drop_index("ix_editor_jobs_status", table_name="editor_jobs")
        if "ix_editor_jobs_job_type" in existing_editor_jobs_indexes:
            op.drop_index("ix_editor_jobs_job_type", table_name="editor_jobs")
        if "ix_editor_jobs_user_id" in existing_editor_jobs_indexes:
            op.drop_index("ix_editor_jobs_user_id", table_name="editor_jobs")
        if "ix_editor_jobs_project_id" in existing_editor_jobs_indexes:
            op.drop_index("ix_editor_jobs_project_id", table_name="editor_jobs")
        op.drop_table("editor_jobs")

    editor_job_status.drop(bind, checkfirst=True)
    editor_job_type.drop(bind, checkfirst=True)

    existing_project_indexes = {
        index["name"] for index in inspector.get_indexes("projects")
    }
    if "ix_projects_schema_version" in existing_project_indexes:
        op.drop_index("ix_projects_schema_version", table_name="projects")

    existing_project_columns = {
        column["name"] for column in inspector.get_columns("projects")
    }
    if "revision" in existing_project_columns:
        op.drop_column("projects", "revision")
    if "schema_version" in existing_project_columns:
        op.drop_column("projects", "schema_version")
