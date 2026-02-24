"""
Lightweight application timings for integration verification and quick perf checks.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.core.deps import get_current_user_optional
from app.models.user import User
from app.services.metrics_lite import get_metrics_snapshot, observe_duration

router = APIRouter()


class TimingEventRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    duration_ms: float = Field(ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


@router.get("/metrics-lite")
async def get_metrics_lite(_current_user: User | None = Depends(get_current_user_optional)):
    return get_metrics_snapshot()


@router.post("/metrics-lite/client", status_code=status.HTTP_202_ACCEPTED)
async def ingest_client_timing(
    payload: TimingEventRequest,
    current_user: User | None = Depends(get_current_user_optional),
):
    metadata = dict(payload.metadata or {})
    if current_user is not None:
        metadata.setdefault("user_id", str(current_user.id))
    metadata.setdefault("source", "client")
    observe_duration(payload.name, float(payload.duration_ms), metadata=metadata)
    return {"ok": True}
