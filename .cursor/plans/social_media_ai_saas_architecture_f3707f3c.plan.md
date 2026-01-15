---
name: Social Media AI SaaS Architecture
overview: Comprehensive architecture and business plan for an AI-powered social media marketing hub that analyzes video patterns, creates strategies, generates scripts, edits videos, and optimizes performance through learning loops.
todos:
  - id: setup-infrastructure
    content: "Set up development infrastructure: Nuxt.js frontend, FastAPI backend, Supabase database, Redis cache"
    status: pending
  - id: implement-auth
    content: Implement authentication system using Supabase Auth with JWT tokens
    status: pending
  - id: create-db-schema
    content: Create database schema migrations for all core tables (users, organizations, patterns, strategies, scripts, videos, posts, analytics)
    status: pending
  - id: build-pattern-service
    content: Build Pattern Analysis Service with Gemini 1.5 Pro integration for video pattern extraction
    status: pending
  - id: build-strategy-service
    content: Build Strategy Generation Service with GPT-4 integration for marketing strategy creation
    status: pending
  - id: build-script-service
    content: Build Script Generation Service for creating filming scripts and instructions
    status: pending
  - id: build-video-editor
    content: Build Video Editing Service using FFmpeg to apply patterns and create variations
    status: pending
  - id: implement-oauth
    content: Implement OAuth authentication service for connecting social media accounts (Instagram, TikTok, YouTube, Facebook) with token encryption and refresh mechanisms
    status: pending
  - id: integrate-social-apis
    content: Integrate social media APIs (Instagram, TikTok, YouTube, Facebook) for autopublish functionality using OAuth tokens
    status: pending
  - id: build-scheduler
    content: Build Scheduling Service with Celery for background task processing
    status: pending
  - id: build-analytics
    content: Build Analytics Service to track performance and update pattern scores
    status: pending
  - id: implement-templates
    content: Implement template system for caching LLM responses and reducing API costs
    status: pending
  - id: build-frontend-dashboard
    content: Build Nuxt.js frontend with dashboard, video upload, analytics, and scheduling UI
    status: pending
  - id: setup-render-deployment
    content: Configure Render deployment for both frontend (Nuxt.js) and backend (FastAPI) services
    status: pending
---

# Social Media AI SaaS - Architecture & Business Plan

## Infrastructure & Deployment

### Hosting Platform: Render

**All services will be hosted on Render**:
- Frontend (Nuxt.js) - Render Static Site or Web Service
- Backend (FastAPI) - Render Web Service
- Celery Workers - Render Background Workers
- Redis - Render Redis (managed service)

### Render Configuration

#### Frontend (Nuxt.js) - Static Site or Web Service

**Option 1: Static Site (Recommended for SSR/SSG)**
- Build command: `npm run build`
- Publish directory: `.output/public` (Nuxt 3)
- Environment: Node.js 20
- Auto-deploy from Git

**Option 2: Web Service (For SSR)**
- Build command: `npm run build`
- Start command: `node .output/server/index.mjs`
- Environment: Node.js 20
- Instance type: Starter ($7/month) or Standard ($25/month)

**Render Configuration File** (`render.yaml`):
```yaml
services:
  # Frontend - Nuxt.js
  - type: web
    name: social-media-ai-frontend
    env: node
    buildCommand: npm install && npm run build
    startCommand: node .output/server/index.mjs
    envVars:
      - key: NODE_ENV
        value: production
      - key: API_URL
        fromService:
          type: web
          name: social-media-ai-backend
          property: host
    healthCheckPath: /health

  # Backend - FastAPI
  - type: web
    name: social-media-ai-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: social-media-ai-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: social-media-ai-redis
          property: connectionString
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: ENCRYPTION_KEY
        sync: false
    healthCheckPath: /health

  # Celery Worker - Video Processing
  - type: worker
    name: social-media-ai-worker
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: celery -A app.workers.celery_app worker --loglevel=info --concurrency=2
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: social-media-ai-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: social-media-ai-redis
          property: connectionString

databases:
  - name: social-media-ai-db
    databaseName: socialmediaai
    user: socialmediaai
    plan: starter  # PostgreSQL 15

services:
  - type: redis
    name: social-media-ai-redis
    plan: starter  # 25MB memory
```

### Environment Variables

**Frontend (.env.production)**:
```env
NUXT_PUBLIC_API_URL=https://social-media-ai-backend.onrender.com
NUXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NUXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

**Backend (.env)**:
```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://red-xxx:6379

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-key
SUPABASE_JWT_SECRET=your-jwt-secret

