"""
Shared editor jobs endpoints.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.editor_job import EditorJob
from app.models.user import User

router = APIRouter()


class EditorJobStatusResponse(BaseModel):
    job_id: str
    project_id: Optional[str] = None
    job_type: str
    status: str
    progress: float = 0.0
    cancel_requested: bool = False
    result: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: str
    updated_at: str


@router.get("/jobs/{job_id}", response_model=EditorJobStatusResponse)
async def get_editor_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        resolved_job_id = UUID(job_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid job id"
        ) from exc

    job = (
        db.query(EditorJob)
        .filter(EditorJob.id == resolved_job_id, EditorJob.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    return EditorJobStatusResponse(
        job_id=str(job.id),
        project_id=str(job.project_id) if job.project_id else None,
        job_type=(
            job.job_type.value if hasattr(job.job_type, "value") else str(job.job_type)
        ),
        status=job.status.value if hasattr(job.status, "value") else str(job.status),
        progress=float(job.progress or 0),
        cancel_requested=bool(job.cancel_requested),
        result=job.result or {},
        error_message=job.error_message,
        created_at=job.created_at.isoformat(),
        updated_at=job.updated_at.isoformat(),
    )
