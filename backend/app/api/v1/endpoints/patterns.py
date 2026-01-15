"""
Pattern analysis endpoints.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.video import Video
from app.models.pattern import Pattern

router = APIRouter()


class PatternResponse(BaseModel):
    """Pattern response schema."""
    id: str
    video_id: str
    type: str
    score: float
    data: Dict[str, Any]
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PatternListResponse(BaseModel):
    """Pattern list response schema."""
    items: List[PatternResponse]
    total: int


class PatternSummary(BaseModel):
    """Summary of patterns by type."""
    type: str
    count: int
    average_score: float
    top_patterns: List[PatternResponse]


class PatternInsightsResponse(BaseModel):
    """Pattern insights response."""
    total_patterns: int
    average_score: float
    by_type: List[PatternSummary]
    top_performing: List[PatternResponse]


@router.get("", response_model=PatternListResponse)
async def list_patterns(
    video_id: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    pattern_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List analyzed patterns with optional filtering.
    """
    # Build query with user filter through videos
    query = db.query(Pattern).join(Video).filter(Video.user_id == current_user.id)
    
    if video_id:
        query = query.filter(Pattern.video_id == UUID(video_id))
    
    if min_score is not None:
        query = query.filter(Pattern.score >= min_score)
    
    if pattern_type:
        query = query.filter(Pattern.type == pattern_type)
    
    total = query.count()
    
    patterns = query.order_by(Pattern.score.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return PatternListResponse(
        items=[
            PatternResponse(
                id=str(p.id),
                video_id=str(p.video_id),
                type=p.type,
                score=p.score,
                data=p.data,
                description=p.description,
                created_at=p.created_at,
            )
            for p in patterns
        ],
        total=total,
    )


@router.get("/insights", response_model=PatternInsightsResponse)
async def get_pattern_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get aggregated pattern insights for the user.
    """
    # Get all patterns for user
    query = db.query(Pattern).join(Video).filter(Video.user_id == current_user.id)
    
    all_patterns = query.all()
    
    if not all_patterns:
        return PatternInsightsResponse(
            total_patterns=0,
            average_score=0.0,
            by_type=[],
            top_performing=[],
        )
    
    # Calculate overall stats
    total_patterns = len(all_patterns)
    average_score = sum(p.score for p in all_patterns) / total_patterns
    
    # Group by type
    by_type_dict: Dict[str, List[Pattern]] = {}
    for p in all_patterns:
        if p.type not in by_type_dict:
            by_type_dict[p.type] = []
        by_type_dict[p.type].append(p)
    
    by_type = []
    for pattern_type, patterns in by_type_dict.items():
        avg_score = sum(p.score for p in patterns) / len(patterns)
        top = sorted(patterns, key=lambda x: x.score, reverse=True)[:3]
        by_type.append(PatternSummary(
            type=pattern_type,
            count=len(patterns),
            average_score=avg_score,
            top_patterns=[
                PatternResponse(
                    id=str(p.id),
                    video_id=str(p.video_id),
                    type=p.type,
                    score=p.score,
                    data=p.data,
                    description=p.description,
                    created_at=p.created_at,
                )
                for p in top
            ],
        ))
    
    # Top performing patterns overall
    top_performing = sorted(all_patterns, key=lambda x: x.score, reverse=True)[:10]
    
    return PatternInsightsResponse(
        total_patterns=total_patterns,
        average_score=average_score,
        by_type=by_type,
        top_performing=[
            PatternResponse(
                id=str(p.id),
                video_id=str(p.video_id),
                type=p.type,
                score=p.score,
                data=p.data,
                description=p.description,
                created_at=p.created_at,
            )
            for p in top_performing
        ],
    )


@router.get("/{pattern_id}", response_model=PatternResponse)
async def get_pattern(
    pattern_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get pattern details by ID.
    """
    pattern = db.query(Pattern).join(Video).filter(
        Pattern.id == UUID(pattern_id),
        Video.user_id == current_user.id,
    ).first()
    
    if pattern is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pattern not found",
        )
    
    return PatternResponse(
        id=str(pattern.id),
        video_id=str(pattern.video_id),
        type=pattern.type,
        score=pattern.score,
        data=pattern.data,
        description=pattern.description,
        created_at=pattern.created_at,
    )


@router.get("/video/{video_id}", response_model=PatternListResponse)
async def get_video_patterns(
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all patterns for a specific video.
    """
    # Verify video belongs to user
    video = db.query(Video).filter(
        Video.id == UUID(video_id),
        Video.user_id == current_user.id,
    ).first()
    
    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    
    patterns = db.query(Pattern).filter(Pattern.video_id == UUID(video_id)).order_by(Pattern.score.desc()).all()
    
    return PatternListResponse(
        items=[
            PatternResponse(
                id=str(p.id),
                video_id=str(p.video_id),
                type=p.type,
                score=p.score,
                data=p.data,
                description=p.description,
                created_at=p.created_at,
            )
            for p in patterns
        ],
        total=len(patterns),
    )
