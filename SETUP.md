# Setup Guide

This guide will help you set up the Social Media AI SaaS platform locally.

There are two setup methods:
1. **Docker Setup (Recommended)** - Quick setup using containers
2. **Manual Setup** - Install each service individually

---

## Docker Setup (Recommended)

Docker is the easiest way to get the full stack running locally. It includes all services pre-configured.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
- Git

### Step 1: Configure Environment

```bash
# Copy the Docker environment template
cp .env.docker.example .env.docker
```

Edit `.env.docker` with your values:

| Variable | Required | How to Get |
|----------|----------|------------|
| SUPABASE_URL | Yes | [Supabase Dashboard](https://supabase.com) > Settings > API |
| SUPABASE_KEY | Yes | Supabase Dashboard > Settings > API (service_role key) |
| SUPABASE_JWT_SECRET | Yes | Supabase Dashboard > Settings > API |
| NUXT_PUBLIC_SUPABASE_URL | Yes | Same as SUPABASE_URL |
| NUXT_PUBLIC_SUPABASE_ANON_KEY | Yes | Supabase Dashboard > Settings > API (anon key) |
| GEMINI_API_KEY | Yes | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| OPENAI_API_KEY | Yes | [OpenAI Platform](https://platform.openai.com/api-keys) |
| ENCRYPTION_KEY | Yes | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| SECRET_KEY | Yes | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |

### Step 2: Start All Services

```bash
# Start the full stack
docker-compose up -d

# Wait for services to be healthy (about 60 seconds)
docker-compose ps

# Run database migrations
docker-compose exec backend alembic upgrade head
```

### Step 3: Access the Application

| Service | URL |
|---------|-----|
| Application (via nginx) | http://localhost |
| Frontend (direct) | http://localhost:3000 |
| Backend API (direct) | http://localhost:8000 |
| API Documentation | http://localhost/docs |
| Health Check | http://localhost/health |

### Docker Commands Reference

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery-worker

# Rebuild after Dockerfile changes
docker-compose up -d --build

# Reset database (delete volumes)
docker-compose down -v

# Open shell in container
docker-compose exec backend bash
docker-compose exec frontend sh

# Run a command in container
docker-compose exec backend python -c "print('hello')"
```

### Testing Production Build Locally

To test with production-like builds:

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### Docker Troubleshooting

1. **Container won't start**
   ```bash
   # Check logs for errors
   docker-compose logs backend
   
   # Restart specific service
   docker-compose restart backend
   ```

2. **Database connection issues**
   ```bash
   # Check if postgres is healthy
   docker-compose ps postgres
   
   # Check postgres logs
   docker-compose logs postgres
   ```

3. **Out of disk space**
   ```bash
   # Clean up unused Docker resources
   docker system prune -a
   ```

4. **Port already in use**
   ```bash
   # Stop conflicting services or change ports in docker-compose.yml
   # Check what's using the port:
   netstat -ano | findstr :80      # Windows
   lsof -i :80                      # Linux/Mac
   ```

---

## Manual Setup

If you prefer not to use Docker, follow this section.

### Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL 15+ (or Supabase account)
- Redis 7+
- FFmpeg

### 1. Environment Files

The `.env` files have been created from the examples. You need to fill in your actual values:

#### Backend (`backend/.env`)
- **DATABASE_URL**: Your PostgreSQL connection string (or Supabase connection string)
- **REDIS_URL**: Your Redis connection string (default: `redis://localhost:6379`)
- **SUPABASE_URL**: Your Supabase project URL
- **SUPABASE_KEY**: Your Supabase service role key
- **SUPABASE_JWT_SECRET**: Your Supabase JWT secret
- **GEMINI_API_KEY**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **OPENAI_API_KEY**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **ENCRYPTION_KEY**: Generate a 32-byte key (use: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- **SECRET_KEY**: Generate a secret key for JWT (use: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)

#### Frontend (`frontend/.env`)
- **NUXT_PUBLIC_API_URL**: Backend API URL (default: `http://localhost:8000/api/v1`)
- **NUXT_PUBLIC_SUPABASE_URL**: Your Supabase project URL
- **NUXT_PUBLIC_SUPABASE_ANON_KEY**: Your Supabase anonymous key (not the service key!)

### 2. Database Setup

#### Option A: Using Supabase (Recommended)

1. Create a project at [supabase.com](https://supabase.com)
2. Get your connection string from Settings > Database
3. Update `DATABASE_URL` in `backend/.env`
4. Run migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```

#### Option B: Local PostgreSQL

1. Install PostgreSQL 15+
2. Create a database:
   ```sql
   CREATE DATABASE socialmediaai;
   ```
3. Update `DATABASE_URL` in `backend/.env`
4. Run migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```

### 3. Redis Setup

#### Option A: Local Redis

1. Install Redis 7+
2. Start Redis:
   ```bash
   redis-server
   ```
3. Default URL `redis://localhost:6379` should work

#### Option B: Redis Cloud

1. Sign up at [Redis Cloud](https://redis.com/try-free/)
2. Get your connection string
3. Update `REDIS_URL` in `backend/.env`

### 4. Start Backend

```bash
cd backend
# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source venv/bin/activate  # Linux/Mac

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### 5. Start Celery Worker (Optional, for background tasks)

In a new terminal:

```bash
cd backend
.\venv\Scripts\Activate.ps1
celery -A app.workers.celery_app worker --loglevel=info
```

### 6. Start Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at:
- http://localhost:3000

## Verification

### Backend Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","service":"social-media-ai-backend"}
```

### Frontend Check
Open http://localhost:3000 in your browser. You should see the application (may show Supabase error until credentials are configured).

## Troubleshooting

### Backend Issues

1. **Database Connection Error**
   - Verify `DATABASE_URL` is correct
   - Ensure PostgreSQL/Supabase is running
   - Check database exists

2. **Redis Connection Error**
   - Verify `REDIS_URL` is correct
   - Ensure Redis is running
   - Check Redis is accessible

3. **Import Errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt` again

### Frontend Issues

1. **Supabase Error**
   - Verify `NUXT_PUBLIC_SUPABASE_URL` and `NUXT_PUBLIC_SUPABASE_ANON_KEY` are set
   - Ensure you're using the **anon key**, not the service key
   - Check Supabase project is active

2. **API Connection Error**
   - Verify backend is running
   - Check `NUXT_PUBLIC_API_URL` matches backend URL
   - Check CORS settings in backend

## Next Steps

1. Configure your Supabase project:
   - Set up authentication providers
   - Create storage buckets for videos
   - Configure Row Level Security (RLS) policies

2. Get API Keys:
   - [Google Gemini API](https://makersuite.google.com/app/apikey)
   - [OpenAI API](https://platform.openai.com/api-keys)

3. Set up OAuth Apps (for social media publishing):
   - [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
   - [TikTok Marketing API](https://developers.tiktok.com/doc/marketing-api-overview)
   - [YouTube Data API](https://developers.google.com/youtube/v3)
   - [Facebook Graph API](https://developers.facebook.com/docs/graph-api)

4. Test the application:
   - Register a new user
   - Upload a test video
   - Generate patterns and strategies

## Production Deployment

### Render Deployment

This project is configured for deployment on Render using `render.yaml`.

1. **Connect Repository**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Create a new Blueprint Instance
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`

2. **Configure Environment Variables**
   
   Set these in each service's environment settings:
   - `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_JWT_SECRET`
   - `GEMINI_API_KEY`, `OPENAI_API_KEY`
   - `ENCRYPTION_KEY`, `SECRET_KEY`
   - OAuth credentials (if using social publishing)

3. **Deploy**
   - Render will automatically deploy on push to main branch

### CI/CD Pipeline

The project includes GitHub Actions for automated testing and deployment:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | PR/Push to main/develop | Lint, test, build verification |
| `deploy-staging.yml` | Push to develop | Deploy to staging |
| `deploy-production.yml` | Push to main | Deploy to production |

To enable CI/CD:

1. **Add GitHub Repository Secrets/Variables:**
   ```
   # Render deploy hook URLs
   RENDER_BACKEND_HOOK_URL
   RENDER_FRONTEND_HOOK_URL
   RENDER_WORKER_HOOK_URL
   RENDER_BEAT_HOOK_URL
   
   # Health check URLs
   PRODUCTION_BACKEND_URL
   PRODUCTION_FRONTEND_URL
   ```

2. **Create GitHub Environments:**
   - `staging`
   - `production`
   - `production-approval` (for manual approval gate)

3. **Get Deploy Hook URLs:**
   - Go to each Render service
   - Settings > Deploy Hook
   - Copy the URL

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Render                                │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐   ┌──────────┐   ┌──────────┐  ┌──────────┐  │
│  │ Frontend │   │ Backend  │   │  Worker  │  │   Beat   │  │
│  │ (Nuxt)   │   │ (FastAPI)│   │ (Celery) │  │ (Celery) │  │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘  └────┬─────┘  │
│       │              │              │             │         │
│       └──────────────┼──────────────┼─────────────┘         │
│                      │              │                        │
│               ┌──────┴──────┐  ┌────┴────┐                  │
│               │    Redis    │  │  Supabase│                 │
│               │   (Render)  │  │(External)│                 │
│               └─────────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
```
