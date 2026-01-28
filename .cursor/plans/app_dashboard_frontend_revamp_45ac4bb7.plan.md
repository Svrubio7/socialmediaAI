---
name: App dashboard frontend revamp
overview: Introduce a dedicated app layout (logo-only top bar, no website nav), revamp the dashboard page for better alignment, icon placement, and space use, and wire dashboard stats to real data. Backend may need a small extension to expose counts for the stat cards.
todos: []
isProject: false
---

# App Dashboard Frontend Revamp

## 1. Database summary (investigation)

The project uses **Supabase** (and/or local Postgres via Alembic). Relevant tables:

- **users** – id, supabase_user_id, email, name, avatar_url, is_active, last_login
- **videos** – user_id, filename, storage_path, thumbnail_url, duration, status, etc.
- **patterns** – video_id, type, score, data (from video analysis)
- **strategies** – user_id, video_ids, platforms, goals, niche, strategy_data
- **scripts** – user_id, concept, platform, target_duration, script_data
- **social_accounts** – user_id, platform, platform_user_id, username, tokens (OAuth)
- **posts** – video_id, social_account_id, platform, status, scheduled_at, published_at
- **analytics** – post_id, views, likes, comments, shares, saves, engagement_rate
- **video_templates** / **template_segments** – video analysis templates

All tables have RLS enabled. Local migrations: [backend/app/db/migrations/versions/001_initial_schema.py](backend/app/db/migrations/versions/001_initial_schema.py), [002_add_video_templates.py](backend/app/db/migrations/versions/002_add_video_templates.py).

**Dashboard data today:** `GET /api/v1/analytics/dashboard` returns `total_views`, `total_engagement`, `average_engagement_rate`, `top_performing_videos`, `platform_breakdown`, `period_start/end`. It does **not** return `video_count`, `pattern_count`, or `post_count`, which the dashboard UI currently shows as hardcoded "0".

---

## 2. App layout (different from website)

**Goal:** App area has no full top bar; only logo top-left linking back to the website.

- **Add** [frontend/layouts/app.vue](frontend/layouts/app.vue):
  - Minimal header: fixed or sticky bar with **logo only** (left). Use existing [frontend/components/ui/Logo.vue](frontend/components/ui/Logo.vue) with `to` pointing to website home (e.g. `localePath('/')`). Optional: right side "Back to website" text link or user avatar/menu.
  - No nav links (Home, About, Pricing, Contact), no language switcher, no "Go to App" button.
  - Main content area: `<main class="flex-1"><slot /></main>`.
  - No [LayoutFooter](frontend/components/layout/Footer.vue) (or a minimal app footer if desired).
  - Same background as current app (`bg-surface-950`), consistent with [default.vue](frontend/layouts/default.vue).
- **Use app layout** for all authenticated app routes by setting `layout: 'app'` in `definePageMeta`:
  - [frontend/pages/dashboard.vue](frontend/pages/dashboard.vue)
  - [frontend/pages/videos/index.vue](frontend/pages/videos/index.vue)
  - [frontend/pages/strategies/index.vue](frontend/pages/strategies/index.vue)
  - [frontend/pages/scripts/index.vue](frontend/pages/scripts/index.vue)
  - [frontend/pages/publish/index.vue](frontend/pages/publish/index.vue)
  - [frontend/pages/analytics/index.vue](frontend/pages/analytics/index.vue)

Website routes (/, /about, /pricing, /contact) keep using the default layout (full Header + Footer).

---

## 3. Dashboard page revamp (alignment, icons, space)

**Current issues (from [dashboard.vue](frontend/pages/dashboard.vue)):**

- Stats grid: `flex items-start justify-between` puts the icon on the **right**; label/value on the left. This can look uneven across cards and wastes space.
- Icon containers: `w-10 h-10 lg:w-12 lg:h-12` with Icon size 20; alignment and visual weight can feel off.
- Quick actions: layout is acceptable (icon left, text right) but spacing and icon boxes should be consistent.
- Bottom section: two-column grid is fine; empty state and card heights can be tightened.

**Planned changes:**

1. **Stat cards**
  - Use a **consistent structure**: e.g. icon on the **left** in a fixed square box (e.g. `w-12 h-12`), then a column with label, value, and optional change line. This gives a clear left-to-right flow and even alignment across all four cards.
  - Ensure icon box is always square and flex-shrink-0; center the [Icon](frontend/components/ui/Icon.vue) (lucide-vue-next) inside. Use a single icon wrapper class (e.g. `flex items-center justify-center rounded-xl flex-shrink-0`) so all stat cards look the same.
  - Keep existing icons: Video, Target, Send, Eye (names are valid in Icon.vue). No placeholder divs; only Icon components.
2. **Spacing and grid**
  - Stats: keep `grid grid-cols-2 lg:grid-cols-4` but use a **tighter gap** (e.g. `gap-4` on all breakpoints or `gap-3 lg:gap-4`) so cards don’t feel too spread out.
  - Add a **max-width** for the dashboard content (reuse or mirror `container-wide` from [main.css](frontend/assets/css/main.css)) so on very wide screens the content doesn’t stretch excessively.
  - Quick actions: keep `md:grid-cols-3`; use same gap as stats for consistency.
  - Bottom section: `grid lg:grid-cols-2` with consistent gap (e.g. `gap-6`) and min-height or equal card height if needed so "Recent Videos" and "Connected Platforms" feel balanced.
