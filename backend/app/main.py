"""
Social Media AI SaaS - FastAPI Backend
Main application entry point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    print("Starting Social Media AI Backend...")
    yield
    # Shutdown
    print("Shutting down Social Media AI Backend...")


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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


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
