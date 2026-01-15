"""
Analytics model for storing post performance metrics.
"""

from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class Analytics(Base, TimestampMixin):
    """Analytics model for tracking post performance."""
    
    __tablename__ = "analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Core metrics
    views = Column(Integer, default=0, nullable=False)
    likes = Column(Integer, default=0, nullable=False)
    comments = Column(Integer, default=0, nullable=False)
    shares = Column(Integer, default=0, nullable=False)
    saves = Column(Integer, default=0, nullable=False)
    
    # Calculated metrics
    engagement_rate = Column(Float, default=0.0, nullable=False)
    
    # Platform-specific metrics (flexible JSON)
    platform_metrics = Column(JSONB, nullable=True, default=dict)
    
    # Historical data for trend analysis
    metrics_history = Column(JSONB, nullable=True, default=list)
    
    # Relationships
    post = relationship("Post", back_populates="analytics")
    
    def __repr__(self):
        return f"<Analytics(id={self.id}, post_id={self.post_id}, engagement_rate={self.engagement_rate})>"
    
    def calculate_engagement_rate(self) -> float:
        """Calculate and update engagement rate."""
        if self.views == 0:
            self.engagement_rate = 0.0
        else:
            total_engagements = self.likes + self.comments + self.shares + self.saves
            self.engagement_rate = (total_engagements / self.views) * 100
        return self.engagement_rate
