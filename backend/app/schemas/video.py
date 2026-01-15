"""
Video schemas for request/response validation.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class VideoMetadata(BaseModel):
    """Video metadata schema."""
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    codec: Optional[str] = None
    bitrate: Optional[int] = None
    file_size: Optional[int] = None


class VideoCreate(BaseModel):
    """Schema for creating a video record."""
    filename: str
    original_filename: Optional[str] = None
    storage_path: str


class VideoResponse(BaseModel):
    """Schema for video response."""
    id: UUID
    filename: str
    original_filename: Optional[str] = None
    thumbnail_url: Optional[str] = None
    status: str
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoUploadResponse(BaseModel):
    """Schema for video upload response."""
    id: UUID
    filename: str
    status: str
    upload_url: Optional[str] = None
    created_at: datetime


class VideoListResponse(BaseModel):
    """Schema for video list response."""
    items: List[VideoResponse]
    total: int
    page: int
    limit: int


class VideoAnalyzeRequest(BaseModel):
    """Schema for video analysis request."""
    video_id: UUID


class VideoEditRequest(BaseModel):
    """Schema for video editing request."""
    script_id: Optional[UUID] = None
    pattern_ids: Optional[List[UUID]] = None
    platform: str
    output_format: Optional[Dict[str, Any]] = None
