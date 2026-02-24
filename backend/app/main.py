"""
Social Media AI SaaS - FastAPI Backend
Main application entry point
"""

from contextlib import asynccontextmanager
import logging
import mimetypes
import re
import time
import uuid
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.services.metrics_lite import get_metrics_snapshot

# Ensure common video types are served with correct mime types (Windows often lacks these).
mimetypes.add_type("video/mp4", ".mp4")
mimetypes.add_type("video/mp4", ".m4v")
mimetypes.add_type("video/quicktime", ".mov")

logger = logging.getLogger("app.request")


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
raw_cors_origin_regex = (settings.CORS_ORIGIN_REGEX or "").strip()
compiled_cors_origin_regex = (
    re.compile(raw_cors_origin_regex) if raw_cors_origin_regex else None
)
if allow_all:
    # In dev or when CORS_ORIGINS="*", allow any origin.
    cors_kwargs["allow_origin_regex"] = ".*"
else:
    cors_kwargs["allow_origins"] = settings.cors_origins_list
    if raw_cors_origin_regex:
        cors_kwargs["allow_origin_regex"] = raw_cors_origin_regex

app.add_middleware(CORSMiddleware, **cors_kwargs)


@app.middleware("http")
async def attach_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers.setdefault("X-Request-ID", request_id)
    return response


def _is_allowed_origin(origin: str) -> bool:
    if not origin:
        return False
    if allow_all:
        return True
    if origin in settings.cors_origins_list:
        return True
    if compiled_cors_origin_regex and compiled_cors_origin_regex.match(origin):
        return True
    return False


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started = time.perf_counter()
    request_id = request.headers.get("X-Request-ID") or "-"
    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.exception(
            "request method=%s path=%s status=500 request_id=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            request_id,
            elapsed_ms,
        )
        raise

    elapsed_ms = (time.perf_counter() - started) * 1000
    request_id = response.headers.get("X-Request-ID", request_id)
    logger.info(
        "request method=%s path=%s status=%s request_id=%s duration_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        request_id,
        elapsed_ms,
    )
    return response


@app.middleware("http")
async def ensure_cors_headers(request: Request, call_next):
    """
    Ensure CORS headers are present even on error responses.
    CORSMiddleware should handle this, but we set fallbacks if headers are missing.
    """
    response = await call_next(request)
    origin = request.headers.get("origin")
    if origin and _is_allowed_origin(origin):
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


@app.get("/api/health")
async def api_health_check():
    """Health endpoint under /api for unified same-origin routing contracts."""
    return await health_check()


@app.get("/api/metrics-lite")
async def api_metrics_lite():
    """Mirror metrics-lite under /api for same-origin reverse-proxy contracts."""
    return get_metrics_snapshot()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Social Media AI SaaS API",
        "docs": "/docs",
        "health": "/health",
    }
