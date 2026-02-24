"""
Video management endpoints.
"""

from typing import List, Optional, Tuple
from uuid import UUID, uuid4
import os
import json
import logging
import subprocess
import asyncio
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Request, status, Header
from fastapi.responses import Response
from fastapi.responses import RedirectResponse
from fastapi.responses import StreamingResponse
import httpx
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_current_user_optional
from app.core.security import decode_token, verify_supabase_token
from app.core.config import settings
from app.models.user import User
from app.models.video import Video, VideoStatus
from app.services.storage_service import get_storage_service
from app.workers.video_tasks import analyze_video_patterns, edit_video as edit_video_task

router = APIRouter()
logger = logging.getLogger(__name__)
storage = get_storage_service()

# Allowed video formats
ALLOWED_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".m4v",
    ".avi",
    ".mkv",
    ".webm",
    ".mpeg",
    ".mpg",
    ".ogv",
    ".3gp",
    ".3g2",
    ".ts",
}
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
    thumbnail_storage_path: Optional[str] = None
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


class VideoRegisterRequest(BaseModel):
    """Register a video that already exists in storage (direct upload)."""
    storage_path: str
    thumbnail_storage_path: Optional[str] = None
    filename: Optional[str] = None
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    codec: Optional[str] = None
    bitrate: Optional[int] = None


class TaskResponse(BaseModel):
    """Task response schema."""
    task_id: str
    status: str
    message: Optional[str] = None


class VideoMediaUrlsRequest(BaseModel):
    """Batch request for short-lived media playback URLs."""
    video_ids: List[str]
    include_video: bool = True
    include_thumbnail: bool = True


class VideoMediaUrlItem(BaseModel):
    """Media URLs resolved for a specific video."""
    id: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class VideoMediaUrlsResponse(BaseModel):
    """Batch media URL response."""
    items: List[VideoMediaUrlItem]
    expires_in: Optional[int] = None


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


def _extract_stream_codecs(video_path: str) -> dict:
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_streams",
        video_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
    except Exception:
        return {"video": None, "audio": None}

    streams = data.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})
    return {
        "video": video_stream.get("codec_name"),
        "audio": audio_stream.get("codec_name"),
    }


def _normalize_video_for_playback(video_path: str) -> str:
    """
    Ensure uploads are browser-playable:
    - For H.264/AAC (or no audio) MP4/M4V/MOV, apply faststart (moov atom).
    - Otherwise transcode to H.264/AAC with faststart.
    Falls back to original file on failure.
    """
    ext = Path(video_path).suffix.lower()
    if ext not in {".mp4", ".m4v", ".mov"}:
        return video_path

    codecs = _extract_stream_codecs(video_path)
    video_codec = (codecs.get("video") or "").lower()
    audio_codec = (codecs.get("audio") or "").lower()
    needs_reencode = video_codec != "h264" or (audio_codec not in {"", "aac", "mp3"})

    tmp_path = str(Path(video_path).with_suffix(f".normalized{ext}"))
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-map",
        "0:v",
        "-map",
        "0:a?",
    ]
    if needs_reencode:
        cmd += ["-c:v", "libx264", "-preset", "fast", "-c:a", "aac"]
    else:
        cmd += ["-c", "copy"]
    cmd += ["-movflags", "+faststart", tmp_path]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        Path(tmp_path).replace(video_path)
    except Exception as exc:
        logger.warning("Playback normalization failed for %s: %s", video_path, exc)
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass
        return video_path

    return video_path


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


def _thumbnail_storage_path(video: Video) -> Optional[str]:
    meta = video.video_metadata or {}
    thumb_path = meta.get("thumbnail_storage_path")
    if isinstance(thumb_path, str) and thumb_path:
        return thumb_path
    return None


def _thumbnail_url(video: Video, request: Request) -> Optional[str]:
    thumb_path = _thumbnail_storage_path(video)
    if not thumb_path:
        return video.thumbnail_url

    if (settings.STORAGE_BACKEND or "").lower() == "supabase":
        # Avoid expensive N signed-url calls in list/get; proxy each image on demand.
        base = str(request.base_url).rstrip("/")
        return f"{base}{settings.API_V1_STR}/videos/{video.id}/thumbnail"

    signed = storage.build_public_url(thumb_path, request)
    if signed:
        return signed
    return video.thumbnail_url


