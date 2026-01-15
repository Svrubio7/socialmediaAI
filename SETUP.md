# Setup Guide

This guide will help you set up the Social Media AI SaaS platform locally.

## Quick Start

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

See `render.yaml` for Render deployment configuration. Update environment variables in Render dashboard after deployment.
