"""
Analytics endpoints.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime, date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.video import Video
from app.models.post import Post, PostStatus as PostStatusEnum
from app.models.analytics import Analytics
from app.models.pattern import Pattern

router = APIRouter()


class PlatformMetrics(BaseModel):
    """Platform-specific metrics schema."""
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    engagement_rate: float = 0.0


class VideoAnalyticsResponse(BaseModel):
    """Video analytics response schema."""
    video_id: str
    platforms: Dict[str, PlatformMetrics]
    pattern_match_score: Optional[float] = None
    total_views: int = 0
    total_engagement: int = 0
    average_engagement_rate: float = 0.0
    updated_at: datetime


class DashboardResponse(BaseModel):
    """Dashboard analytics response schema."""
    video_count: int = 0
    pattern_count: int = 0
    post_count: int = 0
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
    """Trend response schema."""
    data: List[TrendDataPoint]
    period_start: date
    period_end: date


class TopVideoResponse(BaseModel):
    """Top performing video response."""
    id: str
    filename: str
    platform: str
    views: int
    likes: int
    engagement_rate: float
    published_at: Optional[datetime] = None


class TopPerformersResponse(BaseModel):
    """Top performers response."""
    items: List[TopVideoResponse]
    total: int


@router.get("/videos/{video_id}", response_model=VideoAnalyticsResponse)
async def get_video_analytics(
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get performance analytics for a specific video.
    """
    # Verify video ownership
    video = db.query(Video).filter(
        Video.id == UUID(video_id),
        Video.user_id == current_user.id,
    ).first()
    
    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    # Get all posts for this video
    posts = db.query(Post).filter(Post.video_id == UUID(video_id)).all()
    
    # Aggregate metrics by platform
    platforms: Dict[str, PlatformMetrics] = {}
    total_views = 0
    total_engagement = 0
    
    for post in posts:
        if post.analytics:
            analytics = post.analytics
            platform_metrics = PlatformMetrics(
                views=analytics.views,
                likes=analytics.likes,
                comments=analytics.comments,
                shares=analytics.shares,
                saves=analytics.saves,
                engagement_rate=analytics.engagement_rate,
            )
            platforms[post.platform] = platform_metrics
            total_views += analytics.views
            total_engagement += (analytics.likes + analytics.comments + analytics.shares)
    
    # Calculate average engagement rate
    avg_engagement = (total_engagement / total_views * 100) if total_views > 0 else 0.0
    
    # Get pattern score
    patterns = db.query(Pattern).filter(Pattern.video_id == UUID(video_id)).all()
    pattern_score = None
    if patterns:
        pattern_score = sum(p.score for p in patterns) / len(patterns)
    
    return VideoAnalyticsResponse(
        video_id=video_id,
        platforms=platforms,
        pattern_match_score=pattern_score,
        total_views=total_views,
        total_engagement=total_engagement,
        average_engagement_rate=avg_engagement,
        updated_at=datetime.utcnow(),
    )


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    platform: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get aggregated analytics dashboard data.
    """
    # Default to last 30 days
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Build base query
    query = db.query(Analytics).join(Post).join(Video).filter(
        Video.user_id == current_user.id,
        Post.published_at >= datetime.combine(start_date, datetime.min.time()),
        Post.published_at <= datetime.combine(end_date, datetime.max.time()),
    )
    
    if platform:
        query = query.filter(Post.platform == platform)
    
    analytics_list = query.all()
    
    # Counts for dashboard stat cards
    video_count = db.query(Video).filter(Video.user_id == current_user.id).count()
    pattern_count = (
        db.query(Pattern.id)
        .join(Video, Pattern.video_id == Video.id)
        .filter(Video.user_id == current_user.id)
        .count()
    )
    post_count = (
        db.query(Post.id)
        .join(Video, Post.video_id == Video.id)
        .filter(Video.user_id == current_user.id)
        .count()
    )
    
    # Aggregate totals
    total_views = sum(a.views for a in analytics_list)
    total_engagement = sum(a.likes + a.comments + a.shares for a in analytics_list)
    avg_engagement = (total_engagement / total_views * 100) if total_views > 0 else 0.0
    
    # Group by platform
    platform_breakdown: Dict[str, PlatformMetrics] = {}
    for analytics in analytics_list:
        post = analytics.post
        if post.platform not in platform_breakdown:
            platform_breakdown[post.platform] = PlatformMetrics()
        
        metrics = platform_breakdown[post.platform]
        platform_breakdown[post.platform] = PlatformMetrics(
            views=metrics.views + analytics.views,
            likes=metrics.likes + analytics.likes,
            comments=metrics.comments + analytics.comments,
            shares=metrics.shares + analytics.shares,
            saves=metrics.saves + analytics.saves,
        )
    
    # Calculate engagement rates per platform
    for platform_name, metrics in platform_breakdown.items():
        if metrics.views > 0:
            eng_rate = (metrics.likes + metrics.comments + metrics.shares) / metrics.views * 100
            platform_breakdown[platform_name] = PlatformMetrics(
                views=metrics.views,
                likes=metrics.likes,
                comments=metrics.comments,
                shares=metrics.shares,
                saves=metrics.saves,
                engagement_rate=eng_rate,
            )
    
    # Get top performing videos
    top_videos = []
    video_analytics = db.query(
        Video.id,
        Video.filename,
        func.sum(Analytics.views).label('total_views'),
        func.sum(Analytics.likes).label('total_likes'),
    ).join(Post, Post.video_id == Video.id).join(Analytics).filter(
        Video.user_id == current_user.id,
    ).group_by(Video.id, Video.filename).order_by(
        func.sum(Analytics.views).desc()
    ).limit(5).all()
    
    for v in video_analytics:
        top_videos.append({
            "id": str(v.id),
            "filename": v.filename,
            "views": v.total_views or 0,
            "likes": v.total_likes or 0,
        })
    
    return DashboardResponse(
        video_count=video_count,
        pattern_count=pattern_count,
        post_count=post_count,
        total_views=total_views,
        total_engagement=total_engagement,
        average_engagement_rate=avg_engagement,
        top_performing_videos=top_videos,
        platform_breakdown=platform_breakdown,
        period_start=start_date,
        period_end=end_date,
    )


@router.get("/trends", response_model=TrendResponse)
async def get_analytics_trends(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    platform: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get analytics trends over time.
    """
    # Default to last 30 days
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Build data points for each day
    data: List[TrendDataPoint] = []
    current = start_date
    
    while current <= end_date:
        # Query analytics for this day
        query = db.query(
            func.sum(Analytics.views).label('views'),
            func.sum(Analytics.likes + Analytics.comments + Analytics.shares).label('engagement'),
        ).join(Post).join(Video).filter(
            Video.user_id == current_user.id,
            func.date(Post.published_at) == current,
        )
        
        if platform:
            query = query.filter(Post.platform == platform)
        
        result = query.first()
        
        data.append(TrendDataPoint(
            date=current,
            views=result.views or 0 if result else 0,
            engagement=result.engagement or 0 if result else 0,
        ))
        
        current += timedelta(days=1)
    
    return TrendResponse(
        data=data,
        period_start=start_date,
        period_end=end_date,
    )


@router.get("/top-performers", response_model=TopPerformersResponse)
async def get_top_performers(
    limit: int = Query(10, ge=1, le=50),
    platform: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get top performing videos.
    """
    query = db.query(
        Post.id,
        Video.id.label('video_id'),
        Video.filename,
        Post.platform,
        Analytics.views,
        Analytics.likes,
        Analytics.engagement_rate,
        Post.published_at,
    ).join(Video, Post.video_id == Video.id).join(Analytics).filter(
        Video.user_id == current_user.id,
        Post.status == PostStatusEnum.PUBLISHED,
    )
    
    if platform:
        query = query.filter(Post.platform == platform)
    
    results = query.order_by(Analytics.views.desc()).limit(limit).all()
    
    items = [
        TopVideoResponse(
            id=str(r.video_id),
            filename=r.filename,
            platform=r.platform,
            views=r.views or 0,
            likes=r.likes or 0,
            engagement_rate=r.engagement_rate or 0.0,
            published_at=r.published_at,
        )
        for r in results
    ]
    
    return TopPerformersResponse(
        items=items,
        total=len(items),
    )
