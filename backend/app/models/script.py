"""
Script model for storing generated video scripts.
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class Script(Base, TimestampMixin):
    """Script model for storing AI-generated video scripts."""
    
    __tablename__ = "scripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Script inputs
    concept = Column(String(500), nullable=False)
    platform = Column(String(50), nullable=False)
    target_duration = Column(Integer, nullable=False)  # in seconds
    pattern_ids = Column(JSONB, nullable=True, default=list)  # List of pattern UUIDs
    
    # Generated script
    script_data = Column(JSONB, nullable=False, default=dict)
    actual_duration = Column(Float, nullable=True)  # Calculated total duration
    
    # Versioning
    version = Column(Integer, default=1, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="scripts")
    
    def __repr__(self):
        return f"<Script(id={self.id}, concept={self.concept[:50]}...)>"
