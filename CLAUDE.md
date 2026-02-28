# CLAUDE.md — Project Intelligence

## Architecture

Monorepo with 3 services unified behind nginx in production:

```
Production (Docker)                  Local Dev (native)
┌─────────────────────┐
│ nginx :3000         │
│  ├─ /      → Nuxt   │  ←→  Nuxt      http://localhost:3001
│  ├─ /editor → Next   │  ←→  Editor    http://localhost:3002
│  └─ /api   → FastAPI │  ←→  Backend   http://localhost:8000
└─────────────────────┘
```

- **Frontend:** Nuxt 3 (Vue) — `frontend/` — npm
- **Editor:** Next.js (React, Elevo Editor) — `apps/elevo-editor/` — bun + turborepo
- **Backend:** FastAPI (Python) — `backend/` — uvicorn, SQLAlchemy, Celery
- **Database:** Supabase (cloud PostgreSQL) — no local DB needed
- **Redis:** Only needed for Celery workers (video processing); optional in local dev

## Quick Start (Local Dev)

```bash
npm run dev        # Starts all 3 services with hot reload
```

| Service | URL | Hot reload |
|---------|-----|------------|
| Nuxt frontend | http://localhost:3001 | Instant (HMR) |
| Editor | http://localhost:3002 | Instant (Turbopack) |
| Backend API | http://localhost:8000 | Auto-restart on save |
| API Docs | http://localhost:8000/docs | Swagger UI |

## Commands

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start all 3 services (hot reload) |
| `npm run dev:frontend` | Nuxt only |
| `npm run dev:editor` | Editor only |
| `npm run dev:backend` | FastAPI only |
| `npm run dev:redis` | Start Redis container (for Celery) |
| `npm run dev:redis:stop` | Stop Redis container |
| `npm run dev:docker` | Full Docker build (production-like) |

## Environment Files

| File | Purpose | Gitignored |
|------|---------|------------|
| `backend/.env` | Backend secrets (DB, Supabase service key, API keys) | Yes |
| `frontend/.env` | Frontend public config (API URL = `/api/v1` for production) | Yes |
| `frontend/.env.local` | Local dev override (API URL = `http://localhost:8000/api/v1`) | Yes |
| `apps/elevo-editor/apps/web/.env.local` | Editor local dev overrides | Yes |
| `.env` | Root shared vars for Docker Compose | Yes |

## Key Patterns

- **API URL:** `/api/v1` in production (nginx proxy) vs `http://localhost:8000/api/v1` in local dev
- **Editor basePath:** `/editor` in production (nginx route) vs empty in local dev (standalone)
- **CORS:** Backend allows localhost:3001 and localhost:3002 by default
- **Theme:** Shared localStorage key `elevo-theme` syncs dark/light across Nuxt + Editor
- **Branding:** "Elevo" (not "ElevoAI"). Logo: `elevo_just_logo.png`
- **Palette:** Onyx #0A0A09, Lime Cream #E1F690, Electric Aqua #7CFBFD, Papaya Whip #FFF0D9, White #FFFFFF

## Port Assignments

| Service | Local Dev | Docker (internal) | Docker (exposed) |
|---------|-----------|-------------------|------------------|
| nginx | N/A | 3000 | 3000 |
| Nuxt | 3001 | 3001 | via nginx |
| Editor | 3002 | 3002 | via nginx |
| FastAPI | 8000 | 8000 | via nginx |
| Redis | 6379 | N/A | N/A |

## Package Managers

- Root: npm
- Frontend (`frontend/`): npm
- Editor (`apps/elevo-editor/`): bun
- Backend (`backend/`): pip (venv at `backend/venv/`)

## Deployment

- **Platform:** Render.com (see `render.yaml`)
- **CI/CD:** GitHub Actions (`.github/workflows/`)
- **Branches:** `main` → production, `develop` → staging
- **Docker:** Single container with nginx + supervisord managing all services
