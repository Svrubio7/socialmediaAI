"""
Editor projects endpoints.
"""

import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.editor_job import EditorJob, EditorJobStatus, EditorJobType
from app.models.project import EditorProject
from app.models.user import User
from app.models.video import Video, VideoStatus
from app.models.user_asset import UserAsset
from app.services.storage_service import get_storage_service
from app.services.video_editor import VideoEditorService

router = APIRouter()
storage = get_storage_service()
logger = logging.getLogger(__name__)

CURRENT_PROJECT_SCHEMA_VERSION = 2


class ProjectListItem(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    source_video_id: Optional[str] = None
    schema_version: int = CURRENT_PROJECT_SCHEMA_VERSION
    revision: int = 0
    last_opened_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectResponse(ProjectListItem):
    state: Dict[str, Any] = Field(default_factory=dict)


class ProjectListResponse(BaseModel):
    items: List[ProjectListItem]
    total: int
    page: int
    limit: int


class ProjectCreateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    source_video_id: Optional[str] = None


class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    state: Optional[Dict[str, Any]] = None
    source_video_id: Optional[str] = None
    schema_version: Optional[int] = None
    revision: Optional[int] = None


class ProjectExportRequest(BaseModel):
    output_title: Optional[str] = None
    output_settings: Optional[Dict[str, Any]] = None


class ProjectExportResponse(BaseModel):
    output_path: str
    output_url: Optional[str] = None
    output_video_id: Optional[str] = None


class ProjectExportJobRequest(BaseModel):
    output_title: Optional[str] = None
    output_settings: Optional[Dict[str, Any]] = None
    preset: Optional[str] = None
    format: Optional[str] = "mp4"
    include_audio: bool = True


class ProjectExportJobResponse(BaseModel):
    job_id: str
    status: str
    progress: float = 0
    result: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    cancel_requested: bool = False
    created_at: datetime
    updated_at: datetime


class ProjectAssetResponse(BaseModel):
    id: str
    kind: str
    filename: str
    storage_path: str
    url: Optional[str] = None
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProjectAssetListResponse(BaseModel):
    items: List[ProjectAssetResponse]
    total: int


class ProjectAssetRegisterRequest(BaseModel):
    kind: str
    storage_path: str
    filename: Optional[str] = None
    original_filename: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    file_size: Optional[int] = None
    duration: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    codec: Optional[str] = None
    bitrate: Optional[int] = None


class ProjectAssetDeriveRequest(BaseModel):
    operations: List[str] = Field(default_factory=list)
    options: Dict[str, Any] = Field(default_factory=dict)


class ProjectDeriveJobResponse(BaseModel):
    job_id: str
    status: str


def _parse_uuid(raw_id: str, detail: str) -> UUID:
    try:
        return UUID(raw_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        ) from exc


def _state_hash(state: Dict[str, Any]) -> str:
    try:
        payload = json.dumps(state or {}, sort_keys=True, separators=(",", ":"))
    except Exception:
        payload = "{}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _default_project_state(project_name: str) -> Dict[str, Any]:
    return {
        "version": CURRENT_PROJECT_SCHEMA_VERSION,
        "metadata": {"name": project_name},
        "settings": {
            "fps": 30,
            "canvas": {"width": 1080, "height": 1920},
            "background": {"type": "color", "value": "#000000"},
        },
        "currentSceneId": "scene_main",
        "scenes": [
            {
                "id": "scene_main",
                "name": "Scene 1",
                "isMain": True,
                "bookmarks": [],
                "tracks": [],
            }
        ],
        "timelineViewState": {"zoomLevel": 1.0, "scrollLeft": 0, "playheadTime": 0},
        # Compatibility for the current Vue editor implementation.
        "projectName": project_name,
        "tracks": [],
        "transitions": [],
        "selectedClipId": None,
        "playheadTime": 0,
        "timelineZoom": 1,
        "outputSettings": {
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "bitrate": "8M",
        },
    }


def _normalize_project_state(
    raw_state: Optional[Dict[str, Any]], project_name: str
) -> Dict[str, Any]:
    if not isinstance(raw_state, dict):
        return _default_project_state(project_name)

    state = dict(raw_state)
    scenes_raw = state.get("scenes")
    normalized_scenes: List[Dict[str, Any]] = []
    if isinstance(scenes_raw, list):
        for index, scene in enumerate(scenes_raw):
            if not isinstance(scene, dict):
                continue
            scene_id = str(scene.get("id") or f"scene_{index + 1}")
            tracks = scene.get("tracks")
            if not isinstance(tracks, list):
                tracks = []
            bookmarks = scene.get("bookmarks")
            if not isinstance(bookmarks, list):
                bookmarks = []
            normalized_scenes.append(
                {
                    **scene,
                    "id": scene_id,
                    "tracks": tracks,
                    "bookmarks": bookmarks,
                }
            )

    if normalized_scenes:
        current_scene_id = str(
            state.get("currentSceneId")
            or normalized_scenes[0].get("id")
            or "scene_main"
        )
        if not any(scene.get("id") == current_scene_id for scene in normalized_scenes):
            current_scene_id = str(normalized_scenes[0].get("id") or "scene_main")
        active_scene = next(
            (
                scene
                for scene in normalized_scenes
                if scene.get("id") == current_scene_id
            ),
            normalized_scenes[0],
        )
        main_tracks = list(active_scene.get("tracks") or [])
    else:
        tracks_raw = state.get("tracks")
        main_tracks = list(tracks_raw) if isinstance(tracks_raw, list) else []
        current_scene_id = "scene_main"
        normalized_scenes = [
            {
                "id": current_scene_id,
                "name": "Scene 1",
                "isMain": True,
                "bookmarks": [],
                "tracks": main_tracks,
            }
        ]

    metadata = state.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    metadata = {
        **metadata,
        "name": metadata.get("name") or state.get("projectName") or project_name,
    }

    settings = state.get("settings")
    if not isinstance(settings, dict):
        settings = {}
    canvas = settings.get("canvas")
    if not isinstance(canvas, dict):
        canvas = {}
    background = settings.get("background")
    if not isinstance(background, dict):
        background = {}
    settings = {
        **settings,
        "fps": int(settings.get("fps") or 30),
        "canvas": {
            "width": int(canvas.get("width") or 1080),
            "height": int(canvas.get("height") or 1920),
        },
        "background": {
            "type": str(background.get("type") or "color"),
            "value": str(background.get("value") or "#000000"),
        },
    }

    timeline_view_state = state.get("timelineViewState")
    if not isinstance(timeline_view_state, dict):
        timeline_view_state = {}
    timeline_view_state = {
        "zoomLevel": float(
            timeline_view_state.get("zoomLevel") or state.get("timelineZoom") or 1.0
        ),
        "scrollLeft": float(timeline_view_state.get("scrollLeft") or 0),
        "playheadTime": float(
            timeline_view_state.get("playheadTime") or state.get("playheadTime") or 0
        ),
    }

    output_settings = state.get("outputSettings")
    if not isinstance(output_settings, dict):
        output_settings = {}
    output_settings = {
        "width": int(output_settings.get("width") or 1920),
        "height": int(output_settings.get("height") or 1080),
        "fps": int(output_settings.get("fps") or 30),
        "bitrate": str(output_settings.get("bitrate") or "8M"),
    }

    normalized = {
        **state,
        "version": CURRENT_PROJECT_SCHEMA_VERSION,
        "metadata": metadata,
        "settings": settings,
        "currentSceneId": current_scene_id,
        "scenes": normalized_scenes,
        "timelineViewState": timeline_view_state,
        # Compatibility fields:
        "projectName": str(state.get("projectName") or project_name),
        "tracks": main_tracks,
        "transitions": list(state.get("transitions") or []),
        "selectedClipId": state.get("selectedClipId"),
        "playheadTime": float(
            state.get("playheadTime") or timeline_view_state["playheadTime"]
        ),
        "timelineZoom": float(
            state.get("timelineZoom") or timeline_view_state["zoomLevel"]
        ),
        "outputSettings": output_settings,
    }
    return normalized


def _project_or_404(project_id: str, db: Session, current_user: User) -> EditorProject:
    resolved_id = _parse_uuid(project_id, "Invalid project id")
    project = (
        db.query(EditorProject)
        .filter(
            EditorProject.id == resolved_id,
            EditorProject.user_id == current_user.id,
        )
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return project


def _build_project_response(project: EditorProject) -> ProjectResponse:
    normalized_state = _normalize_project_state(project.state or {}, project.name)
    return ProjectResponse(
        id=str(project.id),
        name=project.name,
        description=project.description,
        state=normalized_state,
        source_video_id=(
            str(project.source_video_id) if project.source_video_id else None
        ),
        schema_version=int(project.schema_version or CURRENT_PROJECT_SCHEMA_VERSION),
        revision=int(project.revision or 0),
        last_opened_at=project.last_opened_at,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _build_job_response(job: EditorJob) -> ProjectExportJobResponse:
    return ProjectExportJobResponse(
        job_id=str(job.id),
        status=job.status.value if hasattr(job.status, "value") else str(job.status),
        progress=float(job.progress or 0.0),
        result=job.result or {},
        error_message=job.error_message,
        cancel_requested=bool(job.cancel_requested),
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def _build_asset_response(
    *,
    kind: str,
    asset_id: str,
    filename: str,
    storage_path: str,
    request: Request,
    metadata: Optional[Dict[str, Any]] = None,
    duration: Optional[float] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    file_size: Optional[int] = None,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
) -> ProjectAssetResponse:
    return ProjectAssetResponse(
        id=asset_id,
        kind=kind,
        filename=filename,
        storage_path=storage_path,
        url=storage.build_public_url(storage_path, request),
        duration=duration,
        width=width,
        height=height,
        file_size=file_size,
        metadata=metadata or {},
        created_at=created_at,
        updated_at=updated_at,
    )


def _validate_user_storage_path(
    path: str, user_id: str, prefixes: Optional[List[str]] = None
) -> str:
    rel = path.replace("\\", "/").lstrip("/")
    allowed = prefixes or [
        f"videos/{user_id}/",
        f"thumbnails/{user_id}/",
        f"editor/outputs/{user_id}/",
    ]
    if not any(rel.startswith(prefix) for prefix in allowed):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Storage path is not under the current user's namespace",
        )
    return rel


def _extract_video_clip_ids(state: Dict[str, Any]) -> List[str]:
    tracks = state.get("tracks") or []
    clip_entries: List[Dict[str, Any]] = []
    for track in tracks:
        for clip in track.get("clips", []) or []:
            if clip.get("type") == "video" and clip.get("sourceId"):
                clip_entries.append(
                    {
                        "id": str(clip.get("sourceId")),
                        "start": float(clip.get("startTime") or 0),
                    }
                )
    clip_entries.sort(key=lambda item: item.get("start", 0))
    return [item["id"] for item in clip_entries]


def _extract_asset_ids(state: Dict[str, Any]) -> List[str]:
    tracks = state.get("tracks") or []
    asset_ids: List[str] = []
    for track in tracks:
        for clip in track.get("clips", []) or []:
            if clip.get("type") in {"image", "audio"} and clip.get("sourceId"):
                asset_ids.append(str(clip.get("sourceId")))
    return asset_ids


def _resolve_source_video_id(
    raw_id: Optional[str],
    db: Session,
    current_user: User,
) -> Optional[UUID]:
    if not raw_id:
        return None
    resolved_id = _parse_uuid(raw_id, "Invalid source video id")
    video = (
        db.query(Video)
        .filter(
            Video.id == resolved_id,
            Video.user_id == current_user.id,
        )
        .first()
    )
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source video not found"
        )
    return resolved_id


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    source_video_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(EditorProject).filter(EditorProject.user_id == current_user.id)
    if source_video_id:
        resolved_id = _parse_uuid(source_video_id, "Invalid source video id")
        query = query.filter(EditorProject.source_video_id == resolved_id)
    total = query.count()
    items = (
        query.order_by(EditorProject.updated_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return ProjectListResponse(
        items=[
            ProjectListItem(
                id=str(project.id),
                name=project.name,
                description=project.description,
                source_video_id=(
                    str(project.source_video_id) if project.source_video_id else None
                ),
                schema_version=int(
                    project.schema_version or CURRENT_PROJECT_SCHEMA_VERSION
                ),
                revision=int(project.revision or 0),
                last_opened_at=project.last_opened_at,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
            for project in items
        ],
        total=total,
        page=page,
        limit=limit,
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    raw_name = (payload.name or "").strip()
    if payload.source_video_id and not raw_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Project name is required for video projects",
        )
    name = raw_name or "Untitled project"
    source_video_id = _resolve_source_video_id(
        payload.source_video_id, db, current_user
    )
    initial_state = _default_project_state(name)
    project = EditorProject(
        id=uuid4(),
        user_id=current_user.id,
        name=name,
        description=(payload.description or "").strip() or None,
        state=initial_state,
        schema_version=CURRENT_PROJECT_SCHEMA_VERSION,
        revision=0,
        source_video_id=source_video_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _build_project_response(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _project_or_404(project_id, db, current_user)

    project.last_opened_at = datetime.utcnow()
    db.commit()
    db.refresh(project)

    return _build_project_response(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    payload: ProjectUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _project_or_404(project_id, db, current_user)
    current_revision = int(project.revision or 0)

    if payload.revision is not None and int(payload.revision) != current_revision:
        server_state = _normalize_project_state(project.state or {}, project.name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "revision_conflict",
                "message": "Project has been updated elsewhere.",
                "server_revision": current_revision,
                "server_schema_version": int(
                    project.schema_version or CURRENT_PROJECT_SCHEMA_VERSION
                ),
                "server_state_hash": _state_hash(server_state),
            },
        )

    dirty = False

    if payload.name is not None:
        normalized_name = payload.name.strip() or "Untitled project"
        if normalized_name != project.name:
            project.name = normalized_name
            dirty = True
    if payload.description is not None:
        normalized_description = payload.description.strip() or None
        if normalized_description != project.description:
            project.description = normalized_description
            dirty = True
    if payload.state is not None:
        normalized_state = _normalize_project_state(payload.state, project.name)
        requested_schema = int(
            payload.schema_version
            or normalized_state.get("version")
            or CURRENT_PROJECT_SCHEMA_VERSION
        )
        if requested_schema > CURRENT_PROJECT_SCHEMA_VERSION:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "version_unsupported",
                    "message": (
                        f"Schema version {requested_schema} is newer than supported "
                        f"server version {CURRENT_PROJECT_SCHEMA_VERSION}."
                    ),
                },
            )
        project.state = normalized_state
        project.schema_version = requested_schema
        dirty = True
    elif payload.schema_version is not None:
        requested_schema = int(payload.schema_version)
        if requested_schema > CURRENT_PROJECT_SCHEMA_VERSION:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "version_unsupported",
                    "message": (
                        f"Schema version {requested_schema} is newer than supported "
                        f"server version {CURRENT_PROJECT_SCHEMA_VERSION}."
                    ),
                },
            )
        if requested_schema != int(
            project.schema_version or CURRENT_PROJECT_SCHEMA_VERSION
        ):
            project.schema_version = requested_schema
            dirty = True
    if payload.source_video_id is not None:
        if payload.source_video_id.strip() == "":
            if project.source_video_id is not None:
                project.source_video_id = None
                dirty = True
        else:
            resolved_source_video_id = _resolve_source_video_id(
                payload.source_video_id, db, current_user
            )
            if resolved_source_video_id != project.source_video_id:
                project.source_video_id = resolved_source_video_id
                dirty = True

    if dirty:
        project.revision = current_revision + 1

    db.commit()
    db.refresh(project)
    return _build_project_response(project)


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _project_or_404(project_id, db, current_user)
    db.delete(project)
    db.commit()
    return {"ok": True}


@router.get("/{project_id}/assets", response_model=ProjectAssetListResponse)
async def list_project_assets(
    project_id: str,
    request: Request,
    kind: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _project_or_404(project_id, db, current_user)

    if kind is not None:
        kind = kind.strip().lower()
    if kind not in {None, "video", "image", "audio"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid asset kind filter"
        )

    items: List[ProjectAssetResponse] = []

    if kind in {None, "video"}:
        videos = (
            db.query(Video)
            .filter(Video.user_id == current_user.id)
            .order_by(Video.updated_at.desc())
            .all()
        )
        for video in videos:
            items.append(
                _build_asset_response(
                    kind="video",
                    asset_id=str(video.id),
                    filename=video.filename,
                    storage_path=video.storage_path,
                    request=request,
                    duration=video.duration,
                    width=video.width,
                    height=video.height,
                    file_size=video.file_size,
                    metadata=dict(video.video_metadata or {}),
                    created_at=video.created_at,
                    updated_at=video.updated_at,
                )
            )

    if kind in {None, "image", "audio"}:
        assets = (
            db.query(UserAsset)
            .filter(UserAsset.user_id == current_user.id)
            .order_by(UserAsset.updated_at.desc())
            .all()
        )
        for asset in assets:
            normalized_kind = "audio" if asset.type == "audio" else "image"
            if kind is not None and normalized_kind != kind:
                continue
            items.append(
                _build_asset_response(
                    kind=normalized_kind,
                    asset_id=str(asset.id),
                    filename=asset.filename,
                    storage_path=asset.storage_path,
                    request=request,
                    metadata=dict(asset.asset_metadata or {}),
                    created_at=asset.created_at,
                    updated_at=asset.updated_at,
                )
            )

    items.sort(
        key=lambda item: item.updated_at or item.created_at or datetime.min,
        reverse=True,
    )
    return ProjectAssetListResponse(items=items, total=len(items))


@router.post(
    "/{project_id}/assets/register",
    response_model=ProjectAssetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_project_asset(
    project_id: str,
    payload: ProjectAssetRegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _project_or_404(project_id, db, current_user)
    kind = (payload.kind or "").strip().lower()
    if kind not in {"video", "image", "audio"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid asset kind"
        )

    user_id = str(current_user.supabase_user_id or current_user.id)
    metadata = dict(payload.metadata or {})
    filename = (
        payload.filename or payload.original_filename or Path(payload.storage_path).name
    )

    if kind == "video":
        storage_path = _validate_user_storage_path(
            payload.storage_path, user_id, [f"videos/{user_id}/"]
        )
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
            video_metadata=metadata,
            status=VideoStatus.UPLOADED,
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        return _build_asset_response(
            kind="video",
            asset_id=str(video.id),
            filename=video.filename,
            storage_path=video.storage_path,
            request=request,
            duration=video.duration,
            width=video.width,
            height=video.height,
            file_size=video.file_size,
            metadata=dict(video.video_metadata or {}),
            created_at=video.created_at,
            updated_at=video.updated_at,
        )

    allowed_prefixes = [
        f"branding/{user_id}/",
        f"audio/{user_id}/",
        f"videos/{user_id}/",
        f"thumbnails/{user_id}/",
        f"editor/outputs/{user_id}/",
    ]
    storage_path = _validate_user_storage_path(
        payload.storage_path, user_id, allowed_prefixes
    )
    asset = UserAsset(
        id=uuid4(),
        user_id=current_user.id,
        type=kind,
        filename=filename,
        storage_path=storage_path,
        asset_metadata=metadata,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return _build_asset_response(
        kind=kind,
        asset_id=str(asset.id),
        filename=asset.filename,
        storage_path=asset.storage_path,
        request=request,
        metadata=dict(asset.asset_metadata or {}),
        created_at=asset.created_at,
        updated_at=asset.updated_at,
    )


@router.post(
    "/{project_id}/assets/{asset_id}/derive",
    response_model=ProjectDeriveJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def derive_project_asset(
    project_id: str,
    asset_id: str,
    payload: ProjectAssetDeriveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _project_or_404(project_id, db, current_user)
    resolved_asset_id = _parse_uuid(asset_id, "Invalid asset id")
    video = (
        db.query(Video)
        .filter(Video.id == resolved_asset_id, Video.user_id == current_user.id)
        .first()
    )
    asset = (
        None
        if video
        else db.query(UserAsset)
        .filter(UserAsset.id == resolved_asset_id, UserAsset.user_id == current_user.id)
        .first()
    )
    if not video and not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found"
        )

    job = EditorJob(
        id=uuid4(),
        project_id=project.id,
        user_id=current_user.id,
        job_type=EditorJobType.DERIVE,
        status=EditorJobStatus.QUEUED,
        payload={
            "asset_id": str(resolved_asset_id),
            "operations": payload.operations,
            "options": payload.options,
        },
        progress=0.0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return ProjectDeriveJobResponse(job_id=str(job.id), status=job.status.value)


@router.post(
    "/{project_id}/exports",
    response_model=ProjectExportJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_project_export_job(
    project_id: str,
    payload: ProjectExportJobRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _project_or_404(project_id, db, current_user)
    job = EditorJob(
        id=uuid4(),
        project_id=project.id,
        user_id=current_user.id,
        job_type=EditorJobType.EXPORT,
        status=EditorJobStatus.QUEUED,
        payload={
            "output_title": payload.output_title,
            "output_settings": payload.output_settings or {},
            "preset": payload.preset,
            "format": payload.format or "mp4",
            "include_audio": payload.include_audio,
        },
        progress=0.0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    try:
        from app.workers.video_tasks import render_project_export_job

        task = render_project_export_job.delay(str(job.id))
        job.celery_task_id = str(task.id)
        db.commit()
        db.refresh(job)
    except Exception as exc:
        logger.exception("Failed to enqueue export job %s: %s", job.id, exc)
        job.status = EditorJobStatus.FAILED
        job.error_message = "Failed to queue export job"
        job.finished_at = datetime.utcnow()
        db.commit()
        db.refresh(job)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Background worker unavailable. Please ensure Celery is running.",
        ) from exc
    return _build_job_response(job)


@router.get("/{project_id}/exports/{job_id}", response_model=ProjectExportJobResponse)
async def get_project_export_job(
    project_id: str,
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _project_or_404(project_id, db, current_user)
    resolved_job_id = _parse_uuid(job_id, "Invalid job id")
    job = (
        db.query(EditorJob)
        .filter(
            EditorJob.id == resolved_job_id,
            EditorJob.project_id == project.id,
            EditorJob.user_id == current_user.id,
            EditorJob.job_type == EditorJobType.EXPORT,
        )
        .first()
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found"
        )
    return _build_job_response(job)


@router.post(
    "/{project_id}/exports/{job_id}/cancel", response_model=ProjectExportJobResponse
)
async def cancel_project_export_job(
    project_id: str,
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _project_or_404(project_id, db, current_user)
    resolved_job_id = _parse_uuid(job_id, "Invalid job id")
    job = (
        db.query(EditorJob)
        .filter(
            EditorJob.id == resolved_job_id,
            EditorJob.project_id == project.id,
            EditorJob.user_id == current_user.id,
            EditorJob.job_type == EditorJobType.EXPORT,
        )
        .first()
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found"
        )
    job.cancel_requested = True
    if job.status == EditorJobStatus.QUEUED:
        job.status = EditorJobStatus.CANCELED
        job.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    return _build_job_response(job)


@router.post("/{project_id}/export", response_model=ProjectExportResponse)
async def export_project(
    project_id: str,
    payload: ProjectExportRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _project_or_404(project_id, db, current_user)
    project_state = _normalize_project_state(project.state or {}, project.name)

    clip_ids = _extract_video_clip_ids(project_state)
    # Video clips are required for a full timeline, but we allow graphics/audio-only exports
    # (renderer will generate a blank base if needed).

    resolved_ids: List[UUID] = []
    for clip_id in clip_ids:
        resolved_ids.append(
            _parse_uuid(clip_id, f"Invalid video id in project state: {clip_id}")
        )

    videos = []
    video_map: Dict[str, Video] = {}
    if resolved_ids:
        videos = (
            db.query(Video)
            .filter(
                Video.id.in_(resolved_ids),
                Video.user_id == current_user.id,
            )
            .all()
        )
        video_map = {str(v.id): v for v in videos}
        missing = [cid for cid in clip_ids if cid not in video_map]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Missing source videos: {', '.join(missing)}",
            )

    asset_ids = _extract_asset_ids(project_state)
    resolved_assets: List[UUID] = []
    for asset_id in asset_ids:
        try:
            resolved_assets.append(UUID(asset_id))
        except Exception:
            continue

    asset_map: Dict[str, UserAsset] = {}
    if resolved_assets:
        assets = (
            db.query(UserAsset)
            .filter(
                UserAsset.id.in_(resolved_assets),
                UserAsset.user_id == current_user.id,
            )
            .all()
        )
        asset_map = {str(a.id): a for a in assets}

    out_storage_path = (
        f"editor/outputs/{current_user.id}/projects/{project.id}/{uuid4()}_export.mp4"
    )
    out_abs = str(storage.get_write_path(out_storage_path))
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)

    settings = payload.output_settings or {}
    try:
        from app.services.timeline_renderer import TimelineRenderer
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Project export dependencies are unavailable on the API runtime. "
                "Install rendering extras (Pillow/FFmpeg) or run export via worker."
            ),
        ) from exc

    renderer = TimelineRenderer(storage)
    try:
        renderer.render(project_state, video_map, asset_map, out_abs, settings)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    svc = VideoEditorService()
    info = await svc.get_video_info(out_abs)
    file_size = os.path.getsize(out_abs)

    storage.finalize_write(out_storage_path, out_abs, content_type="video/mp4")
    out_url = storage.build_public_url(out_storage_path, request)

    output_title = payload.output_title or f"{project.name} - export"
    video = Video(
        id=uuid4(),
        user_id=current_user.id,
        filename=output_title,
        original_filename=output_title,
        storage_path=out_storage_path,
        file_size=file_size,
        duration=info.get("duration"),
        width=info.get("width"),
        height=info.get("height"),
        fps=info.get("fps"),
        codec=info.get("codec"),
        bitrate=info.get("bitrate"),
        status=VideoStatus.UPLOADED,
        tags=["project-export"],
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    return ProjectExportResponse(
        output_path=out_storage_path,
        output_url=out_url,
        output_video_id=str(video.id),
    )
