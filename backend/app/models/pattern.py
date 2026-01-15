"""
Pattern model for storing analyzed video patterns.
"""

from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class Pattern(Base, TimestampMixin):
    """Pattern model for storing video pattern analysis results."""
    
    __tablename__ = "patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Pattern information
    type = Column(String(100), nullable=False, index=True)  # hook_timing, cut_frequency, text_overlays, etc.
    score = Column(Float, default=0.0, nullable=False, index=True)  # 0-100 score
    
    # Pattern data (flexible JSON structure)
    data = Column(JSONB, nullable=False, default=dict)
    
    # Description
    description = Column(String(500), nullable=True)
    
    # Relationships
    video = relationship("Video", back_populates="patterns")
    
    def __repr__(self):
        return f"<Pattern(id={self.id}, type={self.type}, score={self.score})>"
