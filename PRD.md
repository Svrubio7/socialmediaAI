# Product Requirements Document: Social Media AI SaaS Platform

## 1. Executive Summary

Social Media AI SaaS is an AI-powered social media marketing hub designed to help content creators and marketers optimize their video content strategy through intelligent pattern analysis, automated strategy generation, and performance-driven learning loops. The platform leverages advanced AI models (Gemini 1.5 Pro, GPT-4) to analyze successful video patterns, generate marketing strategies, create filming scripts, and automatically edit videos to match proven patterns.

The core value proposition centers on transforming raw video content into optimized, platform-specific variations that maximize engagement and performance across Instagram, TikTok, YouTube, and Facebook. By learning from performance data, the platform continuously refines its pattern recognition and strategy recommendations, creating a self-improving system that adapts to evolving social media trends.

The MVP goal is to deliver a fully functional platform that enables users to upload videos, receive AI-generated strategies and scripts, create optimized video variations, schedule and publish content across multiple platforms, and track performance analytics—all within a unified, intuitive interface.

**Current implementation state**: Infrastructure is Supabase-only (no Postgres containers; development uses Docker without nginx at :3000/:8000; production is Render-only with release-command migrations). The app includes a dedicated app layout (logo-only header), dashboard with real stats and a Posting Schedule card, Strategies page as an LLM-powered chatbot with result cards (schedule changes, scripts, strategy docs), account area (Profile, Preferences, Branding, Connected Platforms), Schedule page, Strategy and Script detail/export, toasts, timezone in preferences, empty/loading states, breadcrumbs/back links, and Escape-to-close for modals/dropdowns. See Appendix for executed plans.

## 2. Mission

**Mission Statement**: Empower content creators and marketers to maximize their social media impact through AI-driven content optimization, pattern recognition, and automated publishing workflows.

**Core Principles**:
1. **Data-Driven Optimization**: All recommendations and strategies are based on real performance data and proven patterns
2. **Multi-Platform Excellence**: Deliver platform-specific optimizations that respect each platform's unique characteristics and audience expectations
3. **Continuous Learning**: Build a self-improving system that learns from performance metrics and refines strategies over time
4. **User-Centric Design**: Provide intuitive interfaces that make complex AI capabilities accessible to users of all technical levels
5. **Scalable Architecture**: Design for growth with cloud-native infrastructure that can scale seamlessly with user demand

## 3. Target Users

### Primary User Personas

**1. Content Creator (Individual)**
- **Profile**: Solo creator or small team producing video content for personal brand or business
- **Technical Comfort**: Moderate to high comfort with web applications and social media platforms
- **Pain Points**: 
  - Struggling to identify what makes content successful
  - Time-consuming manual video editing and optimization
  - Difficulty maintaining consistent posting schedules
  - Limited understanding of platform-specific best practices
- **Key Needs**: Quick video optimization, pattern insights, automated publishing, performance tracking

**2. Social Media Manager (Agency/Team)**
- **Profile**: Marketing professional managing multiple clients or brand accounts
- **Technical Comfort**: High comfort with SaaS tools and marketing platforms
- **Pain Points**:
  - Managing content across multiple platforms and accounts
  - Scaling content production efficiently
  - Proving ROI and performance improvements
  - Keeping up with platform algorithm changes
- **Key Needs**: Bulk operations, multi-account management, detailed analytics, template systems

**3. Marketing Team Lead**
- **Profile**: Decision-maker responsible for content strategy and team productivity
- **Technical Comfort**: Moderate comfort, relies on team for execution
- **Pain Points**:
  - Lack of data-driven insights for strategy decisions
  - Difficulty measuring content performance impact
  - Need for scalable content production processes
- **Key Needs**: Strategic insights, performance dashboards, ROI metrics, team collaboration features

## 4. MVP Scope

### In Scope (MVP)

#### Core Functionality
- ✅ User authentication and authorization (Supabase Auth with JWT)
- ✅ Video upload and storage (Supabase Storage)
- ✅ AI-powered video pattern analysis (Gemini 1.5 Pro)
- ✅ Marketing strategy generation (GPT-4)
- ✅ Script generation for filming and editing instructions
- ✅ Video editing service (FFmpeg-based pattern application)
- ✅ OAuth integration for social media accounts (Instagram, TikTok, YouTube, Facebook)
- ✅ Automated publishing to connected social media platforms
- ✅ Content scheduling with Celery background workers
- ✅ Performance analytics and pattern scoring updates
- ✅ Template system for caching LLM responses
- ✅ Dashboard UI for managing content, strategies, and analytics
- ✅ App layout (logo-only header, no website nav) for authenticated routes
- ✅ Strategies page as LLM-powered chatbot with result cards (schedule changes, scripts, strategy docs)
- ✅ Chat backend with tool/function calling (schedule, scripts, strategies, videos, Branding, connected platforms)
- ✅ Account area: Profile, Preferences, Branding, Connected Platforms (dropdown in app header)
- ✅ Schedule page (full schedule view; per-platform filter; edit/cancel)
- ✅ Dashboard Posting Schedule card (expandable; link to Schedule page)
- ✅ Branding backend and frontend (user assets: upload, list, delete)
- ✅ Strategy detail page and Script detail/export
- ✅ Toasts (useToast + component) for success/error feedback
- ✅ Timezone in preferences; schedule display/creation in user timezone
- ✅ Empty states and loading states (skeletons/spinners) for lists and modals
- ✅ Breadcrumbs or back links on account and schedule pages
- ✅ Escape to close modals and dropdowns
- ✅ Publish page: connection summary + link to Account > Connected Platforms

#### Technical Infrastructure
- ✅ Nuxt.js frontend with SSR/SSG support
- ✅ FastAPI backend with RESTful API
- ✅ PostgreSQL database (Supabase only; no local Postgres containers) with migrations
- ✅ Redis cache for session management and Celery task queue (Render Redis in production)
- ✅ Celery workers for asynchronous video processing
- ✅ Render deployment configuration (frontend, backend, worker, beat, Redis; no Render DB)
- ✅ Health check endpoints for monitoring
- ✅ Development: Docker Compose without nginx (frontend :3000, backend :8000); DATABASE_URL from backend/.env (Supabase)
- ✅ Production: Render only; CORS from env (comma-separated); backend release command for migrations

#### Integration
- ✅ Supabase Auth integration
- ✅ Supabase Storage for video files
- ✅ Gemini 1.5 Pro API for pattern analysis
- ✅ OpenAI GPT-4 API for strategy generation
- ✅ Instagram Graph API
- ✅ TikTok Marketing API
- ✅ YouTube Data API v3
- ✅ Facebook Graph API

### Out of Scope (Post-MVP)

#### Features Deferred
- ❌ Multi-user collaboration and team workspaces
- ❌ Advanced video editing features (transitions, effects, filters)
- ❌ A/B testing framework for content variations
- ❌ White-label solutions for agencies
- ❌ Mobile applications (iOS/Android)
- ❌ Real-time collaboration on scripts and strategies
- ❌ Custom AI model training
- ❌ Advanced analytics dashboards with custom reports
- ❌ Integration with additional platforms (Twitter/X, LinkedIn, Pinterest)
- ❌ Content calendar with drag-and-drop scheduling
- ❌ Bulk import/export functionality
- ❌ API access for third-party integrations

#### Technical Enhancements
- ❌ CDN integration for video delivery
- ❌ Advanced caching strategies beyond Redis
- ❌ Multi-region deployment
- ❌ Advanced monitoring and alerting (beyond Render defaults)
- ❌ Automated backup and disaster recovery beyond Render defaults
- ❌ Rate limiting and advanced security features (WAF, DDoS protection)

## 5. User Stories

### Primary User Stories

**US-1: Video Pattern Analysis**
- **As a** content creator, **I want to** upload my videos and receive AI-generated insights about successful patterns, **so that** I can understand what makes my best-performing content successful and replicate those patterns.
- **Example**: User uploads a 60-second TikTok video that received 100K views. The system analyzes pacing, hook timing, visual transitions, and identifies that videos with hooks in the first 3 seconds and 3-4 cuts per 10 seconds perform best for this user's audience.

