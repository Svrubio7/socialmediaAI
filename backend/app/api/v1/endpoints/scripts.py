"""
Script generation endpoints.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Response
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.pattern import Pattern
from app.models.script import Script
from app.services.script_service import ScriptService
from app.utils.templates import get_cached_response, cache_response

router = APIRouter()


class ScriptGenerateRequest(BaseModel):
    """Script generation request schema."""
    concept: str
    platform: str
    duration: int = 60
    target_patterns: Optional[List[str]] = None


class ScriptResponse(BaseModel):
    """Script response schema."""
    id: str
    user_id: str
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
    """Script list response schema."""
    items: List[ScriptResponse]
    total: int


@router.post("/generate", response_model=ScriptResponse)
async def generate_script(
    request: ScriptGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate a filming/editing script based on concept and patterns.
    """
    # Get patterns if specified
    patterns = []
    if request.target_patterns:
        patterns = db.query(Pattern).filter(
            Pattern.id.in_([UUID(pid) for pid in request.target_patterns])
        ).all()
    
    # Check template cache
    cache_params = {
        "concept": request.concept,
        "platform": request.platform,
        "duration": request.duration,
        "pattern_count": len(patterns),
    }
    
    cached = get_cached_response("script", cache_params)
    if cached:
        script_data = cached
    else:
        # Generate script using AI
        script_service = ScriptService(openai_api_key=settings.OPENAI_API_KEY)
        
        pattern_data = [
            {
                "type": p.type,
                "score": p.score,
                "data": p.data,
            }
            for p in patterns
        ] if patterns else None
        
        script_data = await script_service.generate_script(
            concept=request.concept,
            platform=request.platform,
            duration=request.duration,
            patterns=pattern_data,
        )
        
        # Cache the response
        cache_response("script", cache_params, script_data)
    
    # Calculate actual duration from segments
    actual_duration = None
    if "segments" in script_data:
        segments = script_data["segments"]
        if segments:
            actual_duration = max(s.get("end_time", 0) for s in segments)
    
    # Save script to database
    script = Script(
        id=uuid4(),
        user_id=current_user.id,
        concept=request.concept,
        platform=request.platform,
        target_duration=request.duration,
        pattern_ids=[str(p.id) for p in patterns] if patterns else [],
        script_data=script_data,
        actual_duration=actual_duration,
        version=1,
    )
    
    db.add(script)
    db.commit()
    db.refresh(script)
    
    return ScriptResponse(
        id=str(script.id),
        user_id=str(script.user_id),
        concept=script.concept,
        platform=script.platform,
        target_duration=script.target_duration,
        actual_duration=script.actual_duration,
        script_data=script.script_data,
        version=script.version,
        created_at=script.created_at,
    )


@router.get("", response_model=ScriptListResponse)
async def list_scripts(
    page: int = 1,
    limit: int = 20,
    platform: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List user's scripts.
    """
    query = db.query(Script).filter(Script.user_id == current_user.id)
    
    if platform:
        query = query.filter(Script.platform == platform)
    
    total = query.count()
    scripts = query.order_by(Script.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return ScriptListResponse(
        items=[
            ScriptResponse(
                id=str(s.id),
                user_id=str(s.user_id),
                concept=s.concept,
                platform=s.platform,
                target_duration=s.target_duration,
                actual_duration=s.actual_duration,
                script_data=s.script_data,
                version=s.version,
                created_at=s.created_at,
            )
            for s in scripts
        ],
        total=total,
    )


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(
    script_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get script details by ID.
    """
    script = db.query(Script).filter(
        Script.id == UUID(script_id),
        Script.user_id == current_user.id,
    ).first()
    
    if script is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )
    
    return ScriptResponse(
        id=str(script.id),
        user_id=str(script.user_id),
        concept=script.concept,
        platform=script.platform,
        target_duration=script.target_duration,
        actual_duration=script.actual_duration,
        script_data=script.script_data,
        version=script.version,
        created_at=script.created_at,
    )


@router.get("/{script_id}/export")
async def export_script(
    script_id: str,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export script in specified format.
    """
    script = db.query(Script).filter(
        Script.id == UUID(script_id),
        Script.user_id == current_user.id,
    ).first()
    
    if script is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )
    
    if format == "markdown":
        content = _export_as_markdown(script)
        return Response(
            content=content,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=script_{script_id[:8]}.md"},
        )
    elif format == "json":
        import json
        content = json.dumps(script.script_data, indent=2)
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=script_{script_id[:8]}.json"},
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}. Supported: markdown, json",
        )


def _export_as_markdown(script: Script) -> str:
    """Export script as Markdown."""
    data = script.script_data
    
    md = f"""# Video Script: {script.concept}

**Generated:** {script.created_at.strftime('%Y-%m-%d %H:%M UTC')}

**Platform:** {script.platform}

**Target Duration:** {script.target_duration} seconds

---

## Script Timeline

"""
    
    segments = data.get("segments", [])
    for segment in segments:
        start = segment.get("start_time", 0)
        end = segment.get("end_time", 0)
        segment_type = segment.get("type", "content")
        
        md += f"### [{start:.1f}s - {end:.1f}s] {segment_type.upper()}\n\n"
        
        if segment.get("visual"):
            md += f"**Visual:** {segment['visual']}\n\n"
        
        if segment.get("audio"):
            md += f"**Audio:** {segment['audio']}\n\n"
        
        if segment.get("text_overlay"):
            md += f"**Text Overlay:** {segment['text_overlay']}\n\n"
        
        if segment.get("instructions"):
            md += f"**Instructions:** {segment['instructions']}\n\n"
        
        md += "---\n\n"
    
    return md
