"""
Post and publishing schemas for request/response validation.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class PublishRequest(BaseModel):
    """Schema for publish request."""
    video_id: UUID
    platforms: List[str]
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    publish_now: bool = True


class ScheduleRequest(BaseModel):
    """Schema for schedule request."""
    video_id: UUID
    platforms: List[str]
    scheduled_at: datetime
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None


class PostStatus(BaseModel):
    """Post status schema."""
    platform: str
    status: str
    post_id: Optional[str] = None
    error: Optional[str] = None


class PublishResponse(BaseModel):
    """Schema for publish response."""
    task_id: str
    status: str
    posts: List[PostStatus]


class ScheduleResponse(BaseModel):
    """Schema for schedule response."""
    id: UUID
    video_id: UUID
    platforms: List[str]
    scheduled_at: datetime
    status: str


class PostResponse(BaseModel):
    """Schema for post response."""
    id: UUID
    video_id: UUID
    platform: str
    platform_post_id: Optional[str] = None
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    status: str
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    """Schema for post list response."""
    items: List[PostResponse]
    total: int
