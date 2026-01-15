"""
Strategy model for storing generated marketing strategies.
"""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class Strategy(Base, TimestampMixin):
    """Strategy model for storing AI-generated marketing strategies."""
    
    __tablename__ = "strategies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Strategy inputs
    video_ids = Column(JSONB, nullable=False, default=list)  # List of video UUIDs
    platforms = Column(JSONB, nullable=False, default=list)  # List of platform names
    goals = Column(JSONB, nullable=True, default=list)  # Marketing goals
    niche = Column(String(100), nullable=True)
    
    # Generated strategy
    strategy_data = Column(JSONB, nullable=False, default=dict)
    
    # Versioning
    version = Column(Integer, default=1, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="strategies")
    
    def __repr__(self):
        return f"<Strategy(id={self.id}, platforms={self.platforms})>"
