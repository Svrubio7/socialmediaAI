"""
Pydantic schemas for request/response validation.
"""

from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.video import VideoCreate, VideoResponse, VideoUploadResponse
from app.schemas.pattern import PatternResponse, PatternListResponse
from app.schemas.strategy import StrategyCreate, StrategyResponse
from app.schemas.script import ScriptCreate, ScriptResponse
from app.schemas.post import PublishRequest, ScheduleRequest, PostResponse
from app.schemas.analytics import AnalyticsResponse, DashboardResponse

__all__ = [
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "VideoCreate",
    "VideoResponse",
    "VideoUploadResponse",
    "PatternResponse",
    "PatternListResponse",
    "StrategyCreate",
    "StrategyResponse",
    "ScriptCreate",
    "ScriptResponse",
    "PublishRequest",
    "ScheduleRequest",
    "PostResponse",
    "AnalyticsResponse",
    "DashboardResponse",
]