**US-2: Strategy Generation**
- **As a** social media manager, **I want to** receive AI-generated marketing strategies based on my video patterns and target platforms, **so that** I can create content that aligns with proven success patterns.
- **Example**: After analyzing a user's top 10 videos, the system generates a strategy document recommending: "Focus on educational hooks (question format), maintain 2-second cuts, include text overlays for first 5 seconds, optimal posting time: 6-8 PM EST."

**US-3: Script Generation**
- **As a** content creator, **I want to** receive detailed filming scripts and editing instructions based on successful patterns, **so that** I can produce new content efficiently without guessing what will work.
- **Example**: User requests a script for a "5 Tips for Better Sleep" video. System generates: "Hook (0-3s): 'Are you tired of waking up exhausted?' + Visual: Close-up of alarm clock. Tip 1 (3-15s): [Detailed instructions with timing, visuals, and text overlay specifications]..."

**US-4: Automated Video Editing**
- **As a** content creator, **I want to** upload raw footage and have the system automatically apply successful patterns to create optimized variations, **so that** I can quickly produce multiple platform-specific versions without manual editing.
- **Example**: User uploads a 2-minute raw video. System creates: (1) 60-second TikTok version with fast cuts and trending music, (2) 90-second Instagram Reel with text overlays, (3) Full-length YouTube version with intro/outro.

**US-5: Multi-Platform Publishing**
- **As a** social media manager, **I want to** connect my social media accounts and publish content to multiple platforms simultaneously, **so that** I can maintain consistent presence across all channels efficiently.
- **Example**: User connects Instagram, TikTok, and YouTube accounts. After creating optimized variations, user clicks "Publish All" and content is automatically posted to all three platforms with platform-specific captions and hashtags.

**US-6: Content Scheduling**
- **As a** marketing team lead, **I want to** schedule content for future publication across multiple platforms, **so that** I can plan content calendars in advance and maintain consistent posting schedules.
- **Example**: User creates 10 video variations and schedules them to publish daily at 6 PM EST across Instagram and TikTok for the next 10 days, with automatic hashtag optimization per platform.

**US-7: Performance Analytics**
- **As a** content creator, **I want to** view detailed analytics about my published content's performance, **so that** I can understand what's working and make data-driven decisions about future content.
- **Example**: Dashboard shows: "Video 'Morning Routine Tips' - TikTok: 50K views, 5K likes, 2% engagement rate (above average). Pattern match: 92%. Recommended: Create similar content focusing on morning routine variations."

**US-8: Pattern Learning Loop**
- **As a** platform user, **I want** the system to automatically update pattern scores based on performance data, **so that** recommendations improve over time and reflect the latest trends.
- **Example**: System initially recommended 3-second hooks, but after analyzing 50 videos, discovers that 2-second hooks perform 15% better for this user's niche. System automatically updates pattern scores and future recommendations.

### Technical User Stories

**US-T1: Authentication**
- **As a** system administrator, **I want** users to authenticate via Supabase Auth with JWT tokens, **so that** user sessions are secure and scalable.

**US-T2: Background Processing**
- **As a** system, **I want** video processing tasks to run asynchronously via Celery workers, **so that** users don't experience timeouts during long-running operations.

**US-T3: Template Caching**
- **As a** system, **I want** to cache common LLM responses in templates, **so that** API costs are reduced and response times are improved for similar requests.

## 6. Core Architecture & Patterns

### High-Level Architecture

The platform follows a microservices-oriented architecture with clear separation between frontend, backend API, and background workers.

**Development**: Docker Compose without nginx—frontend at `http://localhost:3000`, backend at `http://localhost:8000`. Five services: frontend, backend, redis, celery-worker, celery-beat. Database and auth: Supabase only (DATABASE_URL and Supabase keys in `backend/.env`).

**Production**: Render only. Same logical services (frontend web, backend web, worker, beat, Redis). Supabase for database and auth; Render Redis for cache and Celery broker. Migrations run via backend release command (`alembic upgrade head`). CORS origins configurable via comma-separated env.

```
┌─────────────────┐
│  Nuxt.js Frontend│  (Render Web Service / local :3000)
│  (SSR/SSG)      │
└────────┬─────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI Backend│  (Render Web Service / local :8000)
│  (REST API)     │
└────────┬─────────┘
         │
    ┌────┴────┬──────────────┐
    ▼         ▼              ▼
┌────────┐ ┌────────┐  ┌──────────┐
│Supabase│ │ Redis  │  │ Celery   │
│(Postgres│ │(Cache/ │  │ Workers  │
│ + Auth) │ │ Queue) │  │(Render)  │
└────────┘ └────────┘  └──────────┘
```

### Directory Structure

**Frontend (Nuxt.js)**:
```
frontend/
├── components/          # Reusable Vue components
├── pages/              # Route-based pages
├── layouts/            # Layout components
├── composables/        # Vue composables (API clients, auth)
├── stores/             # Pinia stores (state management)
├── utils/              # Utility functions
├── assets/             # Static assets
└── nuxt.config.ts      # Nuxt configuration
```

**Backend (FastAPI)**:
```
backend/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── api/                       # API route handlers
│   │   ├── v1/
│   │   │   ├── auth.py           # Authentication endpoints
│   │   │   ├── videos.py          # Video management endpoints
│   │   │   ├── patterns.py        # Pattern analysis endpoints
│   │   │   ├── strategies.py      # Strategy generation endpoints
│   │   │   ├── scripts.py         # Script generation endpoints
│   │   │   ├── posts.py           # Publishing endpoints
│   │   │   └── analytics.py       # Analytics endpoints
│   ├── services/                  # Business logic services
│   │   ├── pattern_service.py     # Pattern analysis (Gemini)
│   │   ├── strategy_service.py    # Strategy generation (GPT-4)
│   │   ├── script_service.py      # Script generation
│   │   ├── video_editor.py        # FFmpeg video editing
│   │   ├── oauth_service.py       # OAuth token management
│   │   ├── social_apis.py         # Social media API clients
│   │   └── analytics_service.py   # Performance tracking
│   ├── models/                    # SQLAlchemy models
│   ├── schemas/                   # Pydantic schemas
│   ├── workers/                   # Celery tasks
│   │   ├── celery_app.py          # Celery configuration
│   │   ├── video_tasks.py         # Video processing tasks
│   │   └── publish_tasks.py       # Publishing tasks
│   ├── db/                        # Database utilities
│   │   ├── session.py             # DB session management
│   │   └── migrations/            # Alembic migrations
│   └── utils/                     # Utility functions
│       ├── encryption.py          # Token encryption
│       └── templates.py           # LLM response caching
├── requirements.txt               # Python dependencies
└── alembic.ini                    # Alembic configuration
```

### Key Design Patterns

**1. Service Layer Pattern**
- Business logic isolated in service classes
- API routes delegate to services
- Services handle external API calls and data transformations
- Enables testability and reusability

**2. Repository Pattern** (via SQLAlchemy)
- Database access abstracted through models
- Centralized query logic
- Easy to mock for testing

**3. Task Queue Pattern** (Celery)
- Long-running operations (video processing, publishing) handled asynchronously
- Prevents API timeouts
- Enables retry logic and error handling
- Scales independently from API servers

**4. Template Pattern** (LLM Response Caching)
- Common LLM prompts cached as templates
- Reduces API costs for similar requests
- Improves response times
- Template matching based on content similarity

**5. Strategy Pattern** (Social Media APIs)
- Platform-specific implementations behind common interface
- Easy to add new platforms
- Consistent error handling across platforms

**6. Observer Pattern** (Analytics Updates)
- Pattern scores update automatically when new performance data arrives
- Decoupled analytics service listens for events
- Enables real-time learning loop

### Technology-Specific Patterns

