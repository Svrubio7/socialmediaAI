"""
FastAPI dependencies for authentication and database.
"""

from typing import Generator, Optional
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID, uuid4

from app.db.session import SessionLocal
from app.core.security import verify_supabase_token, decode_token
from app.models.user import User

# HTTP Bearer token security
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Validate JWT token and return decoded payload.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    
    # Try internal token first (fast path for local/dev auth endpoints).
    payload = decode_token(token)

    # Fall back to Supabase token verification.
    if payload is None:
        payload = verify_supabase_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def get_current_user(
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_current_user_token),
) -> User:
    """
    Get current authenticated user from database.
    
    Args:
        db: Database session
        token_payload: Decoded JWT token
        
    Returns:
        Current user model instance
        
    Raises:
        HTTPException: If user not found or inactive
    """
    user_id = token_payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    supabase_uuid: Optional[UUID] = None
    try:
        supabase_uuid = UUID(str(user_id))
    except (ValueError, TypeError):
        supabase_uuid = None

    # Try to find user by Supabase user ID
    user = db.query(User).filter(User.supabase_user_id == supabase_uuid).first() if supabase_uuid else None
    
    # If not found, try by internal user ID
    if user is None:
        try:
            user = db.query(User).filter(User.id == UUID(user_id)).first()
        except (ValueError, TypeError):
            pass

    # Auto-provision local user from a valid Supabase token when missing.
    if user is None and supabase_uuid is not None:
        email = token_payload.get("email")
        if email:
            user_metadata = token_payload.get("user_metadata")
            if not isinstance(user_metadata, dict):
                user_metadata = {}
            display_name = user_metadata.get("name") or token_payload.get("name")
            avatar_url = user_metadata.get("avatar_url") or token_payload.get("picture")

            existing_by_email = db.query(User).filter(User.email == email).first()
            if existing_by_email:
                existing_by_email.supabase_user_id = supabase_uuid
                if display_name and not existing_by_email.name:
                    existing_by_email.name = display_name
                if avatar_url and not existing_by_email.avatar_url:
                    existing_by_email.avatar_url = avatar_url
                existing_by_email.last_login = datetime.utcnow()
                db.commit()
                db.refresh(existing_by_email)
                user = existing_by_email
            else:
                user = User(
                    id=uuid4(),
                    supabase_user_id=supabase_uuid,
                    email=email,
                    name=display_name,
                    avatar_url=avatar_url,
                    is_active=True,
                    last_login=datetime.utcnow(),
                )
                db.add(user)
                db.commit()
                db.refresh(user)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user


async def get_current_user_optional(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    
    Args:
        db: Database session
        credentials: Optional HTTP Bearer credentials
        
    Returns:
        Current user or None
    """
    if credentials is None:
        return None
    
    try:
        token_payload = await get_current_user_token(credentials)
        user = await get_current_user(db, token_payload)
        return user
    except HTTPException:
        return None
