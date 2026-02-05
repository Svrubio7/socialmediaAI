"""
OAuth and social media account endpoints.
Development-safe implementation:
- Stores connected accounts in DB
- Returns immediate "connected" state without external OAuth round-trips
"""

from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.social_account import SocialAccount
from app.utils.encryption import encrypt_token

router = APIRouter()
SUPPORTED_PLATFORMS = {"instagram", "tiktok", "youtube", "facebook"}


class OAuthConnectResponse(BaseModel):
    """OAuth connection initiation response."""

    auth_url: str
    state: str


class SocialAccountResponse(BaseModel):
    """Social account response schema."""

    id: str
    platform: str
    username: str
    profile_url: Optional[str] = None
    connected_at: datetime
    last_sync: Optional[datetime] = None


class SocialAccountsListResponse(BaseModel):
    """Social accounts list response schema."""

    accounts: List[SocialAccountResponse]


def _validate_platform(platform: str) -> str:
    normalized = platform.strip().lower()
    if normalized not in SUPPORTED_PLATFORMS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported platform. Supported: {', '.join(sorted(SUPPORTED_PLATFORMS))}",
        )
    return normalized


@router.get("/{platform}/connect", response_model=OAuthConnectResponse)
async def initiate_oauth(
    platform: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Connect a social account.
    For local/dev workflow we create or refresh a mock connected account.
    """
    platform = _validate_platform(platform)
    existing = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id,
        SocialAccount.platform == platform,
    ).first()
    if existing:
        existing.last_sync = datetime.utcnow()
        db.commit()
        return OAuthConnectResponse(auth_url="", state="already_connected")

    username = f"{platform}_{str(current_user.id)[:8]}"
    now = datetime.utcnow()
    account = SocialAccount(
        id=uuid4(),
        user_id=current_user.id,
        platform=platform,
        platform_user_id=f"{platform}_{uuid4().hex[:12]}",
        username=username,
        profile_url=f"https://{platform}.com/{username}",
        access_token_encrypted=encrypt_token(f"dev_access_{uuid4().hex}"),
        refresh_token_encrypted=encrypt_token(f"dev_refresh_{uuid4().hex}"),
        token_expires_at=now + timedelta(days=30),
        last_sync=now,
    )
    db.add(account)
    db.commit()
    return OAuthConnectResponse(auth_url="", state="connected")


@router.get("/{platform}/callback")
async def oauth_callback(
    platform: str,
    code: str = Query(...),
    state: str = Query(...),
):
    """
    Placeholder callback endpoint for compatibility.
    """
    _ = _validate_platform(platform)
    return {
        "ok": True,
        "platform": platform,
        "state": state,
        "message": "Callback received. Development mode uses immediate account linking.",
    }


@router.get("/accounts", response_model=SocialAccountsListResponse)
async def list_social_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List connected social media accounts for the current user.
    """
    rows = db.query(SocialAccount).filter(
        SocialAccount.user_id == current_user.id,
    ).order_by(SocialAccount.created_at.desc()).all()
    return SocialAccountsListResponse(
        accounts=[
            SocialAccountResponse(
                id=str(a.id),
                platform=a.platform,
                username=a.username or a.platform_user_id,
                profile_url=a.profile_url,
                connected_at=a.created_at,
                last_sync=a.last_sync,
            )
            for a in rows
        ]
    )


@router.delete("/accounts/{account_id}")
async def disconnect_account(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Disconnect a social media account.
    """
    account = db.query(SocialAccount).filter(
        SocialAccount.id == UUID(account_id),
        SocialAccount.user_id == current_user.id,
    ).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connected account not found",
        )
    db.delete(account)
    db.commit()
    return {"ok": True}


@router.post("/accounts/{account_id}/refresh")
async def refresh_account_token(
    account_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Refresh stored token metadata for an account.
    """
    account = db.query(SocialAccount).filter(
        SocialAccount.id == UUID(account_id),
        SocialAccount.user_id == current_user.id,
    ).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connected account not found",
        )
    account.access_token_encrypted = encrypt_token(f"dev_access_{uuid4().hex}")
    account.token_expires_at = datetime.utcnow() + timedelta(days=30)
    account.last_sync = datetime.utcnow()
    db.commit()
    return {"ok": True, "account_id": account_id}

