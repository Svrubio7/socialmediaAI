"""
Publishing and scheduling endpoints.
"""

from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from datetime import datetime, timezone
import logging
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.video import Video
from app.models.social_account import SocialAccount
from app.models.post import Post, PostStatus as PostStatusEnum
from app.workers.publish_tasks import publish_to_platform

router = APIRouter()
logger = logging.getLogger(__name__)


class PublishRequest(BaseModel):
    """Publish request schema."""
    video_id: str
    platforms: List[str]
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    publish_now: bool = True


class ScheduleRequest(BaseModel):
    """Schedule request schema."""
    video_id: str
    platforms: List[str]
    scheduled_at: datetime
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None


class PostStatusResponse(BaseModel):
    """Post status schema."""
    platform: str
    status: str
    post_id: Optional[str] = None
    error: Optional[str] = None


class PublishResponse(BaseModel):
    """Publish response schema."""
    task_ids: List[str]
    status: str
    posts: List[PostStatusResponse]


class ScheduleResponse(BaseModel):
    """Schedule response schema."""
    id: str
    video_id: str
    platforms: List[str]
    scheduled_at: datetime
    status: str


class PostResponse(BaseModel):
    """Post response schema."""
    id: str
    video_id: str
    video_title: Optional[str] = None
    platform: str
    platform_post_id: Optional[str] = None
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    status: str
    error_message: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    """Post list response schema."""
    items: List[PostResponse]
    total: int


def _queue_publish_task(**kwargs):
    """Queue publishing task and return task object or a 503-safe HTTP error."""
    try:
        return publish_to_platform.delay(**kwargs)
    except Exception as exc:
        logger.exception("Failed to queue publish task: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Background worker unavailable. Please ensure Redis/Celery are running.",
        )


@router.post("/publish", response_model=PublishResponse)
async def publish_video(
    request: PublishRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Publish video to social media platforms.
    """
    # Validate video ownership
    video = db.query(Video).filter(
        Video.id == UUID(request.video_id),
        Video.user_id == current_user.id,
    ).first()
    
    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    # Get connected accounts for requested platforms
    accounts = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id,
        SocialAccount.platform.in_(request.platforms),
    ).all()
    
    if not accounts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No connected accounts found for requested platforms",
        )
    
    account_map = {acc.platform: acc for acc in accounts}
    
    # Create posts and queue tasks
    posts = []
    task_ids = []
    
    for platform in request.platforms:
        account = account_map.get(platform)
        if not account:
            posts.append(PostStatusResponse(
                platform=platform,
                status="error",
                error=f"No connected {platform} account",
            ))
            continue
        
        # Create post record
        post = Post(
            id=uuid4(),
            video_id=video.id,
            social_account_id=account.id,
            platform=platform,
            caption=request.caption,
            hashtags=request.hashtags,
            status=PostStatusEnum.PUBLISHING if request.publish_now else PostStatusEnum.SCHEDULED,
        )
        
        db.add(post)
        db.flush()
        
        if request.publish_now:
            # Queue publishing task
            task = _queue_publish_task(
                post_id=str(post.id),
                video_path=video.storage_path,
                platform=platform,
                caption=request.caption,
                hashtags=request.hashtags,
            )
            post.task_id = task.id
            task_ids.append(task.id)
        
        posts.append(PostStatusResponse(
            platform=platform,
            status="queued" if request.publish_now else "scheduled",
        ))
    
    db.commit()
    
    return PublishResponse(
        task_ids=task_ids,
        status="publishing" if request.publish_now else "scheduled",
        posts=posts,
    )


@router.post("/schedule", response_model=ScheduleResponse)
async def schedule_post(
    request: ScheduleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Schedule a post for future publication.
    """
    # Validate video ownership
    video = db.query(Video).filter(
        Video.id == UUID(request.video_id),
        Video.user_id == current_user.id,
    ).first()
    
    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    # Validate scheduled time is in the future
    scheduled_at = request.scheduled_at
    if scheduled_at.tzinfo is not None and scheduled_at.utcoffset() is not None:
        now_utc = datetime.now(timezone.utc)
        if scheduled_at.astimezone(timezone.utc) <= now_utc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scheduled time must be in the future",
            )
        # Store as naive UTC to match DB DateTime schema.
        scheduled_at_db = scheduled_at.astimezone(timezone.utc).replace(tzinfo=None)
    else:
        if scheduled_at <= datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scheduled time must be in the future",
            )
        scheduled_at_db = scheduled_at

    # Get connected accounts
    accounts = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id,
        SocialAccount.platform.in_(request.platforms),
    ).all()
    
    if not accounts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No connected accounts found for requested platforms",
        )
    
    account_map = {acc.platform: acc for acc in accounts}
    
    # Create scheduled posts
    first_post_id = None
    for platform in request.platforms:
        account = account_map.get(platform)
        if not account:
            continue
        
        post = Post(
            id=uuid4(),
            video_id=video.id,
            social_account_id=account.id,
            platform=platform,
            caption=request.caption,
            hashtags=request.hashtags,
            status=PostStatusEnum.SCHEDULED,
            scheduled_at=scheduled_at_db,
        )
        
        db.add(post)
        if first_post_id is None:
            first_post_id = post.id
    
    db.commit()
    
    return ScheduleResponse(
        id=str(first_post_id),
        video_id=request.video_id,
        platforms=request.platforms,
        scheduled_at=scheduled_at_db,
        status="scheduled",
    )