**FastAPI**:
- Dependency injection for database sessions and auth
- Pydantic models for request/response validation
- Async/await for I/O operations
- OpenAPI/Swagger documentation auto-generation

**Nuxt.js**:
- Server-side rendering (SSR) for SEO and initial load performance
- Composables for reusable logic (API calls, auth state)
- Pinia for client-side state management
- Auto-imports for components and utilities

**Supabase**:
- Row Level Security (RLS) for data access control
- Real-time subscriptions for live updates (future enhancement)
- Storage buckets for video file management
- Auth hooks for user management

## 7. Tools/Features

### Feature Specifications

#### 7.1 Video Upload & Management

**Purpose**: Enable users to upload videos and manage their content library.

**Operations**:
- Upload video files (MP4, MOV, AVI) up to 500MB
- Store videos in Supabase Storage buckets
- Generate video metadata (duration, resolution, file size)
- Create video thumbnails automatically
- Support video organization (folders, tags, search)

**Key Features**:
- Drag-and-drop upload interface
- Upload progress indicators
- Video preview before processing
- Bulk upload support
- Video deletion and archival

**Technical Details**:
- File validation (format, size limits)
- Chunked uploads for large files
- Background thumbnail generation
- Storage quota management per user/organization

#### 7.2 Pattern Analysis Service

**Purpose**: Analyze uploaded videos to extract successful patterns using AI.

**Operations**:
- Extract visual patterns (cuts, transitions, pacing)
- Identify audio patterns (music timing, voice pacing)
- Analyze text/overlay patterns
- Detect hook patterns (first 3-5 seconds)
- Calculate pattern scores based on performance data

**Key Features**:
- Pattern extraction using Gemini 1.5 Pro vision capabilities
- Pattern visualization in dashboard
- Pattern comparison across multiple videos
- Pattern scoring algorithm (0-100 scale)
- Pattern recommendations for new content

**Technical Details**:
- Video frame extraction (key frames every 2 seconds)
- Frame analysis via Gemini 1.5 Pro
- Pattern storage in PostgreSQL (JSON format)
- Pattern matching algorithm for similarity detection
- Background processing via Celery

**AI Integration**:
- **Model**: Google Gemini 1.5 Pro
- **Input**: Video frames, metadata, performance data
- **Output**: Structured pattern data (JSON)
- **Caching**: Template system for similar videos

#### 7.3 Strategy Generation Service

**Purpose**: Generate marketing strategies based on analyzed patterns and platform requirements.

**Operations**:
- Generate platform-specific strategies
- Create content calendars
- Recommend posting schedules
- Suggest hashtag strategies
- Provide content theme recommendations

**Key Features**:
- Multi-platform strategy generation
- Strategy templates based on industry/niche
- Customizable strategy parameters
- Strategy export (PDF, Markdown)
- Strategy versioning and history

**Technical Details**:
- GPT-4 integration for strategy generation
- Prompt engineering for consistent output
- Template caching for common strategies
- Strategy storage in PostgreSQL
- Strategy application to video creation workflow

**AI Integration**:
- **Model**: OpenAI GPT-4
- **Input**: Pattern data, platform requirements, user goals
- **Output**: Structured strategy document (Markdown/JSON)
- **Caching**: Template matching for similar requests

#### 7.4 Script Generation Service

**Purpose**: Generate detailed filming and editing scripts based on successful patterns.

**Operations**:
- Generate filming scripts with timing
- Create editing instructions
- Specify visual requirements
- Provide text overlay specifications
- Generate platform-specific script variations

**Key Features**:
- Detailed timing breakdowns (second-by-second)
- Visual shot descriptions
- Audio/music recommendations
- Text overlay specifications
- Multiple script variations per video concept

**Technical Details**:
- GPT-4 integration for script generation
- Pattern-based script templates
- Script storage and versioning
- Script export formats (PDF, DOCX, Markdown)
- Integration with video editor for automated application

**AI Integration**:
- **Model**: OpenAI GPT-4
- **Input**: Video concept, target patterns, platform requirements
- **Output**: Structured script (JSON with timing, visuals, audio, text)
- **Caching**: Template system for similar concepts

#### 7.5 Video Editing Service

**Purpose**: Automatically apply patterns to raw video footage using FFmpeg.

**Operations**:
- Apply pattern-based cuts and transitions
- Add text overlays at specified timings
- Adjust video pacing (speed up/slow down)
- Create platform-specific variations (duration, aspect ratio)
- Generate multiple video outputs from single source

**Key Features**:
- Automated editing based on scripts/patterns
- Platform-specific output formats
- Batch processing for multiple variations
- Preview before final export
- Customizable editing parameters

**Technical Details**:
- FFmpeg-based video processing
- Pattern-to-FFmpeg command translation
- Background processing via Celery
- Video encoding optimization (H.264, various bitrates)
- Output storage in Supabase Storage

**Processing Pipeline**:
1. Parse script/pattern instructions
2. Extract source video segments
3. Apply cuts, transitions, effects
4. Add text overlays and graphics
5. Adjust audio (music, voice)
6. Encode to target format
7. Upload to storage
8. Notify user of completion

#### 7.6 OAuth Integration Service

**Purpose**: Securely connect and manage social media account credentials.

**Operations**:
- Initiate OAuth flows for each platform
- Store encrypted OAuth tokens
- Refresh expired tokens automatically
- Manage multiple accounts per platform
- Handle OAuth errors and re-authentication

**Key Features**:
- One-click OAuth connection per platform
- Token encryption at rest
- Automatic token refresh
- Account disconnection
- Multi-account support (future: team workspaces)

**Technical Details**:
- Platform-specific OAuth implementations:
  - Instagram: Instagram Graph API OAuth
  - TikTok: TikTok Marketing API OAuth
  - YouTube: Google OAuth 2.0
  - Facebook: Facebook Login OAuth
- AES-256 encryption for stored tokens
- Token refresh scheduling via Celery
- OAuth state validation for security

**Security**:
- Tokens encrypted with `ENCRYPTION_KEY` (32 bytes)
- Tokens never exposed in API responses
- Refresh tokens stored separately
- Automatic token rotation on refresh

#### 7.7 Social Media Publishing Service

**Purpose**: Publish content to connected social media platforms via their APIs.

**Operations**:
- Publish videos to Instagram (Reels)
- Publish videos to TikTok
- Publish videos to YouTube (Shorts, regular videos)
- Publish videos to Facebook (Reels, regular posts)
- Schedule future publications

**Key Features**:
- Platform-specific optimization (captions, hashtags, thumbnails)
- Bulk publishing to multiple platforms
- Scheduled publishing
- Publishing status tracking
- Retry logic for failed publications

**Technical Details**:
- Platform-specific API clients:
  - Instagram Graph API (Reels endpoint)
  - TikTok Marketing API (Video upload)
  - YouTube Data API v3 (Video upload)
  - Facebook Graph API (Video upload)
- Background publishing via Celery
- Publishing queue management
- Error handling and retry logic
- Publishing history and logs

**API Endpoints Used**:
- Instagram: `/{user-id}/media`, `/{user-id}/media_publish`
- TikTok: `/video/upload/`, `/video/publish/`
- YouTube: `videos.insert()`, `thumbnails.set()`
- Facebook: `/{page-id}/videos`, `/{page-id}/feed`

#### 7.8 Scheduling Service

**Purpose**: Schedule content for future publication across platforms.

**Operations**:
- Create scheduled posts
- Manage publishing calendar
- Bulk schedule multiple posts
- Edit/cancel scheduled posts
- View upcoming scheduled content

**Key Features**:
- Calendar view of scheduled posts
- Timezone support
- Platform-specific optimal timing recommendations
- Bulk scheduling operations
- Schedule notifications and reminders

**Technical Details**:
- Celery Beat for scheduled task execution
- PostgreSQL for schedule storage
- Timezone-aware scheduling
- Conflict detection (multiple posts at same time)
- Schedule modification and cancellation

**Task Execution**:
- Celery Beat checks for due posts every minute
- Triggers publishing tasks for due posts
- Updates post status (scheduled → publishing → published)
- Handles timezone conversions