def _video_url(video: Video, request: Request) -> Optional[str]:
    if not video.storage_path:
        return None
    if (settings.STORAGE_BACKEND or "").lower() == "supabase":
        base = str(request.base_url).rstrip("/")
        return f"{base}{settings.API_V1_STR}/videos/{video.id}/stream"
    return storage.build_public_url(video.storage_path, request)


def _signed_url_ttl_seconds() -> Optional[int]:
    if (settings.STORAGE_BACKEND or "").lower() != "supabase":
        return None
    if not bool(settings.SUPABASE_STORAGE_PRIVATE):
        return None
    ttl = int(settings.SUPABASE_STORAGE_SIGNED_URL_TTL or 3600)
    return max(1, ttl)


def _is_http_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


async def _head_remote(url: str, range_header: Optional[str]) -> Response:
    headers: dict = {}
    if range_header:
        headers["Range"] = range_header

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.head(url, headers=headers, follow_redirects=True)

    if resp.status_code not in (200, 206):
        raise HTTPException(status_code=resp.status_code, detail="Failed to fetch video headers")

    response = Response(status_code=resp.status_code)
    for header in ("content-length", "content-range", "accept-ranges", "content-type"):
        if header in resp.headers:
            response.headers[header] = resp.headers[header]
    return response


async def _stream_remote(url: str, range_header: Optional[str]) -> StreamingResponse:
    headers: dict = {}
    if range_header:
        headers["Range"] = range_header

    timeout = httpx.Timeout(connect=10.0, read=120.0, write=30.0, pool=30.0)
    client = httpx.AsyncClient(timeout=timeout)
    request = client.build_request("GET", url, headers=headers)
    resp = await client.send(request, stream=True, follow_redirects=True)

    if resp.status_code not in (200, 206):
        await resp.aclose()
        await client.aclose()
        raise HTTPException(status_code=resp.status_code, detail="Failed to fetch video stream")

    async def iterator():
        try:
            async for chunk in resp.aiter_raw():
                if chunk:
                    yield chunk
        finally:
            await resp.aclose()
            await client.aclose()

    response = StreamingResponse(
        iterator(),
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type") or "application/octet-stream",
    )
    for header in (
        "content-length",
        "content-range",
        "accept-ranges",
        "cache-control",
        "etag",
        "last-modified",
    ):
        if header in resp.headers:
            response.headers[header] = resp.headers[header]
    return response


def _absolute_video_path(video: Video) -> str:
    path = storage.resolve_for_processing(video.storage_path)
    return str(Path(path))


def _validate_user_storage_path(path: str, user_id: str, prefixes: Optional[List[str]] = None) -> str:
    rel = path.replace("\\", "/").lstrip("/")
    allowed = prefixes or [
        f"videos/{user_id}/",
        f"thumbnails/{user_id}/",
        f"editor/outputs/{user_id}/",
        f"editor/assets/{user_id}/",
    ]
    if not any(rel.startswith(prefix) for prefix in allowed):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Storage path is not under the current user's namespace",
        )
    return rel


def _queue_task(task_callable, *args, **kwargs):
    try:
        return task_callable.delay(*args, **kwargs)
    except Exception as exc:
        logger.exception("Failed to queue task %s: %s", getattr(task_callable, "name", "unknown"), exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Background worker unavailable. Please ensure Redis/Celery are running.",
        )


def _storage_exists_soft(path: str) -> Optional[bool]:
    try:
        return storage.exists(path)
    except Exception as exc:
        logger.warning("Storage existence check failed for %s: %s", path, exc)
        return None


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
                thumbnail_storage_path=(v.video_metadata or {}).get("thumbnail_storage_path"),
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


