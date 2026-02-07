"""
Editor project model for storing timeline state.
"""

from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class EditorProject(Base, TimestampMixin):
    """Editor project model for storing multi-asset timelines."""

    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    state = Column(JSONB, nullable=False, default=dict)
    last_opened_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="projects")

    def __repr__(self):
        return f"<EditorProject(id={self.id}, name={self.name})>"