#### 7.9 Analytics Service

**Purpose**: Track content performance and update pattern scores based on real data.

**Operations**:
- Fetch performance metrics from platforms
- Calculate engagement rates and scores
- Update pattern scores based on performance
- Generate performance reports
- Identify top-performing content

**Key Features**:
- Real-time performance tracking
- Engagement rate calculations
- Pattern score updates
- Performance comparisons
- Trend analysis over time

**Technical Details**:
- Scheduled metric fetching (hourly/daily)
- Platform API integration for metrics:
  - Instagram: Insights API
  - TikTok: Analytics API
  - YouTube: Analytics API
  - Facebook: Insights API
- Pattern score recalculation algorithm
- Performance data aggregation
- Historical data retention

**Learning Loop**:
1. Content published → Performance data collected
2. Performance metrics analyzed → Pattern effectiveness calculated
3. Pattern scores updated → Future recommendations improved
4. New content uses updated patterns → Cycle repeats

#### 7.10 Chat / LLM with Tools (Strategies)

**Purpose**: Provide a conversational interface for strategy, schedule, and script actions via an LLM with tool/function calling.

**Operations**:
- Accept chat messages and optional session ID; call LLM (OpenAI or configurable provider) with tool definitions matching platform capabilities
- Execute tools: list/create/reschedule/cancel schedule, list/create/update/export scripts, list/create/update/export strategies, list videos/patterns, list/upload/delete Branding, list connected platforms / get OAuth connect URL
- Return assistant message and structured card payloads (schedule changes, generated scripts, strategy docs) for the frontend to render in a result-cards panel

**Key Features**:
- Two-column Strategies UI: chat (left), result cards (right) that update when tools run
- Tool results drive cards (e.g. "Post moved to Friday 6 PM", "Script created", "Strategy refined")
- Streaming or single JSON response with `message` and `cards[]` or tool_results
- All tool executions scoped to current user (Supabase/JWT)

**Technical Details**:
- Endpoint: `POST /chat` or `POST /strategies/chat` with `messages[]`, optional `session_id`
- Tool definitions mirror MCP-style contract: schedule, scripts, strategies, videos, Branding, connected_platforms
- Backend implements tools as internal service calls (or via MCP client); no separate MCP process required for in-app chat

#### 7.11 Branding (User Assets)

**Purpose**: Let users upload and manage brand assets (logos, images) for use in content.

**Operations**:
- List Branding by user; filter by type (logo, image, watermark)
- Upload file with type; store in Supabase Storage (e.g. `Branding/{user_id}/`)
- Get material by ID; delete material

**Key Features**:
- Branding page under Account (or dedicated route); list grid, upload area, delete
- RLS for user_id; storage path and metadata (JSONB) per asset

**Technical Details**:
- Table: `user_assets` or `Branding` (id, user_id, type, filename, storage_path, url/metadata, created_at, updated_at)
- Endpoints: `GET /Branding`, `POST /Branding/upload`, `GET /Branding/{id}`, `DELETE /Branding/{id}`

#### 7.12 Schedule Page & Dashboard Schedule Card

**Purpose**: Full view of scheduled posts and a compact dashboard card for upcoming schedule.

**Operations**:
- Schedule page: list or calendar view of scheduled posts; filter by platform; edit time, cancel
- Dashboard: expandable "Posting Schedule" card with next N posts; "Open full schedule" → `/schedule`

**Key Features**:
- Data from `GET /posts/scheduled`; display date/time in user timezone (from preferences)
- Per-platform tabs or filters on Schedule page; add new scheduled post links to Publish flow

#### 7.13 Account Area (Profile, Preferences, Connected Platforms)

**Purpose**: Central place for user profile, app preferences, Branding, and connected social accounts.

**Operations**:
- App header dropdown: Profile, Preferences, Branding, Connected Platforms, Sign out
- Profile: display/edit name, email, avatar (Supabase user)
- Preferences: language, timezone for scheduling, notifications
- Connected Platforms: list Instagram, TikTok, YouTube, Facebook with connect/disconnect; moved from dashboard/publish; Publish page shows summary + "Manage in Account"

**Key Features**:
- All account pages use app layout and auth middleware
- Timezone stored and used for schedule display and creation

#### 7.14 Toasts, Empty/Loading States, UX Polish

**Purpose**: Non-blocking feedback and consistent list/modal UX.

**Operations**:
- Toasts: success/error (and optional info) via `useToast()` and toast container; auto-dismiss; used for chat tool results, publish, schedule, preferences save, connect/disconnect
- Empty states: every list (Videos, Scripts, Schedule, Branding, etc.) uses EmptyState with icon, title, description, primary action
- Loading: skeleton or spinner for lists; loading state on modals during submit
- Breadcrumbs or "Back to Dashboard" / "Back to Schedule" on account and schedule pages
- Escape key closes topmost modal or dropdown

#### 7.15 Template System

**Purpose**: Cache common LLM responses to reduce API costs and improve response times.

**Operations**:
- Store LLM response templates
- Match new requests to existing templates
- Retrieve cached responses when applicable
- Update templates based on usage patterns
- Manage template lifecycle

**Key Features**:
- Automatic template creation
- Similarity matching for requests
- Template versioning
- Template effectiveness tracking
- Manual template management

**Technical Details**:
- Template storage in PostgreSQL
- Similarity matching using embeddings (future) or keyword matching
- Template hit rate tracking
- Template expiration and cleanup
- Template customization per user/organization

**Matching Algorithm**:
- Compare request parameters (pattern type, platform, niche)
- Calculate similarity score
- Return cached response if similarity > threshold (e.g., 85%)
- Otherwise, call LLM and cache new response

## 8. Technology Stack

### Frontend

**Framework**: Nuxt.js 3.x
- **Rationale**: SSR/SSG support, excellent DX, Vue 3 composition API, auto-imports
- **Key Features**: Server-side rendering, file-based routing, composables

**Core Dependencies**:
- `vue` ^3.3.x - Core Vue framework
- `@nuxtjs/supabase` ^2.x - Supabase integration
- `pinia` ^2.x - State management
- `@vueuse/core` ^10.x - Vue composition utilities
- `axios` ^1.x - HTTP client
- `date-fns` ^2.x - Date manipulation

**UI Libraries** (to be selected):
- Option A: `@headlessui/vue` + `tailwindcss` - Headless components + utility CSS
- Option B: `vuetify` ^3.x - Material Design components
- Option C: `naive-ui` - TypeScript-first component library

**Build Tools**:
- `vite` ^5.x - Build tool (included with Nuxt)
- `typescript` ^5.x - Type safety
- `@nuxtjs/tailwindcss` (if using Tailwind) - Tailwind integration

### Backend

**Framework**: FastAPI 0.104.x+
- **Rationale**: High performance, automatic OpenAPI docs, async support, Python ecosystem
- **Key Features**: Type validation, dependency injection, async/await

**Core Dependencies**:
- `fastapi` ^0.104.x - Web framework
- `uvicorn[standard]` ^0.24.x - ASGI server
- `gunicorn` ^21.x - Production WSGI server
- `sqlalchemy` ^2.x - ORM
- `alembic` ^1.x - Database migrations
- `pydantic` ^2.x - Data validation
- `python-jose[cryptography]` ^3.x - JWT handling
- `python-multipart` ^0.0.6 - File uploads
- `httpx` ^0.25.x - Async HTTP client
- `celery` ^5.3.x - Task queue
- `redis` ^5.x - Redis client
- `cryptography` ^41.x - Token encryption

**AI/ML Libraries**:
- `google-generativeai` ^0.3.x - Gemini API client
- `openai` ^1.x - OpenAI API client
- `ffmpeg-python` ^0.2.x - FFmpeg wrapper

**Database**:
- `psycopg2-binary` ^2.9.x - PostgreSQL adapter
- `asyncpg` ^0.29.x - Async PostgreSQL driver (optional)

