"""
Video management endpoints.
"""

from typing import List, Optional
from uuid import UUID, uuid4
import os
import json
import logging
import subprocess
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Request, status
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.video import Video, VideoStatus
from app.services.storage_service import LocalStorageService
from app.workers.video_tasks import analyze_video_patterns, edit_video as edit_video_task

router = APIRouter()
logger = logging.getLogger(__name__)
storage = LocalStorageService()

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
    storage_path: Optional[str] = None
    video_url: Optional[str] = None
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


def _parse_fps(value: Optional[str]) -> Optional[float]:
    if not value:
        return None
    if "/" in value:
        left, right = value.split("/", 1)
        try:
            num = float(left)
            den = float(right)
            return (num / den) if den else None
        except ValueError:
            return None
    try:
        return float(value)
    except ValueError:
        return None


def _extract_video_metadata(video_path: str) -> dict:
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
    except Exception:
        return {}

    streams = data.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
    format_info = data.get("format", {})
    return {
        "duration": float(format_info.get("duration")) if format_info.get("duration") else None,
        "width": int(video_stream.get("width")) if video_stream.get("width") else None,
        "height": int(video_stream.get("height")) if video_stream.get("height") else None,
        "fps": _parse_fps(video_stream.get("r_frame_rate")),
        "codec": video_stream.get("codec_name"),
        "bitrate": int(format_info.get("bit_rate")) if format_info.get("bit_rate") else None,
    }


def _generate_thumbnail(video_path: str, user_id: str, video_id: str) -> Optional[str]:
    thumb_storage_path = f"thumbnails/{user_id}/{video_id}.jpg"
    thumb_abs = storage.absolute_path(thumb_storage_path)
    thumb_abs.parent.mkdir(parents=True, exist_ok=True)
    # Try a few seek positions for short clips.
    for seek in ("1", "0.1", "0"):
        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            seek,
            "-i",
            video_path,
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(thumb_abs),
        ]
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            return thumb_storage_path
        except Exception:
            continue
    logger.warning("Thumbnail generation failed for %s", video_id)
    return None


def _thumbnail_url(video: Video, request: Request) -> Optional[str]:
    meta = video.video_metadata or {}
    thumb_path = meta.get("thumbnail_storage_path")
    if thumb_path:
        return storage.build_public_url(thumb_path, request)
    return video.thumbnail_url


def _video_url(video: Video, request: Request) -> Optional[str]:
    return storage.build_public_url(video.storage_path, request) if video.storage_path else None


def _absolute_video_path(video: Video) -> str:
    path = storage.resolve_for_processing(video.storage_path)
    return str(Path(path))


def _queue_task(task_callable, *args, **kwargs):
    try:
        return task_callable.delay(*args, **kwargs)
    except Exception as exc:
        logger.exception("Failed to queue task %s: %s", getattr(task_callable, "name", "unknown"), exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Background worker unavailable. Please ensure Redis/Celery are running.",
        )


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
    request: Request,
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
                storage_path=v.storage_path,
                video_url=_video_url(v, request),
                thumbnail_url=_thumbnail_url(v, request),
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
    request: Request,
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
    
    # Persist to local storage
    stored_file = storage.save_bytes(storage_path, content)

    # Extract metadata from uploaded file
    metadata = _extract_video_metadata(str(stored_file))

    # Generate thumbnail synchronously (fast, avoids queue dependency for upload flow)
    thumb_storage_path = _generate_thumbnail(
        video_path=str(stored_file),
        user_id=str(current_user.id),
        video_id=str(video_id),
    )
    thumbnail_url = storage.build_public_url(thumb_storage_path, request) if thumb_storage_path else None
    
    # Create video record
    video = Video(
        id=video_id,
        user_id=current_user.id,
        filename=title or file.filename or storage_filename,
        original_filename=file.filename,
        storage_path=storage_path,
        thumbnail_url=thumbnail_url,
        file_size=file_size,
        duration=metadata.get("duration"),
        width=metadata.get("width"),
        height=metadata.get("height"),
        fps=metadata.get("fps"),
        codec=metadata.get("codec"),
        bitrate=metadata.get("bitrate"),
        video_metadata={"thumbnail_storage_path": thumb_storage_path} if thumb_storage_path else {},
        status=VideoStatus.UPLOADED,
    )
    
    db.add(video)
    db.commit()
    db.refresh(video)
    
    return VideoUploadResponse(
        id=str(video.id),
        filename=video.filename,
        status=video.status.value,
        created_at=video.created_at,
    )


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    request: Request,
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
        storage_path=video.storage_path,
        video_url=_video_url(video, request),
        thumbnail_url=_thumbnail_url(video, request),
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

    # Remove underlying files from local storage.
    storage.delete(video.storage_path)
    thumb_path = (video.video_metadata or {}).get("thumbnail_storage_path")
    if isinstance(thumb_path, str) and thumb_path:
        storage.delete(thumb_path)
    
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

    video_path = _absolute_video_path(video)
    if not Path(video_path).exists():
        video.status = VideoStatus.FAILED
        video.error_message = "Video file not found in storage"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video file missing from storage",
        )

    # Trigger analysis task
    task = _queue_task(analyze_video_patterns, str(video.id), video_path)
    
    return TaskResponse(
        task_id=str(task.id),
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
    video_path = _absolute_video_path(video)
    if not Path(video_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video file missing from storage",
        )

    task = _queue_task(
        edit_video_task,
        video_id=str(video.id),
        video_path=video_path,
        script_id=request.script_id,
        pattern_ids=request.pattern_ids,
        platform=request.platform,
        output_format=request.output_format,
    )
    
    return TaskResponse(
        task_id=str(task.id),
        status="queued",
        message="Video editing started",
    )
