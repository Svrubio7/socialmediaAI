"""Add edit_templates table for reusable edit styles

Revision ID: 004
Revises: 003
Create Date: 2026-01-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "edit_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("style_spec", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_edit_templates_user_id", "edit_templates", ["user_id"])
    op.create_index("ix_edit_templates_name", "edit_templates", ["name"])


def downgrade() -> None:
    op.drop_index("ix_edit_templates_name", table_name="edit_templates")
    op.drop_index("ix_edit_templates_user_id", table_name="edit_templates")
    op.drop_table("edit_templates")