**Utilities**:
- `python-dotenv` ^1.x - Environment variable management
- `pytest` ^7.x - Testing framework
- `pytest-asyncio` ^0.21.x - Async test support

### Database & Storage

**Primary Database**: PostgreSQL 15 (via Supabase)
- **Rationale**: Reliable, feature-rich, excellent JSON support, managed service
- **Key Features**: JSON columns for flexible schema, full-text search, row-level security

**Cache**: Redis 7.x (via Render)
- **Rationale**: Fast in-memory cache, Celery broker, session storage
- **Key Features**: Pub/sub, persistence, clustering support

**File Storage**: Supabase Storage
- **Rationale**: Integrated with Supabase, CDN support, S3-compatible API
- **Key Features**: Public/private buckets, file versioning, automatic CDN

### Authentication & Authorization

**Provider**: Supabase Auth
- **Rationale**: Managed auth service, JWT-based, social OAuth support
- **Key Features**: Email/password, social logins, row-level security integration

**Implementation**:
- JWT tokens for API authentication
- Row Level Security (RLS) policies in PostgreSQL
- Token refresh mechanism
- Session management via Redis

### Background Processing

**Task Queue**: Celery 5.3.x
- **Rationale**: Mature, Python-native, Redis backend, scheduling support
- **Key Features**: Async task execution, scheduled tasks (Celery Beat), retry logic

**Broker**: Redis
- **Rationale**: Fast, reliable, supports both Celery broker and result backend
- **Configuration**: Single Redis instance for broker and cache

### AI Services

**Pattern Analysis**: Google Gemini 1.5 Pro
- **Rationale**: Excellent vision capabilities, large context window, cost-effective
- **Use Case**: Video frame analysis, pattern extraction

**Strategy/Script Generation**: OpenAI GPT-4
- **Rationale**: Best-in-class text generation, creative capabilities
- **Use Case**: Marketing strategy generation, script creation

**Future Considerations**:
- Grok API (X/Twitter) for platform-specific insights
- Claude (Anthropic) as alternative for text generation

### Deployment & Infrastructure

**Platform**: Render (production only; no Render-managed PostgreSQL—Supabase only)
- **Rationale**: Simple configuration, managed services, Git-based deployment
- **Services**: Web services (frontend, backend), background workers (Celery worker, Celery beat), Redis. No Render database; DATABASE_URL is Supabase connection string.

**Development**:
- Docker Compose: frontend, backend, redis, celery-worker, celery-beat (no nginx, no postgres container)
- Access: `http://localhost:3000` (frontend), `http://localhost:8000` (backend)
- Env: `backend/.env` (DATABASE_URL Supabase, REDIS_URL e.g. `redis://redis:6379`), `frontend/.env` (NUXT_PUBLIC_API_URL=`http://localhost:8000/api/v1`)
- See SETUP.md for full instructions; migrations: `docker-compose exec backend alembic upgrade head`

**Configuration**:
- `render.yaml` for infrastructure as code; backend has `releaseCommand: cd backend && alembic upgrade head`
- Environment variables via Render dashboard (DATABASE_URL, NUXT_PUBLIC_API_URL, REDIS_URL from Render Redis, SUPABASE_*, secrets)
- CORS: backend reads `CORS_ORIGINS` from env (comma-separated) so production frontend URL(s) can be set in Render
- Auto-deploy from Git; health checks and auto-restart

**Monitoring** (Basic):
- Render built-in logs
- Health check endpoints (`/health`)
- Future: Advanced monitoring (DataDog, Sentry)

### Development Tools

**Version Control**: Git (GitHub/GitLab/Bitbucket)
**Package Management**:
- Frontend: `npm` / `pnpm`
- Backend: `pip` / `poetry` (optional)

**Code Quality**:
- Frontend: ESLint, Prettier
- Backend: Black, Ruff, mypy

**Testing**:
- Frontend: Vitest, Vue Test Utils
- Backend: pytest, pytest-asyncio

## 9. Security & Configuration

### Authentication & Authorization

**Authentication Approach**:
- Supabase Auth handles user authentication (email/password, social OAuth)
- JWT tokens issued by Supabase for API authentication
- Tokens validated on each API request
- Token refresh via Supabase refresh tokens

**Authorization**:
- Row Level Security (RLS) policies in PostgreSQL
- User-scoped data access (users can only access their own data)
- Organization-level access control (future: team workspaces)
- API-level authorization checks in FastAPI dependencies

**OAuth Token Security**:
- Social media OAuth tokens encrypted at rest (AES-256)
- Encryption key stored in environment variable (`ENCRYPTION_KEY`)
- Tokens never exposed in API responses
- Automatic token refresh to prevent expiration
- Token rotation on refresh

### Configuration Management

**Environment Variables**:

**Frontend** (development vs production):
- **Development**: `NUXT_PUBLIC_API_URL=http://localhost:8000/api/v1`; Supabase URL/anon key in `.env`
- **Production (Render)**: Set in Render Dashboard: `NUXT_PUBLIC_API_URL` = backend URL + `/api/v1` (e.g. `https://social-media-ai-backend.onrender.com/api/v1`), plus Supabase URL/anon key

**Backend** (`.env`):
```env
# Database (Supabase only; no local Postgres)
DATABASE_URL=postgresql://postgres.[ref]:[password]@...pooler.supabase.com:6543/postgres

# Redis (dev: redis://localhost:6379 or redis://redis:6379 in Docker; prod: Render Redis URL)
REDIS_URL=redis://red-xxx:6379

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-key
SUPABASE_JWT_SECRET=your-jwt-secret

# AI APIs
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key

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
ENCRYPTION_KEY=your-32-byte-encryption-key  # Must be exactly 32 bytes
SECRET_KEY=your-secret-key-for-jwt

# Render
PORT=8000  # Auto-set by Render
```

**Configuration Best Practices**:
- All sensitive values stored as environment variables; never commit real secrets
- Never commit `.env` files to Git
- Use Render's secret management for production (DATABASE_URL, SUPABASE_*, REDIS_URL, API keys)
- Development uses `backend/.env` and `frontend/.env`; production env is set in Render Dashboard only
- CORS: set `CORS_ORIGINS` in production as comma-separated list (e.g. `https://social-media-ai-frontend.onrender.com`)
- Validate required environment variables on startup

### Security Scope

**In Scope (MVP)**:
- ✅ JWT-based authentication
- ✅ Encrypted OAuth token storage
- ✅ Row Level Security (RLS) in database
- ✅ API request validation (Pydantic)
- ✅ HTTPS/TLS (via Render)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ XSS prevention (Vue.js auto-escaping)
- ✅ CORS configuration
- ✅ Rate limiting (basic, via Render or middleware)
- ✅ Input sanitization and validation

**Out of Scope (Post-MVP)**:
- ❌ Advanced DDoS protection (WAF)
- ❌ Web Application Firewall (WAF)
- ❌ Advanced rate limiting per user/IP
- ❌ Security audit logging
- ❌ Penetration testing automation
- ❌ Multi-factor authentication (MFA)
- ❌ IP whitelisting/blacklisting
- ❌ Advanced threat detection

### Deployment Considerations

**Render Security Features**:
- Automatic SSL/TLS certificates
- DDoS protection (basic)
- Health check monitoring
- Auto-restart on failures
- Isolated service environments

**Database Security**:
- Managed PostgreSQL with automatic backups
- Connection encryption (SSL)
- Network isolation (private networking)
- Access restricted to Render services

**File Storage Security**:
- Supabase Storage with private buckets
- Signed URLs for temporary access
- Access control via RLS policies
- CDN with HTTPS

## 10. API Specification

### Authentication

All API endpoints (except `/health` and `/auth/*`) require authentication via JWT token in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

### Base URL

```
Production: https://social-media-ai-backend.onrender.com/api/v1
Development: http://localhost:8000/api/v1
```

### Endpoints

#### Health Check

**GET** `/health`

Check API health status.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Authentication

**POST** `/auth/login`

Authenticate user and receive JWT token.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**POST** `/auth/refresh`

