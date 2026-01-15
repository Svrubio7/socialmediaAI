"""
Authentication endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.core.config import settings
from app.models.user import User

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Register request schema."""
    email: EmailStr
    password: str
    name: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RefreshRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


class UserResponse(BaseModel):
    """User response schema."""
    id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT tokens.
    
    Note: This endpoint is primarily for development/testing.
    Production should use Supabase Auth directly.
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
        },
    )


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Note: This endpoint is primarily for development/testing.
    Production should use Supabase Auth directly.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    user = User(
        id=uuid4(),
        supabase_user_id=uuid4(),  # Will be updated when Supabase is configured
        email=request.email,
        name=request.name,
        is_active=True,
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
        },
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    """
    Refresh JWT access token.
    """
    # Decode refresh token
    payload = decode_token(request.refresh_token)
    
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Create new access token
    access_token = create_access_token(subject=str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
        },
    )


@router.post("/logout")
async def logout():
    """
    Logout user and invalidate tokens.
    
    Note: With JWT tokens, logout is typically handled client-side
    by removing the token. This endpoint is for compatibility.
    """
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        avatar_url=current_user.avatar_url,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )


@router.post("/sync-supabase")
async def sync_supabase_user(
    supabase_user_id: str,
    email: str,
    name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Sync user from Supabase Auth to local database.
    Called after Supabase authentication to ensure user exists in local DB.
    """
    supabase_uuid = UUID(supabase_user_id)
    
    # Check if user already exists
    user = db.query(User).filter(User.supabase_user_id == supabase_uuid).first()
    
    if user is None:
        # Check by email
        user = db.query(User).filter(User.email == email).first()
        if user:
            # Update existing user with Supabase ID
            user.supabase_user_id = supabase_uuid
        else:
            # Create new user
            user = User(
                id=uuid4(),
                supabase_user_id=supabase_uuid,
                email=email,
                name=name,
                is_active=True,
            )
            db.add(user)
    
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return {
        "id": str(user.id),
        "supabase_user_id": str(user.supabase_user_id),
        "email": user.email,
        "name": user.name,
    }
