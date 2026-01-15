"""
Social Account model for storing connected social media accounts.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class SocialAccount(Base, TimestampMixin):
    """Social Account model for OAuth-connected social media accounts."""
    
    __tablename__ = "social_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Platform information
    platform = Column(String(50), nullable=False, index=True)  # instagram, tiktok, youtube, facebook
    platform_user_id = Column(String(255), nullable=False)  # Platform-specific user ID
    username = Column(String(255), nullable=True)
    profile_url = Column(String(500), nullable=True)
    
    # Encrypted OAuth tokens
    access_token_encrypted = Column(String(1000), nullable=False)
    refresh_token_encrypted = Column(String(1000), nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    
    # Sync status
    last_sync = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="social_accounts")
    posts = relationship("Post", back_populates="social_account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SocialAccount(id={self.id}, platform={self.platform}, username={self.username})>"