3. **Quick action cards**
  - Standardize icon container: same square size (e.g. `w-12 h-12`), `rounded-xl`, centered icon. Keep current [Card](frontend/components/ui/Card.vue) `variant="interactive"` and links to /videos, /strategies, /publish.
4. **Recent Videos / Connected Platforms**
  - Keep existing [EmptyState](frontend/components/shared/EmptyState.vue) and list layouts.
  - Ensure platform list items use [PlatformIcon](frontend/components/shared/PlatformIcon.vue) and [StatusBadge](frontend/components/shared/StatusBadge.vue) with consistent spacing (e.g. `gap-3`, `p-3`).
5. **Optional**
  - Add a reusable **StatCard** (or similar) component that encapsulates icon-left + label + value + change line so the dashboard (and future pages) stay consistent and maintainable.

---

## 4. Dashboard data (real counts and lists)

**Current:** Stats are hardcoded (`value: '0'`, `change: 0`); `recentVideos` is `ref([])`; platforms are a static list with `connected: false`.

**Planned:**

1. **Backend**
  - **Option A (recommended):** Extend `GET /api/v1/analytics/dashboard` response (or add `GET /api/v1/analytics/summary`) to include:
    - `video_count`, `pattern_count`, `post_count` (and keep `total_views` from existing logic).
    - Optionally `video_count_change`, `pattern_count_change`, etc. for "from last week" (if desired).
  - **Option B:** Frontend calls multiple endpoints: e.g. `videos.list({ limit: 1 })` for total (if API returns total), plus patterns list, posts list, and existing analytics.dashboard() — only if backend changes are not possible; then aggregate counts on the client.
2. **Frontend**
  - In [dashboard.vue](frontend/pages/dashboard.vue): use [useApi](frontend/composables/useApi.ts) to:
    - Fetch dashboard/summary (or videos + patterns + posts + analytics) and map to `stats` (Total Videos, Patterns Found, Posts Published, Total Views) and optional week-over-week change.
    - Fetch recent videos: e.g. `videos.list({ limit: 5 })` and set `recentVideos`.
    - Fetch connected platforms: `oauth.accounts()` and map to the four platforms (Instagram, TikTok, YouTube, Facebook), setting `connected: true/false` per platform.
  - Show loading state (e.g. skeletons for stat cards and lists) while data is loading; keep [StatCardSkeleton](frontend/components/shared/StatCardSkeleton.vue) or align it with the new stat card structure.

---

## 5. File and endpoint checklist


| Area                                                                       | Action                                                                                                                                                                                                                                                              |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [frontend/layouts/app.vue](frontend/layouts/app.vue)                       | **Create** – logo-only header, main slot, no footer.                                                                                                                                                                                                                |
| [frontend/pages/dashboard.vue](frontend/pages/dashboard.vue)               | **Edit** – add `layout: 'app'`; refactor stat cards (icon left, spacing, grid); wire stats + recent videos + platforms to API; optional StatCard component.                                                                                                         |
| [frontend/pages/videos/index.vue](frontend/pages/videos/index.vue)         | **Edit** – add `layout: 'app'`.                                                                                                                                                                                                                                     |
| [frontend/pages/strategies/index.vue](frontend/pages/strategies/index.vue) | **Edit** – add `layout: 'app'`.                                                                                                                                                                                                                                     |
| [frontend/pages/scripts/index.vue](frontend/pages/scripts/index.vue)       | **Edit** – add `layout: 'app'`.                                                                                                                                                                                                                                     |
| [frontend/pages/publish/index.vue](frontend/pages/publish/index.vue)       | **Edit** – add `layout: 'app'`.                                                                                                                                                                                                                                     |
| [frontend/pages/analytics/index.vue](frontend/pages/analytics/index.vue)   | **Edit** – add `layout: 'app'`.                                                                                                                                                                                                                                     |
| Backend analytics                                                          | **Edit** – extend [DashboardResponse](backend/app/api/v1/endpoints/analytics.py) (or add summary endpoint) to include `video_count`, `pattern_count`, `post_count`; implement with existing DB session (count queries on videos, patterns, posts for current_user). |
| [frontend/composables/useApi.ts](frontend/composables/useApi.ts)           | **Edit** – if a new summary endpoint is added, expose it (e.g. `analytics.summary()`).                                                                                                                                                                              |


---

## 6. Order of implementation

1. **App layout** – Create `app.vue` and set `layout: 'app'` on dashboard, videos, strategies, scripts, publish, analytics.
2. **Dashboard layout and icons** – Refactor stat cards (icon left, consistent wrapper, spacing), quick actions, and bottom grid; no new API yet.
3. **Backend counts** – Extend analytics dashboard (or add summary) with video_count, pattern_count, post_count.
4. **Dashboard data** – Wire dashboard to real API (stats, recent videos, oauth.accounts() for platforms); add loading states.

This keeps layout and visual fixes first, then adds real data with minimal backend change.