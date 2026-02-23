"""
Editor project model for storing timeline state.
"""

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class EditorProject(Base, TimestampMixin):
    """Editor project model for storing multi-asset timelines."""

    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_video_id = Column(
        UUID(as_uuid=True),
        ForeignKey("videos.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    state = Column(JSONB, nullable=False, default=dict)
    schema_version = Column(SmallInteger, nullable=False, default=2)
    revision = Column(BigInteger, nullable=False, default=0)
    last_opened_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="projects")
    source_video = relationship("Video", foreign_keys=[source_video_id])
    jobs = relationship("EditorJob", back_populates="project")

    def __repr__(self):
        return f"<EditorProject(id={self.id}, name={self.name})>"