@router.api_route("/{video_id}/stream", methods=["GET", "HEAD"])
async def stream_video(
    video_id: str,
    request: Request,
    range_header: Optional[str] = Header(None, alias="Range"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    token: Optional[str] = None,
):
    user = current_user
    if user is None and token:
        payload = decode_token(token) or verify_supabase_token(token)
        if payload:
            user = await get_current_user(db=db, token_payload=payload)

    if user is None and not settings.DEBUG:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    query = db.query(Video).filter(Video.id == UUID(video_id))
    if user is not None:
        query = query.filter(Video.user_id == user.id)
    video = query.first()

    if video is None or not video.storage_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    url = storage.build_public_url(video.storage_path, request)
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video file not available")

    # For Supabase-backed storage, avoid proxying large media through the API process.
    # Redirecting lets the browser stream directly from the signed URL and reduces stutter.
    if (settings.STORAGE_BACKEND or "").lower() == "supabase" and _is_http_url(url):
        return RedirectResponse(url=url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    if request.method == "HEAD":
        return await _head_remote(url, range_header)
    return await _stream_remote(url, range_header)


@router.api_route("/{video_id}/thumbnail", methods=["GET", "HEAD"])
async def stream_thumbnail(
    video_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    token: Optional[str] = None,
):
    user = current_user
    if user is None and token:
        payload = decode_token(token) or verify_supabase_token(token)
        if payload:
            user = await get_current_user(db=db, token_payload=payload)

    if user is None and not settings.DEBUG:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    query = db.query(Video).filter(Video.id == UUID(video_id))
    if user is not None:
        query = query.filter(Video.user_id == user.id)
    video = query.first()

    if video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    thumb_path = _thumbnail_storage_path(video)
    source_url: Optional[str] = None
    if thumb_path:
        source_url = storage.build_public_url(thumb_path, request)
    if not source_url and video.thumbnail_url:
        source_url = video.thumbnail_url

    if not source_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thumbnail not found")

    if request.method == "HEAD":
        return await _head_remote(source_url, None)
    return await _stream_remote(source_url, None)


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
    if (settings.STORAGE_BACKEND or "").lower() == "supabase":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Direct uploads are handled by Supabase Storage. Use /videos/register instead.",
        )
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

    # Normalize for browser playback (faststart / optional transcode)
    normalized_path = _normalize_video_for_playback(str(stored_file))

    # Extract metadata from uploaded file
    metadata = _extract_video_metadata(normalized_path)

    # Generate thumbnail synchronously (fast, avoids queue dependency for upload flow)
    thumb_storage_path = _generate_thumbnail(
        video_path=normalized_path,
        user_id=str(current_user.id),
        video_id=str(video_id),
    )
    thumbnail_url = storage.build_public_url(thumb_storage_path, request) if thumb_storage_path else None

    # Update file size after normalization
    try:
        file_size = Path(normalized_path).stat().st_size
    except Exception:
        file_size = len(content)
    
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


@router.post("/register", response_model=VideoUploadResponse)
async def register_video(
    payload: VideoRegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Register a video that was uploaded directly to storage (Supabase).
    """
    user_id = str(current_user.supabase_user_id or current_user.id)
    storage_path = _validate_user_storage_path(
        payload.storage_path,
        user_id,
        [f"videos/{user_id}/", f"editor/outputs/{user_id}/", f"editor/assets/{user_id}/"],
    )
    thumb_path = None
    if payload.thumbnail_storage_path:
        thumb_path = _validate_user_storage_path(
            payload.thumbnail_storage_path,
            user_id,
            [f"thumbnails/{user_id}/", f"videos/{user_id}/", f"editor/assets/{user_id}/"],
        )

    # Optional existence check to avoid broken records
    exists = _storage_exists_soft(storage_path)
    if exists is False:
        if (settings.STORAGE_BACKEND or "").lower() != "supabase":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video file not found in storage")
        # Supabase storage list checks can be blocked by RLS or bucket policies; don't fail registration.
        logger.warning("Video %s not found via storage API; continuing registration", storage_path)

    filename = payload.filename or payload.original_filename or Path(storage_path).name
    video = Video(
        id=uuid4(),
        user_id=current_user.id,
        filename=filename,
        original_filename=payload.original_filename or payload.filename,
        storage_path=storage_path,
        file_size=payload.file_size,
        duration=payload.duration,
        width=payload.width,
        height=payload.height,
        fps=payload.fps,
        codec=payload.codec,
        bitrate=payload.bitrate,
        video_metadata={"thumbnail_storage_path": thumb_path} if thumb_path else {},
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


@router.post("/media-urls", response_model=VideoMediaUrlsResponse)
async def get_video_media_urls(
    payload: VideoMediaUrlsRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Resolve short-lived playback URLs in batch.

    This is the primary media-access path for web clients:
    - avoids persisting expiring URLs in editor state
    - avoids exposing full user JWT in media query strings
    - enables direct browser/CDN playback without backend video proxy on each frame
    """
    raw_ids = payload.video_ids or []
    if not raw_ids:
        return VideoMediaUrlsResponse(items=[], expires_in=_signed_url_ttl_seconds())

    if len(raw_ids) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum of 200 video IDs per request",
        )

    ordered_ids: List[str] = []
    parsed_ids: List[UUID] = []
    seen: set[str] = set()
    for raw_id in raw_ids:
        try:
            parsed = UUID(raw_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid video id: {raw_id}",
            )
        canonical = str(parsed)
        if canonical in seen:
            continue
        parsed_ids.append(parsed)
        ordered_ids.append(canonical)
        seen.add(canonical)

    videos = db.query(Video).filter(
        Video.user_id == current_user.id,
        Video.id.in_(parsed_ids),
    ).all()
    by_id = {str(video.id): video for video in videos}

    items = [VideoMediaUrlItem(id=video_id) for video_id in ordered_ids]
    jobs: List[Tuple[str, int, str]] = []

    for index, video_id in enumerate(ordered_ids):
        video = by_id.get(video_id)
        if not video:
            continue
        if payload.include_video and video.storage_path:
            jobs.append(("video", index, video.storage_path))
        if payload.include_thumbnail:
            thumb_path = _thumbnail_storage_path(video)
            if thumb_path:
                jobs.append(("thumbnail", index, thumb_path))
            elif video.thumbnail_url and _is_http_url(video.thumbnail_url):
                items[index].thumbnail_url = video.thumbnail_url

    if jobs:
        semaphore = asyncio.Semaphore(12)

        async def resolve_one(kind: str, index: int, path: str):
            async with semaphore:
                try:
                    resolved = await asyncio.to_thread(storage.build_public_url, path, request)
                except Exception as exc:
                    logger.warning("Failed to resolve %s media URL for %s: %s", kind, path, exc)
                    resolved = None
                return kind, index, resolved

        results = await asyncio.gather(*(resolve_one(kind, idx, path) for kind, idx, path in jobs))
        for kind, index, resolved in results:
            if kind == "video":
                items[index].video_url = resolved
            else:
                items[index].thumbnail_url = resolved

    # Keep only videos user can access. Missing IDs are silently dropped to simplify client sync flows.
    items = [item for item in items if item.id in by_id]

    return VideoMediaUrlsResponse(
        items=items,
        expires_in=_signed_url_ttl_seconds(),
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

    # Backfill metadata if missing (older uploads or failed probe).
    # For Supabase-backed storage this can be slow because it downloads the full asset,
    # which makes page reloads appear to "hang". Keep this best-effort for local storage only.
    if (video.duration is None or video.width is None or video.height is None) and video.storage_path:
        storage_backend = (settings.STORAGE_BACKEND or "").lower()
        if storage_backend == "local":
            try:
                abs_path = _absolute_video_path(video)
                if Path(abs_path).exists():
                    meta = _extract_video_metadata(abs_path)
                    if meta.get("duration") is not None:
                        video.duration = meta.get("duration")
                    if meta.get("width") is not None:
                        video.width = meta.get("width")
                    if meta.get("height") is not None:
                        video.height = meta.get("height")
                    if meta.get("bitrate") is not None:
                        video.bitrate = meta.get("bitrate")
                    if meta.get("codec") is not None:
                        video.codec = meta.get("codec")
                    if meta.get("fps") is not None:
                        video.fps = meta.get("fps")
                    db.commit()
            except Exception:
                # Best-effort: keep existing values if probing fails.
                db.rollback()
    
    return VideoResponse(
        id=str(video.id),
        filename=video.filename,
        original_filename=video.original_filename,
        storage_path=video.storage_path,
        thumbnail_storage_path=(video.video_metadata or {}).get("thumbnail_storage_path"),
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

    if (settings.STORAGE_BACKEND or "").lower() == "supabase":
        if not storage.exists(video.storage_path):
            video.status = VideoStatus.FAILED
            video.error_message = "Video file not found in storage"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video file missing from storage",
            )
        task = _queue_task(analyze_video_patterns, str(video.id), video.storage_path)
    else:
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
    if (settings.STORAGE_BACKEND or "").lower() == "supabase":
        if not storage.exists(video.storage_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video file missing from storage",
            )
        video_path = video.storage_path
    else:
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
