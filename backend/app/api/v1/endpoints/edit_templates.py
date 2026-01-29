"""
Edit templates CRUD endpoints.
"""

from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.edit_template import EditTemplate
from app.schemas.edit_template import (
    EditTemplateCreate,
    EditTemplateUpdate,
    EditTemplateResponse,
    EditTemplateListResponse,
    EditTemplateApplyRequest,
)

router = APIRouter()


@router.get("", response_model=EditTemplateListResponse)
async def list_edit_templates(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List edit templates for the current user."""
    query = db.query(EditTemplate).filter(EditTemplate.user_id == current_user.id)
    total = query.count()
    items = query.order_by(EditTemplate.updated_at.desc()).offset(offset).limit(limit).all()
    return EditTemplateListResponse(
        items=[
            EditTemplateResponse(
                id=str(t.id),
                name=t.name,
                description=t.description,
                style_spec=t.style_spec or {},
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in items
        ],
        total=total,
    )


@router.post("", response_model=EditTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_edit_template(
    body: EditTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create an edit template."""
    t = EditTemplate(
        id=uuid4(),
        user_id=current_user.id,
        name=body.name,
        description=body.description,
        style_spec=body.style_spec,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return EditTemplateResponse(
        id=str(t.id),
        name=t.name,
        description=t.description,
        style_spec=t.style_spec or {},
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


@router.get("/{template_id}", response_model=EditTemplateResponse)
async def get_edit_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single edit template by id."""
    t = db.query(EditTemplate).filter(
        EditTemplate.id == UUID(template_id),
        EditTemplate.user_id == current_user.id,
    ).first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edit template not found")
    return EditTemplateResponse(
        id=str(t.id),
        name=t.name,
        description=t.description,
        style_spec=t.style_spec or {},
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


@router.patch("/{template_id}", response_model=EditTemplateResponse)
async def update_edit_template(
    template_id: str,
    body: EditTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an edit template (partial)."""
    t = db.query(EditTemplate).filter(
        EditTemplate.id == UUID(template_id),
        EditTemplate.user_id == current_user.id,
    ).first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edit template not found")
    if body.name is not None:
        t.name = body.name
    if body.description is not None:
        t.description = body.description
    if body.style_spec is not None:
        t.style_spec = body.style_spec
    db.commit()
    db.refresh(t)
    return EditTemplateResponse(
        id=str(t.id),
        name=t.name,
        description=t.description,
        style_spec=t.style_spec or {},
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


@router.post("/{template_id}/apply")
async def apply_edit_template(
    template_id: str,
    body: EditTemplateApplyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Apply an edit template to a video."""
    from uuid import UUID
    from app.models.video import Video

    t = db.query(EditTemplate).filter(
        EditTemplate.id == UUID(template_id),
        EditTemplate.user_id == current_user.id,
    ).first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edit template not found")
    video_id = body.video_id
    v = db.query(Video).filter(
        Video.id == UUID(video_id),
        Video.user_id == current_user.id,
    ).first()
    if not v:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    # TODO: Run editor ops from t.style_spec against v.storage_path; create new video record.
    return {
        "message": "apply_edit_template queued (not yet implemented)",
        "template_id": template_id,
        "video_id": video_id,
    }


@router.delete("/{template_id}")
async def delete_edit_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an edit template."""
    t = db.query(EditTemplate).filter(
        EditTemplate.id == UUID(template_id),
        EditTemplate.user_id == current_user.id,
    ).first()
    if not t:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edit template not found")
    db.delete(t)
    db.commit()
    return {"ok": True}
