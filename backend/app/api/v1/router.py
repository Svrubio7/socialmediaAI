"""
API v1 Router - Aggregates all API endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    analytics,
    auth,
    branding,
    chat,
    edit_templates,
    editor_jobs,
    editor_ops,
    oauth,
    patterns,
    posts,
    projects,
    scripts,
    strategies,
    videos,
)

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
api_router.include_router(branding.router, prefix="/branding", tags=["Branding"])
api_router.include_router(edit_templates.router, prefix="/edit-templates", tags=["Edit templates"])
api_router.include_router(editor_ops.router, prefix="/editor", tags=["Editor ops"])
api_router.include_router(editor_jobs.router, prefix="/editor", tags=["Editor jobs"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
