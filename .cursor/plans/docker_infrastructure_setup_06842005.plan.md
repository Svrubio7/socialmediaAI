---
name: Docker Infrastructure Setup
overview: Set up complete Docker containerization with nginx reverse proxy, development docker-compose, and CI/CD pipelines that work seamlessly with Render deployment.
todos:
  - id: dockerfiles
    content: Create Dockerfiles for backend (multi-stage with FFmpeg) and frontend (multi-stage Node.js)
    status: pending
  - id: nginx-config
    content: Create nginx directory with reverse proxy configuration for local development
    status: pending
  - id: docker-compose
    content: Update docker-compose.yml with all services (nginx, frontend, backend, celery-worker, celery-beat, redis, postgres)
    status: pending
  - id: docker-compose-prod
    content: Create docker-compose.prod.yml for production-like local testing
    status: pending
  - id: dockerignore
    content: Create .dockerignore files to exclude node_modules, venv, .env files, etc.
    status: pending
  - id: env-docker
    content: Create .env.docker example file with container-specific environment variables
    status: pending
  - id: ci-workflow
    content: Create .github/workflows/ci.yml for linting, testing, and build verification on PRs
    status: pending
  - id: deploy-workflows
    content: Create staging and production deployment workflows with Render integration
    status: pending
  - id: readme-update
    content: Update README.md and SETUP.md with Docker development instructions
    status: pending
isProject: false
---

# Docker Infrastructure and CI/CD Setup

## Current State Analysis

The project already has:

- A basic `docker-compose.yml` with only Redis service
- A complete `render.yaml` for Render deployment (frontend, backend, 2 workers, Redis, PostgreSQL)
- Backend: FastAPI with Celery workers
- Frontend: Nuxt.js 3 with SSR

**Missing infrastructure:**

- Dockerfiles for backend and frontend
- Complete docker-compose for local development
- nginx reverse proxy configuration
- CI/CD pipelines (GitHub Actions)

---

## Architecture Overview

```mermaid
flowchart TB
    subgraph local [Local Development]
        nginx[nginx:80/443]
        nginx --> frontend_dev[Frontend Container:3000]
        nginx --> backend_dev[Backend Container:8000]
        backend_dev --> redis_dev[Redis:6379]
        backend_dev --> postgres_dev[PostgreSQL:5432]
        celery_worker[Celery Worker] --> redis_dev
        celery_beat[Celery Beat] --> redis_dev
    end

    subgraph render [Render Production]
        render_frontend[Frontend Web Service]
        render_backend[Backend Web Service]
        render_worker[Celery Worker]
        render_beat[Celery Beat]
        render_redis[Managed Redis]
        supabase_db[Supabase PostgreSQL]
        supabase_storage[Supabase Storage]
    end
```



---

## File Structure to Create

```
socialmediaAI/
├── backend/
│   └── Dockerfile                 # Multi-stage Python build
├── frontend/
│   └── Dockerfile                 # Multi-stage Node build
├── nginx/
│   ├── nginx.conf                 # Main nginx config
│   ├── nginx.dev.conf             # Development config
│   └── ssl/                       # SSL certificates (gitignored)
├── docker-compose.yml             # Full local dev stack (updated)
├── docker-compose.prod.yml        # Production-like local testing
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Test and lint on PR
│       ├── deploy-staging.yml     # Deploy to staging
│       └── deploy-production.yml  # Deploy to production
├── .dockerignore                  # Docker ignore file
└── render.yaml                    # Existing (minor updates)
```

---

## Implementation Details

### 1. Backend Dockerfile

Location: `[backend/Dockerfile](backend/Dockerfile)`

Key features:

- Multi-stage build (builder + runtime)
- Python 3.11-slim base image
- FFmpeg installation for video processing
- Non-root user for security
- Health check support
- Optimized layer caching

```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Runtime stage
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg --no-install-recommends
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*
COPY app/ ./app/
EXPOSE 8000
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker"]
```

### 2. Frontend Dockerfile

Location: `[frontend/Dockerfile](frontend/Dockerfile)`

Key features:

- Multi-stage build (deps, builder, runtime)
- Node.js 20-alpine base
- SSR output optimization
- Minimal production image

```dockerfile
# Dependencies stage
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Runtime stage
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/.output ./.output
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
```

### 3. nginx Configuration

Location: `[nginx/nginx.conf](nginx/nginx.conf)`

Features:

- Reverse proxy to frontend and backend
- API routing (`/api/*` -> backend)
- WebSocket support for hot reload (dev)
- Gzip compression
- Security headers
- Static file caching

```nginx
upstream frontend {
    server frontend:3000;
}
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 4. docker-compose.yml (Complete)

Update the existing file with all services:

Services:

- **nginx**: Reverse proxy (port 80)
- **frontend**: Nuxt.js SSR app
- **backend**: FastAPI application
- **celery-worker**: Background video processing
- **celery-beat**: Scheduled tasks
- **redis**: Cache and Celery broker
- **postgres**: Local database (mirrors Supabase)

Features:

- Volume mounts for hot reload in development
- Health checks for all services
- Network isolation
- Environment variable files (`.env.docker`)

### 5. CI/CD Pipelines (GitHub Actions)

#### ci.yml - Continuous Integration

- Triggered on: PR to main
- Jobs:
  - Lint backend (ruff, black, mypy)
  - Lint frontend (eslint, prettier)
  - Test backend (pytest)
  - Test frontend (vitest - if configured)
  - Build Docker images (verify builds work)

#### deploy-staging.yml - Staging Deployment

- Triggered on: Push to `develop` branch
- Uses Render deploy hooks or GitHub integration
- Runs integration tests after deploy

#### deploy-production.yml - Production Deployment

- Triggered on: Push to `main` branch
- Manual approval gate (optional)
- Deploys via Render deploy hook

---

## Environment Configuration

### Local Development (.env.docker)

```env
# Database (local PostgreSQL)
DATABASE_URL=postgresql://socialmediaai:password@postgres:5432/socialmediaai

# Redis (local)
REDIS_URL=redis://redis:6379

# Other vars loaded from .env files
```

### Render Integration

The existing `render.yaml` is well-configured. Minor updates:

- Add `dockerfilePath` if we want Render to use our Dockerfiles
- Or keep current setup (Render builds from source)

---

## Development Workflow

1. **Start all services:**
  ```bash
   docker-compose up -d
  ```
2. **View logs:**
  ```bash
   docker-compose logs -f backend
  ```
3. **Run migrations:**
  ```bash
   docker-compose exec backend alembic upgrade head
  ```
4. **Access:**
  - App: [http://localhost](http://localhost) (nginx)
  - API Docs: [http://localhost/docs](http://localhost/docs)
  - Direct frontend: [http://localhost:3000](http://localhost:3000)
  - Direct backend: [http://localhost:8000](http://localhost:8000)

---

## Render Compatibility Notes

Render can work with this Docker setup in two ways:

1. **Current approach (recommended for Render):** Keep using `render.yaml` with buildCommand/startCommand - Render builds from source code directly
2. **Docker approach:** Update `render.yaml` to use Docker images:
  ```yaml
   services:
     - type: web
       name: social-media-ai-backend
       dockerfilePath: ./backend/Dockerfile
  ```

For this project, I recommend keeping the current Render approach (source builds) since:

- Render optimizes builds for their infrastructure
- Avoids managing a container registry
- The Docker setup is primarily for local development

---

## Security Considerations

- Non-root users in containers
- Secrets managed via environment variables (never in images)
- `.dockerignore` to exclude sensitive files
- Network isolation between services
- Health checks for reliability