Refresh JWT token.

**Request Headers**:
```
Authorization: Bearer <refresh_token>
```

**Response**: Same as `/auth/login`

#### Videos

**GET** `/videos`

List user's videos.

**Query Parameters**:
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `status` (string): Filter by status (`uploaded`, `processing`, `processed`, `failed`)

**Response**:
```json
{
  "items": [
    {
      "id": "uuid",
      "filename": "video.mp4",
      "duration": 120,
      "status": "processed",
      "created_at": "2024-01-15T10:00:00Z",
      "thumbnail_url": "https://..."
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 20
}
```

**POST** `/videos/upload`

Upload a new video.

**Request**: `multipart/form-data`
- `file` (file): Video file (MP4, MOV, AVI)
- `title` (string, optional): Video title

**Response**:
```json
{
  "id": "uuid",
  "filename": "video.mp4",
  "status": "uploaded",
  "upload_url": "https://...",
  "created_at": "2024-01-15T10:00:00Z"
}
```

**GET** `/videos/{video_id}`

Get video details.

**Response**:
```json
{
  "id": "uuid",
  "filename": "video.mp4",
  "duration": 120,
  "status": "processed",
  "patterns": [...],
  "created_at": "2024-01-15T10:00:00Z"
}
```

**POST** `/videos/{video_id}/analyze`

Trigger pattern analysis for a video.

**Response**:
```json
{
  "task_id": "uuid",
  "status": "queued",
  "estimated_completion": "2024-01-15T10:05:00Z"
}
```

#### Patterns

**GET** `/patterns`

List analyzed patterns.

**Query Parameters**:
- `video_id` (uuid, optional): Filter by video
- `min_score` (float, optional): Minimum pattern score

