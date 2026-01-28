"""
API v1 Router - Aggregates all API endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, videos, patterns, strategies, scripts, posts, analytics, oauth, chat, materials

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(videos.router, prefix="/videos", tags=["Videos"])
api_router.include_router(patterns.router, prefix="/patterns", tags=["Patterns"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["Strategies"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(scripts.router, prefix="/scripts", tags=["Scripts"])
api_router.include_router(posts.router, prefix="/posts", tags=["Publishing"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(oauth.router, prefix="/oauth", tags=["OAuth"])
api_router.include_router(materials.router, prefix="/materials", tags=["Materials"])
