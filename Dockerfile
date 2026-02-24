# syntax=docker/dockerfile:1.7

FROM node:20-bookworm-slim AS nuxt-builder

WORKDIR /build/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./

ARG NUXT_PUBLIC_API_URL=/api/v1
ARG NUXT_PUBLIC_SUPABASE_URL=
ARG NUXT_PUBLIC_SUPABASE_ANON_KEY=
ARG NUXT_PUBLIC_SUPABASE_STORAGE_BUCKET=videos
ARG NUXT_PUBLIC_EDITOR_PARITY_FLAG=false
ARG NUXT_PUBLIC_EDITOR_FORK_ENABLED=true
ARG NUXT_PUBLIC_EDITOR_FORK_ROLLOUT_PERCENT=100
ARG NUXT_PUBLIC_EDITOR_FORK_ALLOWLIST=

ENV NUXT_PUBLIC_API_URL=${NUXT_PUBLIC_API_URL} \
    NUXT_PUBLIC_SUPABASE_URL=${NUXT_PUBLIC_SUPABASE_URL} \
    NUXT_PUBLIC_SUPABASE_ANON_KEY=${NUXT_PUBLIC_SUPABASE_ANON_KEY} \
    NUXT_PUBLIC_SUPABASE_STORAGE_BUCKET=${NUXT_PUBLIC_SUPABASE_STORAGE_BUCKET} \
    NUXT_PUBLIC_EDITOR_PARITY_FLAG=${NUXT_PUBLIC_EDITOR_PARITY_FLAG} \
    NUXT_PUBLIC_EDITOR_FORK_ENABLED=${NUXT_PUBLIC_EDITOR_FORK_ENABLED} \
    NUXT_PUBLIC_EDITOR_FORK_ROLLOUT_PERCENT=${NUXT_PUBLIC_EDITOR_FORK_ROLLOUT_PERCENT} \
    NUXT_PUBLIC_EDITOR_FORK_ALLOWLIST=${NUXT_PUBLIC_EDITOR_FORK_ALLOWLIST}

RUN npm run build


FROM oven/bun:1.2.18 AS opencut-builder

WORKDIR /build/opencut

COPY apps/opencut-editor/package.json ./package.json
COPY apps/opencut-editor/bun.lock ./bun.lock
COPY apps/opencut-editor/turbo.json ./turbo.json
COPY apps/opencut-editor/apps/web/package.json ./apps/web/package.json
COPY apps/opencut-editor/packages/env/package.json ./packages/env/package.json
COPY apps/opencut-editor/packages/ui/package.json ./packages/ui/package.json

RUN bun install --frozen-lockfile

COPY apps/opencut-editor/apps/web ./apps/web
COPY apps/opencut-editor/packages/env ./packages/env
COPY apps/opencut-editor/packages/ui ./packages/ui

ARG NEXT_PUBLIC_SITE_URL=http://localhost:3000
ARG NEXT_PUBLIC_FASTAPI_URL=/api/v1
ARG NEXT_PUBLIC_SUPABASE_URL=
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY=
ARG NEXT_PUBLIC_SUPABASE_STORAGE_BUCKET=videos
ARG NEXT_PUBLIC_EDITOR_BASE_PATH=/editor
ARG NEXT_PUBLIC_EDITOR_RETURN_TO=/editor
ARG NEXT_PUBLIC_EDITOR_DIAGNOSTICS=false

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    NEXT_PUBLIC_SITE_URL=${NEXT_PUBLIC_SITE_URL} \
    NEXT_PUBLIC_FASTAPI_URL=${NEXT_PUBLIC_FASTAPI_URL} \
    NEXT_PUBLIC_SUPABASE_URL=${NEXT_PUBLIC_SUPABASE_URL} \
    NEXT_PUBLIC_SUPABASE_ANON_KEY=${NEXT_PUBLIC_SUPABASE_ANON_KEY} \
    NEXT_PUBLIC_SUPABASE_STORAGE_BUCKET=${NEXT_PUBLIC_SUPABASE_STORAGE_BUCKET} \
    NEXT_PUBLIC_EDITOR_BASE_PATH=${NEXT_PUBLIC_EDITOR_BASE_PATH} \
    NEXT_PUBLIC_EDITOR_RETURN_TO=${NEXT_PUBLIC_EDITOR_RETURN_TO} \
    NEXT_PUBLIC_EDITOR_DIAGNOSTICS=${NEXT_PUBLIC_EDITOR_DIAGNOSTICS} \
    DATABASE_URL=postgresql://opencut:opencut@localhost:5432/opencut \
    BETTER_AUTH_SECRET=build-time-placeholder-secret \
    UPSTASH_REDIS_REST_URL=http://localhost:8079 \
    UPSTASH_REDIS_REST_TOKEN=build-time-placeholder-token \
    NEXT_PUBLIC_MARBLE_API_URL=https://api.marblecms.com \
    MARBLE_WORKSPACE_KEY=build-time-placeholder-workspace \
    CLOUDFLARE_ACCOUNT_ID=build-time-placeholder-cloudflare-account \
    R2_ACCESS_KEY_ID=build-time-placeholder-r2-access \
    R2_SECRET_ACCESS_KEY=build-time-placeholder-r2-secret \
    R2_BUCKET_NAME=build-time-placeholder-r2-bucket \
    MODAL_TRANSCRIPTION_URL=https://example.com

RUN cd apps/web && bun run build


FROM python:3.11-slim AS python-builder

WORKDIR /build/backend

COPY backend/requirements.txt ./requirements.txt

RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


FROM node:20-bookworm-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/srv/backend \
    PATH=/opt/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    NODE_ENV=production \
    APP_PORT=3000 \
    NUXT_PORT=3001 \
    OPENCUT_PORT=3002 \
    FASTAPI_PORT=8000 \
    NEXT_PUBLIC_FASTAPI_URL=/api/v1 \
    NEXT_PUBLIC_EDITOR_BASE_PATH=/editor \
    NEXT_PUBLIC_EDITOR_RETURN_TO=/editor \
    NEXT_PUBLIC_EDITOR_DIAGNOSTICS=false

WORKDIR /srv

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        ffmpeg \
        libpq5 \
        nginx \
        python3 \
        python3-pip \
        python3-venv \
        supervisor \
    && python3 -m venv /opt/venv \
    && rm -rf /var/lib/apt/lists/*

COPY --from=python-builder /wheels /tmp/wheels
RUN /opt/venv/bin/pip install --no-cache-dir /tmp/wheels/* \
    && rm -rf /tmp/wheels

COPY backend /srv/backend

COPY --from=nuxt-builder /build/frontend/.output /srv/frontend/.output

COPY --from=opencut-builder /build/opencut/apps/web/public /srv/opencut/apps/web/public
COPY --from=opencut-builder /build/opencut/apps/web/.next/standalone /srv/opencut
COPY --from=opencut-builder /build/opencut/apps/web/.next/static /srv/opencut/apps/web/.next/static

COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker/supervisord.conf /etc/supervisor/conf.d/socialmediaai.conf

RUN mkdir -p /run/nginx /srv/backend/temp /var/log/nginx /var/log/supervisor

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
    CMD curl -fsS "http://127.0.0.1:${APP_PORT}/api/health" >/dev/null || exit 1

CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