**Response**:
```json
{
  "items": [
    {
      "id": "uuid",
      "video_id": "uuid",
      "type": "hook_timing",
      "score": 85.5,
      "data": {...},
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### Strategies

**POST** `/strategies/generate`

Generate a marketing strategy.

**Request Body**:
```json
{
  "video_ids": ["uuid1", "uuid2"],
  "platforms": ["tiktok", "instagram"],
  "goals": ["engagement", "views"]
}
```

**Response**:
```json
{
  "id": "uuid",
  "strategy": {
    "recommendations": [...],
    "posting_schedule": {...},
    "hashtag_strategy": {...}
  },
  "created_at": "2024-01-15T10:00:00Z"
}
```

**GET** `/strategies/{strategy_id}`

Get strategy details.

#### Chat (Strategies / LLM with tools)

**POST** `/chat` or `/strategies/chat`

Send messages and receive LLM response with optional tool results (schedule changes, scripts, strategy docs). Tool results can be returned as structured card payloads for the frontend.

**Request Body**:
```json
{
  "messages": [
    { "role": "user", "content": "Schedule my latest video for Friday 6 PM on Instagram" }
  ],
  "session_id": "optional-uuid"
}
```

**Response**: Streaming (SSE) or JSON with `message` and `cards[]` (or `tool_results`) for result cards (schedule updates, script created, strategy refined, etc.). All tool executions are scoped to the authenticated user.

#### Scripts

**POST** `/scripts/generate`

Generate a filming/editing script.

**Request Body**:
```json
{
  "concept": "5 Tips for Better Sleep",
  "target_patterns": ["uuid1", "uuid2"],
  "platform": "tiktok",
  "duration": 60
}
```

**Response**:
```json
{
  "id": "uuid",
  "script": {
    "segments": [
      {
        "start_time": 0,
        "end_time": 3,
        "visual": "Close-up of alarm clock",
        "audio": "Upbeat music starts",
        "text_overlay": "Are you tired of waking up exhausted?"
      }
    ]
  },
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### Video Editing

**POST** `/videos/{video_id}/edit`

Apply patterns/script to create edited video.

**Request Body**:
```json
{
  "script_id": "uuid",
  "platform": "tiktok",
  "output_format": {
    "duration": 60,
    "aspect_ratio": "9:16",
    "resolution": "1080x1920"
  }
}
```

**Response**:
```json
{
  "task_id": "uuid",
  "status": "queued",
  "estimated_completion": "2024-01-15T10:10:00Z"
}
```

#### OAuth & Social Media

**GET** `/oauth/{platform}/connect`

Initiate OAuth flow for platform.

**Query Parameters**:
- `platform`: `instagram`, `tiktok`, `youtube`, `facebook`

**Response**:
```json
{
  "auth_url": "https://platform.com/oauth/authorize?...",
  "state": "random-state-token"
}
```

**GET** `/oauth/{platform}/callback`

Handle OAuth callback (called by platform).

**POST** `/social/accounts`

List connected social media accounts.

**Response**:
```json
{
  "accounts": [
    {
      "id": "uuid",
      "platform": "instagram",
      "username": "@username",
      "connected_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### Publishing

**POST** `/posts/publish`

Publish video to social media platforms.

**Request Body**:
```json
{
  "video_id": "uuid",
  "platforms": ["instagram", "tiktok"],
  "caption": "Check out this amazing video!",
  "hashtags": ["#viral", "#fyp"],
  "publish_now": true
}
```

**Response**:
```json
{
  "task_id": "uuid",
  "status": "queued",
  "posts": [
    {
      "platform": "instagram",
      "status": "queued",
      "post_id": null
    }
  ]
}
```

**POST** `/posts/schedule`

Schedule a post for future publication.

**Request Body**:
```json
{
  "video_id": "uuid",
  "platforms": ["instagram"],
  "scheduled_at": "2024-01-20T18:00:00Z",
  "caption": "...",
  "hashtags": [...]
}
```

**Response**:
```json
{
  "id": "uuid",
  "scheduled_at": "2024-01-20T18:00:00Z",
  "status": "scheduled"
}
```

#### Analytics

**GET** `/analytics/videos/{video_id}`

Get performance analytics for a video.

**Response**:
```json
{
  "video_id": "uuid",
  "platforms": {
    "tiktok": {
      "views": 50000,
      "likes": 5000,
      "comments": 200,
      "shares": 300,
      "engagement_rate": 11.0
    }
  },
  "pattern_match_score": 92.5,
  "updated_at": "2024-01-15T12:00:00Z"
}
```

**GET** `/analytics/dashboard`

Get aggregated analytics dashboard data.

**Query Parameters**:
- `start_date` (date): Start date for analytics
- `end_date` (date): End date for analytics
- `platform` (string, optional): Filter by platform

**Response**:
```json
{
  "total_views": 500000,
  "total_engagement": 55000,
  "average_engagement_rate": 11.0,
  "top_performing_videos": [...],
  "platform_breakdown": {...}
}
```

### Error Responses

All endpoints return standard error responses:

**400 Bad Request**:
```json
{
  "error": "validation_error",
  "message": "Invalid request data",
  "details": {...}
}
```

**401 Unauthorized**:
```json
{
  "error": "authentication_error",
  "message": "Invalid or expired token"
}
```

**404 Not Found**:
```json
{
  "error": "not_found",
  "message": "Resource not found"
}
```

**500 Internal Server Error**:
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred"
}
```

## 11. Success Criteria

### MVP Success Definition

The MVP is considered successful when users can complete the core workflow end-to-end: upload a video, receive AI-generated insights and strategies, create optimized video variations, publish to social media platforms, and track performance—all within a stable, performant platform.

### Functional Requirements

#### Core Workflow
- ✅ Users can create accounts and authenticate securely
- ✅ Users can upload videos (up to 500MB) and see upload progress
- ✅ System analyzes uploaded videos and extracts patterns within 5 minutes
- ✅ Users receive AI-generated marketing strategies based on their video patterns
- ✅ Users can generate detailed filming/editing scripts
- ✅ System creates edited video variations based on scripts/patterns
- ✅ Users can connect social media accounts via OAuth
- ✅ Users can publish videos to connected platforms
- ✅ Users can schedule posts for future publication
- ✅ System tracks performance metrics and updates pattern scores
- ✅ Users can view analytics dashboards with performance data

#### Performance Requirements
- ✅ Video upload completes for files up to 500MB
- ✅ Pattern analysis completes within 5 minutes for videos up to 5 minutes
- ✅ Video editing completes within 10 minutes for 60-second outputs
- ✅ API response times < 500ms for non-processing endpoints
- ✅ Frontend page load times < 2 seconds (initial load)
- ✅ Dashboard renders analytics data within 1 second

#### Reliability Requirements
- ✅ System uptime > 99% (excluding planned maintenance)
- ✅ Background tasks (video processing, publishing) complete successfully > 95% of the time
- ✅ Failed tasks automatically retry up to 3 times
- ✅ Data persistence: No data loss for uploaded videos, patterns, or analytics
- ✅ OAuth token refresh succeeds automatically > 99% of the time

#### User Experience Requirements
- ✅ Intuitive UI: Users can complete core workflow without training
- ✅ Clear error messages: Users understand what went wrong and how to fix it
- ✅ Progress indicators: Users see status for long-running operations
- ✅ Responsive design: Platform works on desktop and tablet (mobile: post-MVP)
- ✅ Accessible: Basic accessibility standards met (WCAG 2.1 Level A)

### Quality Indicators

**Technical Quality**:
- Code coverage > 70% for critical paths (authentication, video processing, publishing)
- Zero critical security vulnerabilities
- API documentation complete and accurate (OpenAPI/Swagger)
- Database migrations tested and reversible

**User Satisfaction**:
- User can complete full workflow (upload → analyze → publish) without support
- Positive user feedback on UI/UX (qualitative assessment)
- Low error rates (< 5% of operations fail)

**Business Metrics** (Post-MVP):
- User retention: > 60% of users return within 7 days
- Content published: Average user publishes > 5 videos per month
- Platform adoption: > 2 platforms connected per user on average

## 12. Implementation Phases

### Phase 1: Foundation & Infrastructure (Weeks 1-3)

**Goal**: Set up development environment, core infrastructure, and basic authentication.

**Deliverables**:
- ✅ Project structure (frontend and backend)
- ✅ Render deployment configuration (`render.yaml`)
- ✅ Supabase project setup (database, auth, storage)
- ✅ PostgreSQL database schema (initial migrations)
- ✅ Redis cache setup
- ✅ User authentication (Supabase Auth integration)
- ✅ Basic API structure (FastAPI routes, Nuxt.js pages)
- ✅ Health check endpoints
- ✅ Development environment documentation

**Validation Criteria**:
- Users can register and log in
- API authentication works end-to-end
- Database migrations run successfully
- Services deploy to Render successfully
- Health checks pass

**Timeline**: 3 weeks

### Phase 2: Core Video Features (Weeks 4-7)

**Goal**: Implement video upload, storage, and pattern analysis.

**Deliverables**:
- ✅ Video upload functionality (frontend + backend)
- ✅ Supabase Storage integration
- ✅ Video metadata extraction
- ✅ Thumbnail generation
- ✅ Pattern Analysis Service (Gemini 1.5 Pro integration)
- ✅ Pattern storage and retrieval
- ✅ Pattern visualization in dashboard
- ✅ Background video processing (Celery tasks)
- ✅ Video management UI (list, view, delete)

**Validation Criteria**:
- Users can upload videos successfully
- Pattern analysis completes and stores results
- Patterns visible in dashboard
- Background processing handles multiple videos concurrently
- Video files stored securely in Supabase Storage

**Timeline**: 4 weeks

### Phase 3: AI Services & Video Editing (Weeks 8-11)

**Goal**: Implement strategy generation, script generation, and video editing.

**Deliverables**:
- ✅ Strategy Generation Service (GPT-4 integration)
- ✅ Script Generation Service
- ✅ Template system for LLM response caching
- ✅ Video Editing Service (FFmpeg integration)
- ✅ Pattern-to-video application logic
- ✅ Platform-specific video output formats
- ✅ Strategy and script UI components
- ✅ Video editing workflow UI

**Validation Criteria**:
- Users receive AI-generated strategies based on patterns
- Scripts generated with detailed timing and instructions
- Video editing creates platform-specific variations
- Template system reduces API costs for similar requests
- Edited videos match script specifications

**Timeline**: 4 weeks

### Phase 4: Publishing & Analytics (Weeks 12-15)

**Goal**: Implement social media publishing, scheduling, and analytics.

**Deliverables**:
- ✅ OAuth integration for all platforms (Instagram, TikTok, YouTube, Facebook)
- ✅ OAuth token encryption and refresh
- ✅ Social Media Publishing Service
- ✅ Scheduling Service (Celery Beat)
- ✅ Analytics Service (performance tracking)
- ✅ Pattern score update logic (learning loop)
- ✅ Publishing UI (connect accounts, publish, schedule)
- ✅ Analytics dashboard UI
- ✅ End-to-end testing

**Validation Criteria**:
- Users can connect all four social media platforms
- Videos publish successfully to connected platforms
- Scheduled posts publish at correct times
- Performance metrics collected and displayed
- Pattern scores update based on performance data
- Full workflow (upload → analyze → edit → publish → track) works end-to-end

**Timeline**: 4 weeks

### Phase 5: Polish & Launch (Weeks 16-17)

**Goal**: Final testing, bug fixes, documentation, and production launch.

**Deliverables**:
- ✅ Comprehensive testing (unit, integration, E2E)
- ✅ Bug fixes and performance optimization
- ✅ Error handling improvements
- ✅ User documentation
- ✅ API documentation (OpenAPI/Swagger)
- ✅ Production deployment configuration
- ✅ Monitoring setup (basic)
- ✅ Launch preparation

**Validation Criteria**:
- All critical bugs fixed
- Performance meets requirements
- Documentation complete
- Production environment stable
- Ready for beta user testing

**Timeline**: 2 weeks

### Phase 6: Infrastructure & App UX (Executed)

**Goal**: Supabase-only infra, dev/prod split, Render-ready; app layout, chatbot strategies, account/schedule/Branding, UX polish.

**Deliverables** (executed per plans):
- ✅ Infrastructure: Docker without nginx (dev :3000/:8000); docker-compose.prod without postgres; CORS from env; Render release command for migrations; SETUP/README/env examples aligned
- ✅ App layout (logo-only header) for authenticated routes; dashboard revamp (real stats, Schedule card)
- ✅ Strategies page as chatbot + result cards; chat backend with LLM + tools (schedule, scripts, strategies, videos, Branding, connected platforms)
- ✅ Account dropdown and pages: Profile, Preferences, Branding, Connected Platforms
- ✅ Schedule page; Strategy and Script detail/export; Toasts; timezone in preferences; empty/loading states; breadcrumbs/back links; Escape to close; Publish connection summary

**Total MVP Timeline**: ~17 weeks (~4 months) plus executed Phase 6

## 13. Future Considerations

### Post-MVP Enhancements

**User Experience**:
- Mobile applications (iOS/Android) for on-the-go content management
- Advanced video editing UI with timeline and preview
- Real-time collaboration on scripts and strategies
- Content calendar with drag-and-drop scheduling
- Bulk import/export functionality

**Features**:
- Multi-user collaboration and team workspaces
- A/B testing framework for content variations
- Advanced analytics with custom reports and insights
- White-label solutions for agencies
- Integration with additional platforms (Twitter/X, LinkedIn, Pinterest, Snapchat)
- Custom AI model training based on user's content

**Technical**:
- CDN integration for faster video delivery
- Advanced caching strategies (edge caching, CDN)
- Multi-region deployment for global users
- Advanced monitoring and alerting (DataDog, Sentry, PagerDuty)
- Automated backup and disaster recovery
- API access for third-party integrations
- Webhook support for external integrations

**AI/ML Enhancements**:
- Fine-tuned models based on user's successful content
- Predictive analytics (forecast performance before publishing)
- Automated hashtag generation and optimization
- Trend detection and recommendations
- Competitor analysis and benchmarking
- Sentiment analysis for comments and engagement

**Business Features**:
- Subscription tiers (free, pro, enterprise)
- Usage-based billing
- Affiliate/referral program
- Marketplace for templates and strategies
- Community features (share strategies, templates)

### Integration Opportunities

**Third-Party Tools**:
- Zapier/Make integrations for workflow automation
- Slack/Discord notifications for publishing events
- Google Analytics integration for website traffic correlation
- Email marketing platforms (Mailchimp, ConvertKit) for audience insights

**Content Sources**:
- YouTube channel import (analyze existing videos)
- Instagram profile import (analyze existing posts)
- TikTok profile import
- RSS feed integration for blog-to-video conversion

**Analytics Platforms**:
- Google Analytics
- Facebook Analytics
- Custom analytics dashboards (Tableau, Looker)

## 14. Risks & Mitigations

### Risk 1: AI API Costs Exceed Budget

**Description**: High usage of Gemini and GPT-4 APIs could result in unexpectedly high costs, especially during video analysis and strategy generation.

**Impact**: High - Could make the product unprofitable or require significant price increases.

**Mitigation**:
- Implement template caching system early to reduce redundant API calls
- Set up API usage monitoring and alerts
- Implement rate limiting per user to prevent abuse
- Consider using cheaper models (GPT-3.5-turbo) for less critical operations
- Implement request queuing to batch similar requests
- Set up cost budgets and automatic throttling in API provider dashboards

### Risk 2: Video Processing Performance Issues

**Description**: FFmpeg video processing may be slow or fail for large/complex videos, causing user frustration and system overload.

**Impact**: High - Core feature may become unusable, affecting user satisfaction.

**Mitigation**:
- Implement robust error handling and retry logic for video processing
- Use Render workers with adequate resources (consider Standard tier)
- Optimize FFmpeg commands for speed vs. quality balance
- Implement video preprocessing (compression, format conversion) before editing
- Add progress tracking so users know processing status
- Consider alternative video processing services (Cloudinary, Mux) if FFmpeg proves insufficient
- Implement queue prioritization for urgent processing

### Risk 3: Social Media API Changes or Limitations

**Description**: Social media platforms may change their APIs, impose rate limits, or restrict access, breaking publishing functionality.

**Impact**: High - Core feature becomes non-functional, users cannot publish content.

**Mitigation**:
- Abstract platform-specific code behind common interfaces (Strategy Pattern)
- Monitor platform API changelogs and developer communities
- Implement comprehensive error handling and user-friendly error messages
- Build fallback mechanisms (manual publishing instructions if API fails)
- Maintain relationships with platform developer support teams
- Implement rate limiting and retry logic respecting platform limits
- Consider official platform partnerships for better API access

### Risk 4: OAuth Token Security Breach

**Description**: If encryption keys are compromised or tokens are exposed, attackers could gain access to users' social media accounts.

**Impact**: Critical - Security breach, loss of user trust, potential legal issues.

**Mitigation**:
- Use strong encryption (AES-256) for token storage
- Store encryption keys securely (environment variables, never in code)
- Implement token rotation on refresh
- Regular security audits of authentication and encryption code
- Implement token expiration and automatic refresh
- Use platform-specific token scopes (minimum required permissions)
- Add user notifications for new account connections
- Implement anomaly detection for suspicious publishing activity

### Risk 5: Scalability Limitations on Render

**Description**: Render's infrastructure may not scale adequately for video processing workloads or high user concurrency, causing performance degradation.

**Impact**: Medium - May require migration to different platform, causing delays and additional costs.

**Mitigation**:
- Start with Render Starter tier, monitor performance closely
- Design architecture to be platform-agnostic (easy to migrate)
- Implement horizontal scaling from the start (stateless services)
- Use Render's scaling features (multiple instances, larger instance types)
- Monitor resource usage and plan upgrades proactively
- Have migration plan ready (AWS, Google Cloud, Azure) if Render proves insufficient
- Consider hybrid approach (Render for web services, specialized services for video processing)

### Risk 6: Data Privacy and Compliance Issues

**Description**: Handling user videos and social media data may require compliance with GDPR, CCPA, or platform-specific data policies.

**Impact**: High - Legal issues, fines, inability to operate in certain regions.

**Mitigation**:
- Implement data retention policies (delete videos after X days of inactivity)
- Provide user data export and deletion capabilities
- Implement privacy controls (users control what data is stored)
- Review and comply with platform data usage policies
- Add privacy policy and terms of service
- Consider GDPR compliance from the start (data minimization, user consent)
- Implement data encryption in transit and at rest
- Regular compliance audits

## 15. Appendix

### Related Documents

- Architecture Plan: `.cursor/plans/social_media_ai_saas_architecture_f3707f3c.plan.md`
- **Executed plans** (reference for current implementation):
  - **Infrastructure (Supabase-only, dev/prod, Render)**: `.cursor/plans/infra_supabase_dev_prod_render_7adb4aba.plan.md` — Docker without nginx, no Postgres containers, CORS from env, release command, SETUP/README/env examples
  - **Complete app features and UX**: `.cursor/plans/complete_app_features_and_ux_f64c9818.plan.md` — Strategies chatbot + result cards, MCP/tools, account/schedule/Branding, toasts, timezone, empty/loading states, breadcrumbs, Escape to close, Publish connection summary
  - **App dashboard frontend revamp**: `.cursor/plans/app_dashboard_frontend_revamp_45ac4bb7.plan.md` — App layout, dashboard stat cards and real data, Schedule card
  - **Frontend professional revamp**: `.cursor/plans/frontend_professional_revamp_ef892aae.plan.md` — UI components, landing sections, icons (lucide), Tailwind, rebrand (ElevoAI if applied)
  - **Docker infrastructure**: `.cursor/plans/docker_infrastructure_setup_06842005.plan.md` — Dockerfiles, compose, CI/CD (superseded in part by Supabase-only infra plan)
- Render Documentation: https://render.com/docs
- Supabase Documentation: https://supabase.com/docs
- FastAPI Documentation: https://fastapi.tiangolo.com
- Nuxt.js Documentation: https://nuxt.com/docs
- SETUP.md: Development (Docker, Supabase, no nginx) and Production (Render, env vars, migrations)

### Key Dependencies

**External Services**:
- Supabase (Database, Auth, Storage): https://supabase.com
- Render (Hosting): https://render.com
- Google Gemini API: https://ai.google.dev
- OpenAI API: https://platform.openai.com

**Social Media APIs**:
- Instagram Graph API: https://developers.facebook.com/docs/instagram-api
- TikTok Marketing API: https://developers.tiktok.com/doc/marketing-api-overview
- YouTube Data API: https://developers.google.com/youtube/v3
- Facebook Graph API: https://developers.facebook.com/docs/graph-api

### Repository Structure

```
socialmediaAI/
├── frontend/                 # Nuxt.js frontend
│   ├── components/
│   ├── pages/
│   ├── composables/
│   ├── stores/
│   └── nuxt.config.ts
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   ├── workers/
│   │   └── db/
│   ├── requirements.txt
│   └── alembic.ini
├── render.yaml               # Render deployment config
├── README.md
└── PRD.md                    # This document
```

### Glossary

- **Pattern**: A successful element or technique identified in video content (e.g., hook timing, cut frequency, text overlay style)
- **Pattern Score**: A numerical value (0-100) indicating how effective a pattern is based on performance data
- **Strategy**: AI-generated marketing plan based on analyzed patterns and platform requirements
- **Script**: Detailed filming and editing instructions with timing, visuals, audio, and text specifications
- **Learning Loop**: The process of updating pattern scores based on performance data to improve future recommendations
- **Template**: Cached LLM response used to reduce API costs for similar requests
- **RLS**: Row Level Security - PostgreSQL feature for user-scoped data access

---

**Document Version**: 1.1  
**Last Updated**: 2026-01-28  
**Status**: Living document — updated from executed plans (infra Supabase-only, app features and UX, dashboard revamp)

