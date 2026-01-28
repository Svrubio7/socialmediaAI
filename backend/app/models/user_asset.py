"""
UserAsset model for storing user-uploaded materials (logos, images, etc.).
"""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.models.base import Base, TimestampMixin


class UserAsset(Base, TimestampMixin):
    """User asset (material) for logos, images, watermarks, etc."""

    __tablename__ = "user_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)  # logo, image, watermark
    filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    url = Column(String(500), nullable=True)  # public URL if using storage bucket
    metadata = Column(JSONB, nullable=True, default=dict)

    def __repr__(self):
        return f"<UserAsset(id={self.id}, type={self.type}, filename={self.filename})>"
