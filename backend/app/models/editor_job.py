"""
Editor background jobs model for export/derivative workflows.
"""

from __future__ import annotations

import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class EditorJobType(str, enum.Enum):
    EXPORT = "export"
    DERIVE = "derive"


class EditorJobStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class EditorJob(Base, TimestampMixin):
    """Tracks long-running editor jobs."""

    __tablename__ = "editor_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    job_type = Column(SQLEnum(EditorJobType), nullable=False, index=True)
    status = Column(
        SQLEnum(EditorJobStatus),
        nullable=False,
        default=EditorJobStatus.QUEUED,
        index=True,
    )
    progress = Column(Float, nullable=False, default=0.0)
    cancel_requested = Column(Boolean, nullable=False, default=False)

    payload = Column(JSONB, nullable=False, default=dict)
    result = Column(JSONB, nullable=True, default=dict)
    error_message = Column(String(1000), nullable=True)
    celery_task_id = Column(String(255), nullable=True, index=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    project = relationship("EditorProject", back_populates="jobs")
    user = relationship("User", back_populates="editor_jobs")

    def __repr__(self):
        return (
            f"<EditorJob(id={self.id}, project_id={self.project_id}, "
            f"type={self.job_type}, status={self.status})>"
        )
