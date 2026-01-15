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
- **Render** - Cloud hosting
- **Supabase** - Database, Auth, Storage

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
│   └── nuxt.config.ts       # Nuxt configuration
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
│   └── requirements.txt
├── render.yaml              # Render deployment config
├── PRD.md                   # Product requirements
└── README.md
```

## Getting Started

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

## Deployment

This project is configured for deployment on Render using the `render.yaml` blueprint.

1. Connect your GitHub repo to Render
2. Render will auto-detect the `render.yaml` configuration
3. Set environment variables in Render dashboard
4. Deploy!

## License

MIT

## Contributing

Contributions are welcome! Please read the contributing guidelines first.
