"""
Video model for storing uploaded video metadata.
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum

from app.models.base import Base, TimestampMixin


class VideoStatus(str, enum.Enum):
    """Video processing status."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class Video(Base, TimestampMixin):
    """Video model for storing video files and metadata."""
    
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=True)
    storage_path = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    
    # Video metadata
    duration = Column(Float, nullable=True)  # in seconds
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    fps = Column(Float, nullable=True)
    codec = Column(String(50), nullable=True)
    bitrate = Column(Integer, nullable=True)
    
    # Status
    status = Column(SQLEnum(VideoStatus), default=VideoStatus.UPLOADED, nullable=False, index=True)
    error_message = Column(String(500), nullable=True)
    
    # Additional metadata (renamed from 'metadata' to avoid SQLAlchemy reserved word conflict)
    video_metadata = Column(JSONB, nullable=True, default=dict)
    tags = Column(JSONB, nullable=True, default=list)
    
    # Relationships
    user = relationship("User", back_populates="videos")
    patterns = relationship("Pattern", back_populates="video", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="video", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Video(id={self.id}, filename={self.filename}, status={self.status})>"
