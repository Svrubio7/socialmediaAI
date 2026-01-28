# Social Media AI SaaS

AI-powered social media marketing hub for video pattern analysis, strategy generation, automated editing, and multi-platform publishing.

## Features

- **Video Pattern Analysis**: AI analyzes your videos to identify successful patterns (hooks, pacing, cuts, text overlays)
- **Strategy Generation**: Get AI-generated marketing strategies based on your content patterns
- **Script Creation**: Detailed filming and editing scripts with timing and visual instructions
- **Automated Video Editing**: Apply patterns to create platform-optimized video variations
- **Multi-Platform Publishing**: Publish to Instagram, TikTok, YouTube, and Facebook
- **Performance Analytics**: Track performance across platforms with learning loops

## Tech Stack

### Frontend
- **Nuxt.js 3** - Vue.js framework with SSR/SSG
- **Tailwind CSS** - Utility-first CSS framework
- **Pinia** - State management
- **Supabase** - Authentication

### Backend
- **FastAPI** - Python web framework
- **SQLAlchemy** - ORM
- **Celery** - Task queue
- **Redis** - Cache and Celery broker
- **PostgreSQL** - Database (via Supabase)

### AI Services
- **Google Gemini 1.5 Pro** - Video pattern analysis
- **OpenAI GPT-4** - Strategy and script generation
- **FFmpeg** - Video processing

### Infrastructure
- **Docker** – Local development (frontend, backend, Redis, Celery; no nginx)
- **Render** – Production hosting
- **Supabase** – Database and Auth only (no local Postgres)
- **GitHub Actions** – CI/CD pipelines

## Project Structure

```
socialmediaAI/
├── frontend/                 # Nuxt.js frontend
│   ├── assets/              # Static assets
│   ├── components/          # Vue components
│   ├── composables/         # Vue composables
│   ├── layouts/             # Layout components
│   ├── middleware/          # Route middleware
│   ├── pages/               # Route pages
│   ├── stores/              # Pinia stores
│   ├── nuxt.config.ts       # Nuxt configuration
│   └── Dockerfile           # Frontend container
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/             # API endpoints
│   │   ├── core/            # Configuration
│   │   ├── db/              # Database
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Utilities
│   │   └── workers/         # Celery tasks
│   ├── requirements.txt
│   └── Dockerfile           # Backend container
├── .github/workflows/        # CI/CD pipelines
│   ├── ci.yml               # Continuous integration
│   ├── deploy-staging.yml   # Staging deployment
│   └── deploy-production.yml # Production deployment
├── docker-compose.yml        # Local development stack
├── docker-compose.prod.yml   # Production-like testing
├── render.yaml               # Render deployment config
├── PRD.md                    # Product requirements
└── README.md
```

## Getting Started

**Database**: Supabase only (no local Postgres). **Production**: Render.  
For full setup (development vs production), see **[SETUP.md](SETUP.md)**.

There are two ways to run this project locally:
1. **Docker (Recommended)** – Frontend, backend, Redis, Celery; no nginx; use :3000 and :8000
2. **Manual Setup** – Install each service individually

---

## Option 1: Docker Development (Recommended)

### Prerequisites
- Docker Desktop (includes Docker Compose)
- Git
- Supabase project (for database and auth)

### Quick Start

1. **Clone and configure:** See [SETUP.md](SETUP.md) for env files (`backend/.env`, `frontend/.env`). Set `DATABASE_URL` (Supabase), `REDIS_URL`, Supabase keys, and `NUXT_PUBLIC_API_URL=http://localhost:8000/api/v1`.

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Run database migrations:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend / API Docs: http://localhost:8000 and http://localhost:8000/docs

### Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f                    # All services
docker-compose logs -f backend            # Specific service

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Run migrations
docker-compose exec backend alembic upgrade head

# Open shell in container
docker-compose exec backend bash
docker-compose exec frontend sh

