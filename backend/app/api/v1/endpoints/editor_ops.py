"""
Editor foundation ops API. Dispatches to VideoEditorService.
Used by UI and MCP. All ops require video_id and user auth.
"""

import os
import tempfile
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.video import Video
from app.services.video_editor import VideoEditorService

router = APIRouter()


class EditorOpRequest(BaseModel):
    """Request to run a single editor op."""

    op: str
    params: Dict[str, Any] = {}


class EditorOpResponse(BaseModel):
    """Response from editor op execution."""

    op: str
    output_path: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


def _get_video_path(db: Session, video_id: str, user_id: UUID) -> str:
    v = db.query(Video).filter(Video.id == UUID(video_id), Video.user_id == user_id).first()
    if not v:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    return v.storage_path


@router.post("/{video_id}/op", response_model=EditorOpResponse)
async def execute_editor_op(
    video_id: str,
    body: EditorOpRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Execute a single editor foundation op on a video.
    Ops: trim_clip, clip_out, split_clip, duplicate_clip, merge_clips, crop_clip,
    rotate_clip, mirror_clip, set_clip_speed, reverse_clip, freeze_frame,
    set_canvas_size, export_video, etc.
    """
    svc = VideoEditorService()
    input_path = _get_video_path(db, video_id, current_user.id)
    tmp = tempfile.gettempdir()
    out = os.path.join(tmp, f"editor_op_{video_id}_{body.op}.mp4")
    p = body.params

    async def run() -> EditorOpResponse:
        try:
            if body.op == "trim_clip":
                await svc.trim_clip(input_path, float(p["start"]), float(p["end"]), out)
                return EditorOpResponse(op=body.op, output_path=out)

            if body.op == "clip_out":
                await svc.clip_out(input_path, float(p["start"]), float(p["end"]), out)
                return EditorOpResponse(op=body.op, output_path=out)

            if body.op == "duplicate_clip":
                await svc.duplicate_clip(input_path, out)
                return EditorOpResponse(op=body.op, output_path=out)

            if body.op == "set_clip_speed":
                await svc.set_clip_speed(input_path, float(p.get("speed", 1.0)), out)
                return EditorOpResponse(op=body.op, output_path=out)

            if body.op == "reverse_clip":
                await svc.reverse_clip(input_path, out)
                return EditorOpResponse(op=body.op, output_path=out)

            if body.op == "crop_clip":
                await svc.crop_clip(
                    input_path,
                    int(p["x"]),
                    int(p["y"]),
                    int(p["width"]),
                    int(p["height"]),
                    out,
                )
                return EditorOpResponse(op=body.op, output_path=out)

            if body.op == "rotate_clip":
                await svc.rotate_clip(input_path, float(p.get("degrees", 90)), out)
                return EditorOpResponse(op=body.op, output_path=out)

            if body.op == "mirror_clip":
                await svc.mirror_clip(input_path, bool(p.get("horizontal", True)), out)
                return EditorOpResponse(op=body.op, output_path=out)

            if body.op == "set_canvas_size":
                await svc.set_canvas_size(input_path, int(p["width"]), int(p["height"]), out)
                return EditorOpResponse(op=body.op, output_path=out)

            if body.op == "export_video":
                await svc.export_video(
                    input_path,
                    out,
                    width=p.get("width"),
                    height=p.get("height"),
                    fps=p.get("fps"),
                    bitrate=p.get("bitrate"),
                )
                return EditorOpResponse(op=body.op, output_path=out)

            if body.op == "merge_clips":
                paths: List[str] = p.get("input_paths", [])
                if not paths:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="merge_clips requires input_paths")
                await svc.merge_clips(paths, out)
                return EditorOpResponse(op=body.op, output_path=out)

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown op: {body.op}")
        except Exception as e:
            return EditorOpResponse(op=body.op, error=str(e))

    return await run()
