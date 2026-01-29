"""Pydantic schemas for edit templates."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EditTemplateBase(BaseModel):
    """Base schema for edit template."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    style_spec: Dict[str, Any] = Field(default_factory=dict)


class EditTemplateCreate(EditTemplateBase):
    """Schema for creating an edit template."""

    pass


class EditTemplateUpdate(BaseModel):
    """Schema for updating an edit template (partial)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    style_spec: Optional[Dict[str, Any]] = None


class EditTemplateResponse(EditTemplateBase):
    """Schema for edit template response."""

    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EditTemplateListResponse(BaseModel):
    """Schema for paginated list of edit templates."""

    items: List[EditTemplateResponse]
    total: int


class EditTemplateApplyRequest(BaseModel):
    """Schema for apply edit template to video."""

    video_id: str