# Reset everything (including volumes)
docker-compose down -v
```

### Production-like Testing

To test with production builds locally:

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## Option 2: Manual Setup

### Prerequisites

- Node.js 20+
- Python 3.11+
- PostgreSQL 15+ (or Supabase account)
- Redis 7+
- FFmpeg

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy environment file and configure:
   ```bash
   cp env.example .env
   # Edit .env with your values
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

7. Start Celery worker (in another terminal):
   ```bash
   celery -A app.workers.celery_app worker --loglevel=info
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy environment file and configure:
   ```bash
   cp env.example .env
   # Edit .env with your values
   ```

4. Start development server:
   ```bash
   npm run dev
   ```

5. Open http://localhost:3000 in your browser

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

### Backend

| Variable | Description |
|----------|-------------|
| DATABASE_URL | PostgreSQL connection string |
| REDIS_URL | Redis connection string |
| SUPABASE_URL | Supabase project URL |
| SUPABASE_KEY | Supabase service key |
| SUPABASE_JWT_SECRET | Supabase JWT secret |
| GEMINI_API_KEY | Google Gemini API key |
| OPENAI_API_KEY | OpenAI API key |
| ENCRYPTION_KEY | 32-byte key for token encryption |
| SECRET_KEY | Secret key for JWT |

### Frontend

| Variable | Description |
|----------|-------------|
| NUXT_PUBLIC_API_URL | Backend API URL |
| NUXT_PUBLIC_SUPABASE_URL | Supabase project URL |
| NUXT_PUBLIC_SUPABASE_ANON_KEY | Supabase anon key |

## CI/CD Pipeline

This project includes GitHub Actions workflows for continuous integration and deployment.

### Workflows

| Workflow | Trigger | Description |
|----------|---------|-------------|
| `ci.yml` | PR to main/develop | Lint, test, and build verification |
| `deploy-staging.yml` | Push to develop | Deploy to staging environment |
| `deploy-production.yml` | Push to main | Deploy to production (with approval) |

### CI Checks
- Backend: Ruff linting, Black formatting, mypy type checking, pytest
- Frontend: ESLint, TypeScript check, build verification
- Docker: Image build verification
- Security: Trivy vulnerability scanning

### Setting Up CI/CD

1. **GitHub Secrets/Variables** - Add these in your repository settings:
   ```
   # Staging
   RENDER_BACKEND_STAGING_HOOK_URL
   RENDER_FRONTEND_STAGING_HOOK_URL
   STAGING_BACKEND_URL
   STAGING_FRONTEND_URL
   
   # Production
   RENDER_BACKEND_HOOK_URL
   RENDER_FRONTEND_HOOK_URL
   PRODUCTION_BACKEND_URL
   PRODUCTION_FRONTEND_URL
   ```

2. **GitHub Environments** - Create `staging`, `production`, and `production-approval` environments

3. **Render Deploy Hooks** - Get deploy hook URLs from each Render service's settings

## Deployment

This project is configured for deployment on Render using the `render.yaml` blueprint.

### Render Setup

1. Connect your GitHub repo to Render
2. Render will auto-detect the `render.yaml` configuration
3. Set environment variables in Render Dashboard (see [SETUP.md](SETUP.md)): **DATABASE_URL** (Supabase), **NUXT_PUBLIC_API_URL**, **REDIS_URL** (from Render Redis), **SUPABASE_***, and other secrets. No Render database; Supabase only.
4. Deploy! Migrations run automatically via the backend release command.

### Services Deployed

| Service | Type | Description |
|---------|------|-------------|
| social-media-ai-frontend | Web | Nuxt.js SSR application |
| social-media-ai-backend | Web | FastAPI REST API |
| social-media-ai-worker | Worker | Celery video processing |
| social-media-ai-beat | Worker | Celery scheduled tasks |
| social-media-ai-redis | Redis | Cache and task queue |

## License

MIT

## Contributing

Contributions are welcome! Please read the contributing guidelines first.