@router.get("", response_model=PostListResponse)
async def list_posts(
    status_filter: Optional[str] = Query(None, alias="status"),
    platform: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List published and scheduled posts.
    """
    query = db.query(Post).join(Video).options(joinedload(Post.video)).filter(Video.user_id == current_user.id)
    
    if status_filter:
        try:
            post_status = PostStatusEnum(status_filter)
            query = query.filter(Post.status == post_status)
        except ValueError:
            pass
    
    if platform:
        query = query.filter(Post.platform == platform)
    
    total = query.count()
    posts = query.order_by(Post.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return PostListResponse(
        items=[
            PostResponse(
                id=str(p.id),
                video_id=str(p.video_id),
                video_title=getattr(p.video, "filename", None) if p.video else None,
                platform=p.platform,
                platform_post_id=p.platform_post_id,
                caption=p.caption,
                hashtags=p.hashtags,
                status=p.status.value,
                error_message=p.error_message,
                scheduled_at=p.scheduled_at,
                published_at=p.published_at,
                created_at=p.created_at,
            )
            for p in posts
        ],
        total=total,
    )


@router.get("/scheduled", response_model=PostListResponse)
async def list_scheduled_posts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List scheduled posts.
    """
    query = (
        db.query(Post)
        .join(Video)
        .options(joinedload(Post.video))
        .filter(
            Video.user_id == current_user.id,
            Post.status == PostStatusEnum.SCHEDULED,
        )
    )
    total = query.count()
    posts = query.order_by(Post.scheduled_at.asc()).all()
    
    return PostListResponse(
        items=[
            PostResponse(
                id=str(p.id),
                video_id=str(p.video_id),
                video_title=getattr(p.video, "filename", None) if p.video else None,
                platform=p.platform,
                platform_post_id=p.platform_post_id,
                caption=p.caption,
                hashtags=p.hashtags,
                status=p.status.value,
                error_message=p.error_message,
                scheduled_at=p.scheduled_at,
                published_at=p.published_at,
                created_at=p.created_at,
            )
            for p in posts
        ],
        total=total,
    )


@router.delete("/scheduled/{post_id}")
async def cancel_scheduled_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cancel a scheduled post.
    """
    post = db.query(Post).join(Video).filter(
        Post.id == UUID(post_id),
        Video.user_id == current_user.id,
        Post.status == PostStatusEnum.SCHEDULED,
    ).first()
    
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found",
        )
    
    post.status = PostStatusEnum.CANCELLED
    db.commit()
    
    return {"message": "Scheduled post cancelled"}


@router.post("/{post_id}/retry")
async def retry_failed_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retry a failed publication.
    """
    post = db.query(Post).join(Video).filter(
        Post.id == UUID(post_id),
        Video.user_id == current_user.id,
        Post.status == PostStatusEnum.FAILED,
    ).first()
    
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed post not found",
        )
    
    # Get video
    video = db.query(Video).filter(Video.id == post.video_id).first()
    
    # Update status and queue retry
    post.status = PostStatusEnum.PUBLISHING
    post.error_message = None
    
    task = _queue_publish_task(
        post_id=str(post.id),
        video_path=video.storage_path,
        platform=post.platform,
        caption=post.caption,
        hashtags=post.hashtags,
    )
    post.task_id = task.id
    
    db.commit()
    
    return {
        "message": "Post retry queued",
        "task_id": task.id,
    }