# AI APIs
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key
GROK_API_KEY=your-grok-key

# OAuth (Social Media)
INSTAGRAM_CLIENT_ID=your-instagram-client-id
INSTAGRAM_CLIENT_SECRET=your-instagram-client-secret
TIKTOK_CLIENT_KEY=your-tiktok-key
TIKTOK_CLIENT_SECRET=your-tiktok-secret
YOUTUBE_CLIENT_ID=your-youtube-client-id
YOUTUBE_CLIENT_SECRET=your-youtube-client-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret

# Security
ENCRYPTION_KEY=your-32-byte-encryption-key
SECRET_KEY=your-secret-key-for-jwt

# Render
PORT=8000  # Auto-set by Render
```

### Render-Specific Considerations

**1. Build & Deploy**
- Auto-deploy from Git (GitHub/GitLab/Bitbucket)
- Build logs available in Render dashboard
- Rollback capability for failed deployments

**2. Scaling**
- **Frontend**: Can scale horizontally (multiple instances)
- **Backend**: Scale based on traffic (Starter → Standard → Pro)
- **Workers**: Scale independently based on queue depth
- **Redis**: Upgrade plan as needed (Starter → Standard)

**3. Health Checks**
- Frontend: `/health` endpoint
- Backend: `/health` endpoint (FastAPI)
- Render monitors health and restarts unhealthy services

**4. Persistent Storage**
- PostgreSQL: Managed by Render (automatic backups)
- Redis: Managed by Render (persistent)
- File Storage: Use Supabase Storage or S3 (not Render disk)

**5. Background Workers (Celery)**
- Deploy as separate Render Background Worker service
- Connects to same Redis instance as backend
- Auto-restarts on failure
- Monitor via Render logs

### Cost Estimation (Render)

**Monthly Costs**:

- **Frontend (Web Service)**: $7/month (Starter) or $25/month (Standard)
- **Backend (Web Service)**: $7/month (Starter) or $25/month (Standard)
- **Celery Worker**: $7/month (Starter) or $25/month (Standard)
- **PostgreSQL**: $7/month (Starter, 1GB) or $20/month (Standard, 10GB)
- **Redis**: $10/month (Starter, 25MB) or $15/month (Standard, 100MB)

**Total (Starter tier)**: ~$38/month
**Total (Standard tier)**: ~$110/month

**Note**: Costs scale with usage. Start with Starter tier, upgrade as needed.

### Deployment Process

1. **Initial Setup**:
   ```bash
   # Connect GitHub repo to Render
   # Render will auto-detect services from render.yaml
   ```

2. **Environment Variables**:
   - Set all environment variables in Render dashboard
   - Use Render's environment variable management
   - Mark sensitive vars as "Secret"

3. **Database Setup**:
   - Create PostgreSQL database in Render
   - Run migrations: `alembic upgrade head` (via Render shell or CI/CD)

4. **Deploy**:
   - Push to main branch → Auto-deploy
   - Monitor build logs
   - Verify health checks pass

5. **Custom Domain**:
   - Add custom domain in Render dashboard
   - Configure DNS (CNAME to Render URL)
   - SSL automatically provisioned by Render

### Render vs Other Platforms

**Advantages of Render**:
- ✅ Simple configuration (render.yaml)
- ✅ Auto SSL certificates
- ✅ Managed PostgreSQL and Redis
- ✅ Background workers support
- ✅ Git-based deployments
- ✅ Health checks and auto-restart
- ✅ Free tier for testing

**Considerations**:
- ⚠️ Services sleep after 15min inactivity (Free tier) - upgrade to paid
- ⚠️ Cold starts on free tier can be slow
- ⚠️ Video processing may need larger instances

### Alternative: Render + External Services

If Render's limitations become an issue:
- **Video Processing**: Consider separate Render worker with more RAM
- **File Storage**: Use Supabase Storage (included) or AWS S3
- **CDN**: Use Cloudflare (free) in front of Render

---

## Next Steps

1. **Set up Render account and connect Git repository**
2. **Create render.yaml configuration file**
3. **Set up PostgreSQL and Redis on Render**
4. **Configure environment variables**
5. **Deploy frontend and backend services**
6. **Set up Celery worker service**
7. **Configure custom domain and SSL**
8. **Set up monitoring and alerts**

---

