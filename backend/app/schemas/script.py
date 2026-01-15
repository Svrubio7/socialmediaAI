"""
Script schemas for request/response validation.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class ScriptSegment(BaseModel):
    """Script segment schema."""
    start_time: float
    end_time: float
    type: Optional[str] = None
    visual: Optional[str] = None
    audio: Optional[str] = None
    text_overlay: Optional[str] = None
    instructions: Optional[str] = None


class ScriptCreate(BaseModel):
    """Schema for creating a script."""
    concept: str
    platform: str
    duration: int = 60
    target_patterns: Optional[List[UUID]] = None


class ScriptData(BaseModel):
    """Script data schema."""
    segments: List[ScriptSegment]
    total_duration: float
    platform: str


class ScriptResponse(BaseModel):
    """Schema for script response."""
    id: UUID
    user_id: UUID
    concept: str
    platform: str
    target_duration: int
    actual_duration: Optional[float] = None
    script_data: Dict[str, Any]
    version: int
    created_at: datetime

    class Config:
        from_attributes = True


class ScriptListResponse(BaseModel):
    """Schema for script list response."""
    items: List[ScriptResponse]
    total: int
