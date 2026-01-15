"""
Post model for storing published and scheduled posts.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum

from app.models.base import Base, TimestampMixin


class PostStatus(str, enum.Enum):
    """Post status enum."""
    SCHEDULED = "scheduled"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Post(Base, TimestampMixin):
    """Post model for published and scheduled content."""
    
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    social_account_id = Column(UUID(as_uuid=True), ForeignKey("social_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Platform information
    platform = Column(String(50), nullable=False, index=True)
    platform_post_id = Column(String(255), nullable=True)  # Post ID on the platform
    
    # Content
    caption = Column(String(2200), nullable=True)  # Max caption length
    hashtags = Column(JSONB, nullable=True, default=list)
    
    # Status
    status = Column(SQLEnum(PostStatus), default=PostStatus.SCHEDULED, nullable=False, index=True)
    error_message = Column(String(500), nullable=True)
    
    # Timing
    scheduled_at = Column(DateTime, nullable=True, index=True)
    published_at = Column(DateTime, nullable=True)
    
    # Task tracking
    task_id = Column(String(255), nullable=True)  # Celery task ID
    
    # Relationships
    video = relationship("Video", back_populates="posts")
    social_account = relationship("SocialAccount", back_populates="posts")
    analytics = relationship("Analytics", back_populates="post", cascade="all, delete-orphan", uselist=False)
    
    def __repr__(self):
        return f"<Post(id={self.id}, platform={self.platform}, status={self.status})>"
