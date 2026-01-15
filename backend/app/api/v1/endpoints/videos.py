"""
Video management endpoints.
"""

from typing import List, Optional
from uuid import UUID, uuid4
import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.video import Video, VideoStatus
from app.workers.video_tasks import analyze_video_patterns, generate_thumbnail, edit_video as edit_video_task

router = APIRouter()

# Allowed video formats
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB


class VideoMetadataResponse(BaseModel):
    """Video metadata schema."""
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    codec: Optional[str] = None
    bitrate: Optional[int] = None
    file_size: Optional[int] = None


class VideoResponse(BaseModel):
    """Video response schema."""
    id: str
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


class VideoListResponse(BaseModel):
    """Video list response schema."""
    items: List[VideoResponse]
    total: int
    page: int
    limit: int


class VideoUploadResponse(BaseModel):
    """Video upload response schema."""
    id: str
    filename: str
    status: str
    created_at: datetime


class TaskResponse(BaseModel):
    """Task response schema."""
    task_id: str
    status: str
    message: Optional[str] = None


class EditRequest(BaseModel):
    """Video edit request schema."""
    script_id: Optional[str] = None
    pattern_ids: Optional[List[str]] = None
    platform: str
    output_format: Optional[dict] = None


def validate_video_file(file: UploadFile) -> None:
    """Validate uploaded video file."""
    # Check file extension
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    
    # Check content type
    if file.content_type and not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a video",
        )


@router.get("", response_model=VideoListResponse)
async def list_videos(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List user's videos with pagination and filtering.
    """
    query = db.query(Video).filter(Video.user_id == current_user.id)
    
    if status_filter:
        try:
            video_status = VideoStatus(status_filter)
            query = query.filter(Video.status == video_status)
        except ValueError:
            pass
    
    total = query.count()
    
    videos = query.order_by(Video.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return VideoListResponse(
        items=[
            VideoResponse(
                id=str(v.id),
                filename=v.filename,
                original_filename=v.original_filename,
                thumbnail_url=v.thumbnail_url,
                status=v.status.value,
                duration=v.duration,
                width=v.width,
                height=v.height,
                file_size=v.file_size,
                tags=v.tags or [],
                created_at=v.created_at,
                updated_at=v.updated_at,
            )
            for v in videos
        ],
        total=total,
        page=page,
        limit=limit,
    )


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a new video file.
    """
    # Validate file
    validate_video_file(file)
    
    # Generate unique filename
    video_id = uuid4()
    ext = os.path.splitext(file.filename or ".mp4")[1].lower()
    storage_filename = f"{video_id}{ext}"
    storage_path = f"videos/{current_user.id}/{storage_filename}"
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Check file size
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)} MB",
        )
    
    # TODO: Upload to Supabase Storage
    # from supabase import create_client
    # supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    # supabase.storage.from_("videos").upload(storage_path, content)
    
    # Create video record
    video = Video(
        id=video_id,
        user_id=current_user.id,
        filename=title or file.filename or storage_filename,
        original_filename=file.filename,
        storage_path=storage_path,
        file_size=file_size,
        status=VideoStatus.UPLOADED,
    )
    
    db.add(video)
    db.commit()
    db.refresh(video)
    
    # Trigger thumbnail generation
    generate_thumbnail.delay(str(video.id), storage_path)
    
    return VideoUploadResponse(
        id=str(video.id),
        filename=video.filename,
        status=video.status.value,
        created_at=video.created_at,
    )


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get video details by ID.
    """
    video = db.query(Video).filter(
        Video.id == UUID(video_id),
        Video.user_id == current_user.id,
    ).first()
    
    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    return VideoResponse(
        id=str(video.id),
        filename=video.filename,
        original_filename=video.original_filename,
        thumbnail_url=video.thumbnail_url,
        status=video.status.value,
        duration=video.duration,
        width=video.width,
        height=video.height,
        file_size=video.file_size,
        tags=video.tags or [],
        created_at=video.created_at,
        updated_at=video.updated_at,
    )


@router.delete("/{video_id}")
async def delete_video(
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a video.
    """
    video = db.query(Video).filter(
        Video.id == UUID(video_id),
        Video.user_id == current_user.id,
    ).first()
    
    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    # TODO: Delete from Supabase Storage
    # supabase.storage.from_("videos").remove([video.storage_path])
    
    db.delete(video)
    db.commit()
    
    return {"message": "Video deleted successfully"}


@router.post("/{video_id}/analyze", response_model=TaskResponse)
async def analyze_video(
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger pattern analysis for a video.
    """
    video = db.query(Video).filter(
        Video.id == UUID(video_id),
        Video.user_id == current_user.id,
    ).first()
    
    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    if video.status == VideoStatus.PROCESSING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video is already being processed",
        )
    
    # Update status
    video.status = VideoStatus.PROCESSING
    db.commit()
    
    # Trigger analysis task
    task = analyze_video_patterns.delay(str(video.id), video.storage_path)
    
    return TaskResponse(
        task_id=task.id,
        status="queued",
        message="Pattern analysis started",
    )


@router.post("/{video_id}/edit", response_model=TaskResponse)
async def edit_video(
    video_id: str,
    request: EditRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Apply patterns/script to create edited video.
    """
    video = db.query(Video).filter(
        Video.id == UUID(video_id),
        Video.user_id == current_user.id,
    ).first()
    
    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    # Trigger editing task
    task = edit_video_task.delay(
        video_id=str(video.id),
        video_path=video.storage_path,
        script_id=request.script_id,
        pattern_ids=request.pattern_ids,
        platform=request.platform,
        output_format=request.output_format,
    )
    
    return TaskResponse(
        task_id=task.id,
        status="queued",
        message="Video editing started",
    )
