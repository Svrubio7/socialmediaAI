"""
EditTemplate model for reusable edit styles (cuts, overlays, layers, etc.).
"""

from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.models.base import Base, TimestampMixin


class EditTemplate(Base, TimestampMixin):
    """Edit template: reusable edit style applied to raw footage."""

    __tablename__ = "edit_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    style_spec = Column(JSONB, nullable=False, default=dict)  # cuts, overlays, layers, pacing, etc.

    def __repr__(self):
        return f"<EditTemplate(id={self.id}, name={self.name})>"
