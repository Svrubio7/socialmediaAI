"""
OAuth and social media account endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


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


@router.get("/{platform}/connect", response_model=OAuthConnectResponse)
async def initiate_oauth(platform: str):
    """
    Initiate OAuth flow for a platform.
    
    Supported platforms: instagram, tiktok, youtube, facebook
    """
    supported_platforms = ["instagram", "tiktok", "youtube", "facebook"]
    if platform not in supported_platforms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported platform. Supported: {', '.join(supported_platforms)}"
        )
    
    # TODO: Implement OAuth initiation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OAuth not yet implemented"
    )


@router.get("/{platform}/callback")
async def oauth_callback(
    platform: str,
    code: str = Query(...),
    state: str = Query(...),
):
    """
    Handle OAuth callback from platform.
    """
    # TODO: Implement OAuth callback handling
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="OAuth callback not yet implemented"
    )


@router.get("/accounts", response_model=SocialAccountsListResponse)
async def list_social_accounts():
    """
    List connected social media accounts.
    """
    # TODO: Implement account listing
    return SocialAccountsListResponse(accounts=[])


@router.delete("/accounts/{account_id}")
async def disconnect_account(account_id: str):
    """
    Disconnect a social media account.
    """
    # TODO: Implement account disconnection
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Account disconnection not yet implemented"
    )


@router.post("/accounts/{account_id}/refresh")
async def refresh_account_token(account_id: str):
    """
    Manually refresh OAuth tokens for an account.
    """
    # TODO: Implement token refresh
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not yet implemented"
    )
