"""
Social Media AI SaaS - FastAPI Backend
Main application entry point
"""

from contextlib import asynccontextmanager
import mimetypes
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings

# Ensure common video types are served with correct mime types (Windows often lacks these).
mimetypes.add_type("video/mp4", ".mp4")
mimetypes.add_type("video/mp4", ".m4v")
mimetypes.add_type("video/quicktime", ".mov")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    print("Starting Social Media AI Backend...")
    yield
    # Shutdown
    print("Shutting down Social Media AI Backend...")


class CORSStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers.setdefault("Access-Control-Allow-Origin", "*")
        response.headers.setdefault("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        response.headers.setdefault("Access-Control-Allow-Headers", "*")
        response.headers.setdefault("Access-Control-Expose-Headers", "Accept-Ranges, Content-Range, Content-Length")
        return response


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered social media marketing hub for video pattern analysis, strategy generation, and automated publishing",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
cors_kwargs = dict(
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
allow_all = settings.DEBUG or "*" in settings.cors_origins_list
if allow_all:
    # In dev or when CORS_ORIGINS="*", allow any origin.
    cors_kwargs["allow_origin_regex"] = ".*"
else:
    cors_kwargs["allow_origins"] = settings.cors_origins_list

app.add_middleware(CORSMiddleware, **cors_kwargs)


@app.middleware("http")
async def ensure_cors_headers(request: Request, call_next):
    """
    Ensure CORS headers are present even on error responses.
    CORSMiddleware should handle this, but we set fallbacks if headers are missing.
    """
    response = await call_next(request)
    origin = request.headers.get("origin")
    if origin and (allow_all or origin in settings.cors_origins_list):
        response.headers.setdefault("Access-Control-Allow-Origin", origin)
        response.headers.setdefault("Vary", "Origin")
        response.headers.setdefault("Access-Control-Allow-Credentials", "true")
        response.headers.setdefault("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        response.headers.setdefault("Access-Control-Allow-Headers", "*")
    return response

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

if (settings.STORAGE_BACKEND or "").lower() == "local":
    # Serve locally stored uploaded files (videos, thumbnails, branding assets).
    # Mounted apps do not inherit parent middleware, so we attach CORS headers here.
    storage_dir = Path(settings.LOCAL_STORAGE_DIR)
    storage_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/storage", CORSStaticFiles(directory=str(storage_dir)), name="storage")


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "social-media-ai-backend"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Social Media AI SaaS API",
        "docs": "/docs",
        "health": "/health",
    }
