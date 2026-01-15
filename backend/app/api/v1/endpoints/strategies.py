"""
Strategy generation endpoints.
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
from app.models.video import Video
from app.models.pattern import Pattern
from app.models.strategy import Strategy
from app.services.strategy_service import StrategyService
from app.utils.templates import get_cached_response, cache_response

router = APIRouter()


class StrategyGenerateRequest(BaseModel):
    """Strategy generation request schema."""
    video_ids: List[str]
    platforms: List[str]
    goals: Optional[List[str]] = None
    niche: Optional[str] = None


class StrategyResponse(BaseModel):
    """Strategy response schema."""
    id: str
    user_id: str
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
    """Strategy list response schema."""
    items: List[StrategyResponse]
    total: int


@router.post("/generate", response_model=StrategyResponse)
async def generate_strategy(
    request: StrategyGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate a marketing strategy based on video patterns.
    """
    # Validate video ownership
    videos = db.query(Video).filter(
        Video.id.in_([UUID(vid) for vid in request.video_ids]),
        Video.user_id == current_user.id,
    ).all()
    
    if len(videos) != len(request.video_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more videos not found",
        )
    
    # Get patterns for videos
    patterns = db.query(Pattern).filter(
        Pattern.video_id.in_([UUID(vid) for vid in request.video_ids])
    ).all()
    
    # Check template cache
    cache_params = {
        "platforms": sorted(request.platforms),
        "goals": sorted(request.goals or []),
        "niche": request.niche,
        "pattern_count": len(patterns),
    }
    
    cached = get_cached_response("strategy", cache_params)
    if cached:
        strategy_data = cached
    else:
        # Generate strategy using AI
        strategy_service = StrategyService(openai_api_key=settings.OPENAI_API_KEY)
        
        pattern_data = [
            {
                "type": p.type,
                "score": p.score,
                "data": p.data,
            }
            for p in patterns
        ]
        
        strategy_data = await strategy_service.generate_strategy(
            patterns=pattern_data,
            platforms=request.platforms,
            goals=request.goals,
            niche=request.niche,
        )
        
        # Cache the response
        cache_response("strategy", cache_params, strategy_data)
    
    # Save strategy to database
    strategy = Strategy(
        id=uuid4(),
        user_id=current_user.id,
        video_ids=[str(vid) for vid in request.video_ids],
        platforms=request.platforms,
        goals=request.goals,
        niche=request.niche,
        strategy_data=strategy_data,
        version=1,
    )
    
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    
    return StrategyResponse(
        id=str(strategy.id),
        user_id=str(strategy.user_id),
        video_ids=strategy.video_ids,
        platforms=strategy.platforms,
        goals=strategy.goals,
        niche=strategy.niche,
        strategy_data=strategy.strategy_data,
        version=strategy.version,
        created_at=strategy.created_at,
    )


@router.get("", response_model=StrategyListResponse)
async def list_strategies(
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List user's strategies.
    """
    query = db.query(Strategy).filter(Strategy.user_id == current_user.id)
    
    total = query.count()
    strategies = query.order_by(Strategy.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return StrategyListResponse(
        items=[
            StrategyResponse(
                id=str(s.id),
                user_id=str(s.user_id),
                video_ids=s.video_ids,
                platforms=s.platforms,
                goals=s.goals,
                niche=s.niche,
                strategy_data=s.strategy_data,
                version=s.version,
                created_at=s.created_at,
            )
            for s in strategies
        ],
        total=total,
    )


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get strategy details by ID.
    """
    strategy = db.query(Strategy).filter(
        Strategy.id == UUID(strategy_id),
        Strategy.user_id == current_user.id,
    ).first()
    
    if strategy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
    
    return StrategyResponse(
        id=str(strategy.id),
        user_id=str(strategy.user_id),
        video_ids=strategy.video_ids,
        platforms=strategy.platforms,
        goals=strategy.goals,
        niche=strategy.niche,
        strategy_data=strategy.strategy_data,
        version=strategy.version,
        created_at=strategy.created_at,
    )


@router.get("/{strategy_id}/export")
async def export_strategy(
    strategy_id: str,
    format: str = "markdown",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export strategy in specified format.
    """
    strategy = db.query(Strategy).filter(
        Strategy.id == UUID(strategy_id),
        Strategy.user_id == current_user.id,
    ).first()
    
    if strategy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
    
    if format == "markdown":
        content = _export_as_markdown(strategy)
        return Response(
            content=content,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=strategy_{strategy_id[:8]}.md"},
        )
    elif format == "json":
        import json
        content = json.dumps(strategy.strategy_data, indent=2)
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=strategy_{strategy_id[:8]}.json"},
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}. Supported: markdown, json",
        )


def _export_as_markdown(strategy: Strategy) -> str:
    """Export strategy as Markdown."""
    data = strategy.strategy_data
    
    md = f"""# Marketing Strategy

**Generated:** {strategy.created_at.strftime('%Y-%m-%d %H:%M UTC')}

**Platforms:** {', '.join(strategy.platforms)}

**Goals:** {', '.join(strategy.goals or ['engagement'])}

**Niche:** {strategy.niche or 'General'}

---

## Recommendations

"""
    
    recommendations = data.get("recommendations", [])
    for i, rec in enumerate(recommendations, 1):
        md += f"### {i}. {rec.get('category', 'General')}\n\n"
        md += f"{rec.get('recommendation', '')}\n\n"
        if rec.get('rationale'):
            md += f"*Rationale: {rec.get('rationale')}*\n\n"
    
    posting_schedule = data.get("posting_schedule", {})
    if posting_schedule:
        md += "## Posting Schedule\n\n"
        md += f"- **Frequency:** {posting_schedule.get('frequency', 'Daily')}\n"
        optimal_times = posting_schedule.get("optimal_times", [])
        if optimal_times:
            md += f"- **Optimal Times:** {', '.join(optimal_times)}\n"
        md += "\n"
    
    hashtag_strategy = data.get("hashtag_strategy", {})
    if hashtag_strategy:
        md += "## Hashtag Strategy\n\n"
        primary = hashtag_strategy.get("primary_hashtags", [])
        if primary:
            md += f"**Primary:** {' '.join(primary)}\n\n"
        secondary = hashtag_strategy.get("secondary_hashtags", [])
        if secondary:
            md += f"**Secondary:** {' '.join(secondary)}\n\n"
    
    content_themes = data.get("content_themes", [])
    if content_themes:
        md += "## Content Themes\n\n"
        for theme in content_themes:
            md += f"- {theme}\n"
    
    return md
