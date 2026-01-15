"""
Strategy schemas for request/response validation.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class StrategyCreate(BaseModel):
    """Schema for creating a strategy."""
    video_ids: List[UUID]
    platforms: List[str]
    goals: Optional[List[str]] = None
    niche: Optional[str] = None


class StrategyData(BaseModel):
    """Strategy data schema."""
    recommendations: List[Dict[str, Any]]
    posting_schedule: Optional[Dict[str, Any]] = None
    hashtag_strategy: Optional[Dict[str, Any]] = None
    content_themes: Optional[List[str]] = None


class StrategyResponse(BaseModel):
    """Schema for strategy response."""
    id: UUID
    user_id: UUID
    video_ids: List[str]
    platforms: List[str]
    goals: Optional[List[str]] = None
    niche: Optional[str] = None
    strategy_data: Dict[str, Any]
    version: int
    created_at: datetime

    class Config:
        from_attributes = True


class StrategyListResponse(BaseModel):
    """Schema for strategy list response."""
    items: List[StrategyResponse]
    total: int
