"""
Editor projects endpoints.
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.project import EditorProject
from app.models.user import User
from app.models.video import Video, VideoStatus
from app.models.user_asset import UserAsset
from app.services.storage_service import get_storage_service
from app.services.video_editor import VideoEditorService
from app.services.timeline_renderer import TimelineRenderer

router = APIRouter()
storage = get_storage_service()


class ProjectListItem(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    source_video_id: Optional[str] = None
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


class ProjectExportRequest(BaseModel):
    output_title: Optional[str] = None
    output_settings: Optional[Dict[str, Any]] = None


class ProjectExportResponse(BaseModel):
    output_path: str
    output_url: Optional[str] = None
    output_video_id: Optional[str] = None


def _extract_video_clip_ids(state: Dict[str, Any]) -> List[str]:
    tracks = state.get("tracks") or []
    clip_entries: List[Dict[str, Any]] = []
    for track in tracks:
        for clip in track.get("clips", []) or []:
            if clip.get("type") == "video" and clip.get("sourceId"):
                clip_entries.append({
                    "id": str(clip.get("sourceId")),
                    "start": float(clip.get("startTime") or 0),
                })
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
    try:
        resolved_id = UUID(raw_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid source video id",
        ) from exc
    video = db.query(Video).filter(
        Video.id == resolved_id,
        Video.user_id == current_user.id,
    ).first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source video not found")
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
        try:
            resolved_id = UUID(source_video_id)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid source video id",
            ) from exc
        query = query.filter(EditorProject.source_video_id == resolved_id)
    total = query.count()
    items = query.order_by(EditorProject.updated_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return ProjectListResponse(
        items=[
            ProjectListItem(
                id=str(p.id),
                name=p.name,
                description=p.description,
                source_video_id=str(p.source_video_id) if p.source_video_id else None,
                last_opened_at=p.last_opened_at,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in items
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
    source_video_id = _resolve_source_video_id(payload.source_video_id, db, current_user)
    project = EditorProject(
        id=uuid4(),
        user_id=current_user.id,
        name=name,
        description=(payload.description or "").strip() or None,
        state={},
        source_video_id=source_video_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectResponse(
        id=str(project.id),
        name=project.name,
        description=project.description,
        state=project.state or {},
        source_video_id=str(project.source_video_id) if project.source_video_id else None,
        last_opened_at=project.last_opened_at,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(EditorProject).filter(
        EditorProject.id == UUID(project_id),
        EditorProject.user_id == current_user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    project.last_opened_at = datetime.utcnow()
    db.commit()
    db.refresh(project)

    return ProjectResponse(
        id=str(project.id),
        name=project.name,
        description=project.description,
        state=project.state or {},
        source_video_id=str(project.source_video_id) if project.source_video_id else None,
        last_opened_at=project.last_opened_at,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    payload: ProjectUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(EditorProject).filter(
        EditorProject.id == UUID(project_id),
        EditorProject.user_id == current_user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if payload.name is not None:
        project.name = payload.name.strip() or "Untitled project"
    if payload.description is not None:
        project.description = payload.description.strip() or None
    if payload.state is not None:
        project.state = payload.state
    if payload.source_video_id is not None:
        if payload.source_video_id.strip() == "":
            project.source_video_id = None
        else:
            project.source_video_id = _resolve_source_video_id(payload.source_video_id, db, current_user)

    db.commit()
    db.refresh(project)
    return ProjectResponse(
        id=str(project.id),
        name=project.name,
        description=project.description,
        state=project.state or {},
        source_video_id=str(project.source_video_id) if project.source_video_id else None,
        last_opened_at=project.last_opened_at,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(EditorProject).filter(
        EditorProject.id == UUID(project_id),
        EditorProject.user_id == current_user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"ok": True}


@router.post("/{project_id}/export", response_model=ProjectExportResponse)
async def export_project(
    project_id: str,
    payload: ProjectExportRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.query(EditorProject).filter(
        EditorProject.id == UUID(project_id),
        EditorProject.user_id == current_user.id,
    ).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    clip_ids = _extract_video_clip_ids(project.state or {})
    # Video clips are required for a full timeline, but we allow graphics/audio-only exports
    # (renderer will generate a blank base if needed).

    resolved_ids: List[UUID] = []
    for clip_id in clip_ids:
        try:
            resolved_ids.append(UUID(clip_id))
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid video id in project state: {clip_id}",
            ) from exc

    videos = []
    video_map: Dict[str, Video] = {}
    if resolved_ids:
        videos = db.query(Video).filter(
            Video.id.in_(resolved_ids),
            Video.user_id == current_user.id,
        ).all()
        video_map = {str(v.id): v for v in videos}
        missing = [cid for cid in clip_ids if cid not in video_map]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Missing source videos: {', '.join(missing)}",
            )

    asset_ids = _extract_asset_ids(project.state or {})
    resolved_assets: List[UUID] = []
    for asset_id in asset_ids:
        try:
            resolved_assets.append(UUID(asset_id))
        except Exception:
            continue

    asset_map: Dict[str, UserAsset] = {}
    if resolved_assets:
        assets = db.query(UserAsset).filter(
            UserAsset.id.in_(resolved_assets),
            UserAsset.user_id == current_user.id,
        ).all()
        asset_map = {str(a.id): a for a in assets}

    out_storage_path = f"editor/outputs/{current_user.id}/projects/{project.id}/{uuid4()}_export.mp4"
    out_abs = str(storage.get_write_path(out_storage_path))
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)

    settings = payload.output_settings or {}
    renderer = TimelineRenderer(storage)
    try:
        renderer.render(project.state or {}, video_map, asset_map, out_abs, settings)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

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
