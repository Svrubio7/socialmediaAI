"""
Pattern schemas for request/response validation.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class PatternData(BaseModel):
    """Pattern data schema."""
    type: str
    description: Optional[str] = None
    timing: Optional[Dict[str, Any]] = None
    visual_elements: Optional[List[str]] = None
    audio_elements: Optional[List[str]] = None
    additional: Optional[Dict[str, Any]] = None


class PatternResponse(BaseModel):
    """Schema for pattern response."""
    id: UUID
    video_id: UUID
    type: str
    score: float
    data: Dict[str, Any]
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PatternListResponse(BaseModel):
    """Schema for pattern list response."""
    items: List[PatternResponse]
    total: int


class PatternScoreUpdate(BaseModel):
    """Schema for updating pattern scores."""
    pattern_id: UUID
    new_score: float
    performance_data: Optional[Dict[str, Any]] = None
