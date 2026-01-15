"""
Analytics schemas for request/response validation.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime, date
from pydantic import BaseModel
from uuid import UUID


class PlatformMetrics(BaseModel):
    """Platform-specific metrics schema."""
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    engagement_rate: float = 0.0


class AnalyticsResponse(BaseModel):
    """Schema for analytics response."""
    id: UUID
    post_id: UUID
    views: int
    likes: int
    comments: int
    shares: int
    saves: int
    engagement_rate: float
    platform_metrics: Optional[Dict[str, Any]] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoAnalyticsResponse(BaseModel):
    """Schema for video analytics response."""
    video_id: UUID
    platforms: Dict[str, PlatformMetrics]
    pattern_match_score: Optional[float] = None
    updated_at: datetime


class DashboardResponse(BaseModel):
    """Schema for dashboard analytics response."""
    total_views: int = 0
    total_engagement: int = 0
    average_engagement_rate: float = 0.0
    top_performing_videos: List[Dict[str, Any]] = []
    platform_breakdown: Dict[str, PlatformMetrics] = {}
    period_start: date
    period_end: date


class TrendDataPoint(BaseModel):
    """Trend data point schema."""
    date: date
    views: int = 0
    engagement: int = 0


class TrendResponse(BaseModel):
    """Schema for trend response."""
    data: List[TrendDataPoint]
    period_start: date
    period_end: date
