"""
Security utilities for authentication and authorization.
"""

from datetime import datetime, timedelta
from typing import Optional, Any
import logging

import httpx
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict] = None,
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Token expiration time
        additional_claims: Additional claims to include
        
    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        subject: Token subject (usually user ID)
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    }
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None


def verify_supabase_token(token: str) -> Optional[dict]:
    """
    Verify a Supabase JWT token.
    
    Args:
        token: Supabase JWT token
        
    Returns:
        Decoded token payload or None if invalid
    """
    jwt_secret = (settings.SUPABASE_JWT_SECRET or "").strip()

    # First try local JWT verification when a real JWT secret is configured.
    if jwt_secret and jwt_secret not in {"your-jwt-secret", "changeme"}:
        try:
            # Supabase legacy tokens use HS256 + project JWT secret.
            payload = jwt.decode(
                token,
                jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )
            return payload
        except JWTError:
            pass

    # Fallback for modern Supabase (asymmetric signing) or missing JWT secret:
    # ask Supabase Auth to validate the bearer token and return user claims.
    supabase_url = (settings.SUPABASE_URL or "").rstrip("/")
    supabase_key = (settings.SUPABASE_KEY or "").strip()
    if supabase_url and supabase_key:
        try:
            resp = httpx.get(
                f"{supabase_url}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": supabase_key,
                },
                timeout=5.0,
            )
            if resp.status_code == 200:
                user = resp.json()
                if isinstance(user, dict) and user.get("id"):
                    user_metadata = user.get("user_metadata")
                    if not isinstance(user_metadata, dict):
                        user_metadata = {}

                    app_metadata = user.get("app_metadata")
                    if not isinstance(app_metadata, dict):
                        app_metadata = {}

                    return {
                        "sub": user.get("id"),
                        "email": user.get("email"),
                        "aud": user.get("aud") or "authenticated",
                        "role": user.get("role") or app_metadata.get("role"),
                        "user_metadata": user_metadata,
                        "name": user_metadata.get("name"),
                        "picture": user_metadata.get("avatar_url") or user_metadata.get("picture"),
                        "iss": f"{supabase_url}/auth/v1",
                    }
        except Exception as exc:
            logger.warning("Supabase token validation fallback failed: %s", exc)
    # Last-resort development fallback to reduce local setup friction.
    # Never used in production when DEBUG=false.
    if settings.DEBUG:
        try:
            claims = jwt.get_unverified_claims(token)
            if isinstance(claims, dict) and claims.get("sub"):
                return claims
        except Exception:
            pass
    return None
