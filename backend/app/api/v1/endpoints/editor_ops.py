"""
Editor foundation ops API. Dispatches to VideoEditorService.
Used by UI and MCP. All ops require video_id and user auth.
"""

import os
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.video import Video, VideoStatus
from app.services.storage_service import LocalStorageService
from app.services.video_editor import VideoEditorService

router = APIRouter()
storage = LocalStorageService()


class EditorOpRequest(BaseModel):
    """Request to run a single editor op."""

    op: str
    params: Dict[str, Any] = Field(default_factory=dict)
    save_to_library: bool = True
    output_title: Optional[str] = None


class EditorOpResponse(BaseModel):
    """Response from editor op execution."""

    op: str
    output_path: Optional[str] = None
    output_url: Optional[str] = None
    output_video_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


def _get_video(db: Session, video_id: str, user_id: UUID) -> Video:
    v = db.query(Video).filter(Video.id == UUID(video_id), Video.user_id == user_id).first()
    if not v:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    return v


def _resolve_existing_file(storage_path: str) -> str:
    path = storage.resolve_for_processing(storage_path)
    if not os.path.exists(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video file missing from storage")
    return path


@router.post("/{video_id}/op", response_model=EditorOpResponse)
async def execute_editor_op(
    video_id: str,
    body: EditorOpRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Execute a single editor foundation op on a video.
    Supports timeline/transform/export operations used by the editor workspace.
    """
    source_video = _get_video(db, video_id, current_user.id)
    input_path = _resolve_existing_file(source_video.storage_path)
    svc = VideoEditorService()
    p = body.params

    out_storage_path = f"editor/outputs/{current_user.id}/{video_id}/{uuid4()}_{body.op}.mp4"
    out_abs = str(storage.absolute_path(out_storage_path))
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)
    out_url = storage.build_public_url(out_storage_path)

    async def finalize_output(op: str) -> EditorOpResponse:
        if not os.path.exists(out_abs):
            return EditorOpResponse(op=op, error="Operation completed but output file was not produced")

        output_video_id: Optional[str] = None
        if body.save_to_library:
            info = await svc.get_video_info(out_abs)
            edited = Video(
                id=uuid4(),
                user_id=current_user.id,
                filename=(body.output_title or f"{source_video.filename} - {op}"),
                original_filename=source_video.original_filename or source_video.filename,
                storage_path=out_storage_path,
                file_size=os.path.getsize(out_abs),
                duration=info.get("duration"),
                width=info.get("width"),
                height=info.get("height"),
                fps=info.get("fps"),
                codec=info.get("codec"),
                bitrate=info.get("bitrate"),
                status=VideoStatus.UPLOADED,
                tags=["edited", op],
            )
            db.add(edited)
            db.commit()
            db.refresh(edited)
            output_video_id = str(edited.id)

        return EditorOpResponse(
            op=op,
            output_path=out_storage_path,
            output_url=out_url,
            output_video_id=output_video_id,
            result={"saved_to_library": body.save_to_library},
        )

    try:
        if body.op == "video_info":
            info = await svc.get_video_info(input_path)
            return EditorOpResponse(op=body.op, result=info)

        if body.op == "trim_clip":
            await svc.trim_clip(input_path, float(p["start"]), float(p["end"]), out_abs)
            return await finalize_output(body.op)

        if body.op == "clip_out":
            await svc.clip_out(input_path, float(p["start"]), float(p["end"]), out_abs)
            return await finalize_output(body.op)

        if body.op == "duplicate_clip":
            await svc.duplicate_clip(input_path, out_abs)
            return await finalize_output(body.op)

        if body.op == "set_clip_speed":
            await svc.set_clip_speed(input_path, float(p.get("speed", 1.0)), out_abs)
            return await finalize_output(body.op)

        if body.op == "reverse_clip":
            await svc.reverse_clip(input_path, out_abs)
            return await finalize_output(body.op)

        if body.op == "crop_clip":
            await svc.crop_clip(
                input_path,
                int(p["x"]),
                int(p["y"]),
                int(p["width"]),
                int(p["height"]),
                out_abs,
            )
            return await finalize_output(body.op)

        if body.op == "rotate_clip":
            await svc.rotate_clip(input_path, float(p.get("degrees", 90)), out_abs)
            return await finalize_output(body.op)

        if body.op == "mirror_clip":
            await svc.mirror_clip(input_path, bool(p.get("horizontal", True)), out_abs)
            return await finalize_output(body.op)

        if body.op == "set_canvas_size":
            await svc.set_canvas_size(input_path, int(p["width"]), int(p["height"]), out_abs)
            return await finalize_output(body.op)

        if body.op == "adjust_color":
            await svc.adjust_color(
                input_path=input_path,
                brightness=float(p.get("brightness", 0.0)),
                contrast=float(p.get("contrast", 1.0)),
                saturation=float(p.get("saturation", 1.0)),
                gamma=float(p.get("gamma", 1.0)),
                output_path=out_abs,
            )
            return await finalize_output(body.op)

        if body.op == "fade_in_out":
            await svc.fade_in_out(
                input_path=input_path,
                fade_in=float(p.get("fade_in", 0.3)),
                fade_out=float(p.get("fade_out", 0.3)),
                output_path=out_abs,
            )
            return await finalize_output(body.op)

        if body.op == "freeze_frame":
            await svc.freeze_frame(
                input_path=input_path,
                at_time=float(p.get("at_time", 0)),
                duration=float(p.get("duration", 1.0)),
                output_path=out_abs,
            )
            return await finalize_output(body.op)

        if body.op == "add_text_overlay":
            await svc.add_text_overlay(
                input_path=input_path,
                text=str(p.get("text", "")),
                position=str(p.get("position", "center")),
                start_time=float(p.get("start_time", 0)),
                end_time=float(p["end_time"]) if p.get("end_time") is not None else None,
                output_path=out_abs,
            )
            return await finalize_output(body.op)

        if body.op == "insert_image":
            await svc.insert_image(
                input_path=input_path,
                image_path=_resolve_existing_file(str(p["image_path"])),
                at_time=float(p.get("at_time", 0)),
                duration=float(p.get("duration", 2.0)),
                position=str(p.get("position", "center")),
                output_path=out_abs,
            )
            return await finalize_output(body.op)

        if body.op == "insert_audio":
            await svc.insert_audio(
                video_path=input_path,
                audio_path=_resolve_existing_file(str(p["audio_path"])),
                at_time=float(p.get("at_time", 0)),
                volume=float(p.get("volume", 1.0)),
                output_path=out_abs,
            )
            return await finalize_output(body.op)

        if body.op == "add_sticker":
            await svc.add_sticker(
                input_path=input_path,
                image_path=_resolve_existing_file(str(p["image_path"])),
                at_time=float(p.get("at_time", 0)),
                duration=float(p.get("duration", 2.0)),
                x=int(p.get("x", 20)),
                y=int(p.get("y", 20)),
                output_path=out_abs,
            )
            return await finalize_output(body.op)

        if body.op == "platform_preset":
            await svc.create_platform_version(
                input_path=input_path,
                platform=str(p.get("platform", "instagram")),
                output_path=out_abs,
            )
            return await finalize_output(body.op)

        if body.op == "export_video":
            await svc.export_video(
                input_path,
                out_abs,
                width=p.get("width"),
                height=p.get("height"),
                fps=p.get("fps"),
                bitrate=p.get("bitrate"),
            )
            return await finalize_output(body.op)

        if body.op == "merge_clips":
            paths: List[str] = p.get("input_paths", [])
            if not paths:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="merge_clips requires input_paths")
            resolved_paths = [_resolve_existing_file(path) for path in paths]
            await svc.merge_clips(resolved_paths, out_abs)
            return await finalize_output(body.op)

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown op: {body.op}")
    except HTTPException:
        raise
    except Exception as exc:
        return EditorOpResponse(op=body.op, error=str(exc))
