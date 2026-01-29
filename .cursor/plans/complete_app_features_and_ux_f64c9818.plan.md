---
name: Complete app features and UX
overview: Strategies page as LLM-powered chatbot (left) with result cards (right) for schedule changes, scripts, and documents; custom MCPs for full platform control (schedules, documents, strategies, OAuth); plus account, schedule, materials, colours/icons, and suggested enhancements.
todos: []
isProject: false
---

# Complete App: Features, Account, Schedule, Chatbot, and MCPs

## 1. Strategies page: chatbot + LLM with result cards (right panel)

**Goal**: Replace the current Strategies list/modal with a **conversational interface**. The user explains their needs in chat; the LLM returns structured outcomes that appear as cards on the right (schedule changes, generated scripts, strategy documents, etc.).

**Layout**

- **Left (~40–50% width)**: Chat UI connected to an LLM API.
  - Message list (user + assistant), input at bottom.
  - Optional: system prompt that sets context (e.g. "You are a marketing strategist for ElevoAI. The user can ask for video scripts, schedule changes, strategy refinements. Use the available tools to apply changes.")
  - Support streaming for assistant replies.
- **Right (~50–60% width)**: **Result cards** that update as the LLM (via backend tools/MCP) produces outcomes:
  - **Schedule changes** – e.g. "Post moved to Friday 6 PM", "3 new posts scheduled"; each as a small card with date, platform, video, action (view in Schedule).
  - **Generated documents** – scripts for videos, strategy notes, marketing copy; each as a card with title, snippet, "View full" / "Save to Scripts" / "Export".
  - **Strategy updates** – e.g. "Strategy refined for Instagram"; card linking to strategy detail or export.
  - Cards are appended when the backend reports a tool result (e.g. via SSE, or in the chat response payload). Style: same Card component, icons (Calendar, FileText, Target), optional left border by type.

**Backend: chat + LLM + tools**

- New endpoint(s), e.g.:
  - `POST /chat` or `POST /strategies/chat`: accepts `messages[]` (and optionally `session_id`); calls LLM API (OpenAI, Anthropic, or configurable provider) with **tool/function definitions** that mirror platform capabilities (list schedule, create/reschedule/cancel post, create script, create/update strategy, list videos, etc.).
- When the LLM requests a tool call, the backend executes the corresponding action (direct service calls or via MCP – see section below), then returns the tool result to the LLM and optionally sends a **structured event** to the client (e.g. "schedule_updated", "script_created") so the frontend can add/update a card on the right.
- Response format: either streaming (SSE) with chunks for text and separate events for "card" payloads, or a single JSON response that includes both `message` and `cards[]` (or `tool_results` that the frontend maps to cards).
- Authentication: same as rest of app (current user from Supabase/JWT); all tool executions are scoped to that user.

**Frontend**

- New [frontend/pages/strategies/index.vue](frontend/pages/strategies/index.vue) (or keep route, full redesign): two-column layout (chat | cards). Chat component: message list, input, send button; call `POST /chat` (or streaming endpoint), display assistant message(s), and on each tool-result event (or in response) render/append a card in the right column. Cards can link to `/schedule`, `/scripts`, `/strategies/[id]`, etc. Keep existing style (no emojis, mono font, primary/accent).

**Scripts page**

- Scripts can remain a **standalone list/detail page** for "saved" scripts. The chatbot can create scripts via tools (e.g. `create_script`); those appear as "Generated documents" cards with an option to "Save to Scripts" (persist via API). So: chat produces scripts and other docs; Scripts page remains the place to browse, edit, and export saved scripts. Optionally keep a small "Generate script" form on the Scripts page that calls the existing script-generation API for users who prefer a form over chat.

---

## 2. Custom MCPs (Model Context Protocol) for full platform control

**Goal**: Build our own MCP server(s) so that chatbots (and any LLM client that supports MCP) can fully interact with the platform: read and modify schedules, create and update documents and scripts, refine marketing strategies, and trigger actions such as connecting social accounts.

**Why MCP**

- MCP gives a standard way to expose "tools" (list_scheduled_posts, reschedule_post, create_script, etc.) that any MCP-capable client (our backend chat service, Cursor, or other agents) can call.
- The backend chat endpoint can use an **MCP client** to call these tools when the LLM requests an action, keeping a single source of truth for platform capabilities and allowing reuse outside the in-app chat (e.g. CLI, external agents).

**MCP server(s) we implement**

- **ElevoAI platform MCP** – one or more MCP servers that expose tools for:
  - **Schedule**: `list_scheduled_posts`, `get_schedule`, `schedule_post` (video_id, platform(s), scheduled_at, caption?), `reschedule_post` (post_id, new_time), `cancel_scheduled_post` (post_id). Optional: `get_optimal_slots` (platform, date range) if we add that API.
  - **Documents / scripts**: `list_scripts`, `create_script` (concept, platform, duration, content?), `get_script` (id), `update_script` (id, content?), `export_script` (id, format). Optional: `create_document` (title, body, type) for generic strategy docs if we add a documents table.
  - **Strategies**: `list_strategies`, `get_strategy` (id), `create_strategy` (video_ids, platforms, goals?, niche?), `update_strategy` (id, strategy_data or partial), `export_strategy` (id, format).
  - **Content / videos**: `list_videos`, `get_video` (id), `get_patterns_for_video` (video_id). Optional: `trigger_analyze` (video_id).
  - **Materials**: `list_materials`, `upload_material` (type, file or url), `delete_material` (id) – once materials backend exists.
  - **Connected accounts**: `list_connected_platforms`, `get_oauth_connect_url` (platform) – returns URL for user to connect; optionally `disconnect_platform` (platform). Triggering "connect" means returning the auth URL so the client (or UI) can redirect the user; the chatbot can say "I've initiated connection for Instagram – please complete the flow in your browser."
- Each tool is implemented by the MCP server calling the existing backend APIs (HTTP) or the same app’s services (if MCP server runs inside the app). Authentication: MCP requests must be scoped to a user (e.g. backend chat passes user context when invoking MCP, or MCP server receives a token and validates it).

**Where the MCP server runs**

- **Option A**: Separate process (e.g. Node or Python MCP server) that the backend chat service calls via MCP transport (stdio or HTTP). The chat service runs the LLM, gets tool calls from the LLM, translates them to MCP tool calls, and sends results back to the LLM.
- **Option B**: MCP tools are implemented **inside** the FastAPI app as internal service functions; the "MCP" layer is just a well-defined list of tool names and schemas that the LLM client (our chat endpoint) uses to call these functions directly. This avoids a separate MCP process but still gives a clear, reusable tool contract; we can later expose the same tools via a real MCP server for external agents.

**Chat backend integration**

- The chat endpoint (section 1) uses **tool/function definitions** that match the MCP tool list (name, description, parameters schema). When the LLM returns a tool call, the backend either (a) calls the MCP server (if Option A) or (b) calls the corresponding internal function (if Option B), then returns the result to the LLM and emits a card payload to the frontend when applicable (e.g. "schedule_updated", "script_created").

**Deliverables**

- Define the full list of MCP tools (names, descriptions, input schemas) for schedule, scripts, strategies, videos, materials, connected accounts.
- Implement the tools (either as MCP server in a separate repo/folder, or as internal FastAPI/service functions with the same interface).
- Document how to run and use the MCP (e.g. for Cursor or other clients) if we expose it externally.
- Wire the chat endpoint to these tools so the in-app Strategies chatbot can modify schedules, create files/documents, refine strategies, and trigger account-connection flows.

---

## 3. More colours and icons (lighter, less flat dark)

**Current state**

- [frontend/tailwind.config.ts](frontend/tailwind.config.ts): primary (sage green), accent (cream), surface (grays). Dashboard and cards are mostly surface-8xx/9xx with small coloured icon boxes.
- [frontend/components/shared/PlatformIcon.vue](frontend/components/shared/PlatformIcon.vue): already provides Instagram, TikTok, YouTube, Facebook SVGs with filled/outline variants.

**Planned changes**

- **Colour**: Use primary/accent/emerald/amber more visibly: stronger icon backgrounds (e.g. `bg-primary-500/20` or `bg-accent-500/15`), subtle coloured left borders on cards (`border-l-4 border-primary-500`), coloured badges and links. Keep background dark (surface-950) but add coloured accents to headings, stat cards, and action cards so the UI is not uniformly gray.
- **Icons**: Use lucide-vue-next consistently: Upload, Target, Send, Calendar, User, Settings, Image, Link, etc. Ensure every action (Generate Strategy, Generate Script, Connect, Publish, View schedule) has an explicit icon. Use PlatformIcon wherever a platform (Instagram, TikTok, YouTube, Facebook) is shown so social icons are always present.
- **No emojis**: Keep copy and UI text icon-free (no emoji); use only Icon/PlatformIcon components.

---

## 4. My Materials (logos and assets)

**Goal**: A dedicated section where users upload and manage brand assets (logos, images, etc.) for use in content.

**Backend**

- New table `user_assets` (or `materials`): `id`, `user_id`, `type` (e.g. logo, image, watermark), `filename`, `storage_path`, `url` (or derived from storage), `metadata` (jsonb), `created_at`, `updated_at`. RLS for user_id.
- New storage bucket or folder (e.g. `materials/{user_id}/`) for uploads; reuse existing storage pattern from videos if possible ([backend/app/api/v1/endpoints/videos.py](backend/app/api/v1/endpoints/videos.py)).
- Endpoints: `GET /materials` (list), `POST /materials/upload` (upload file, type), `GET /materials/{id}`, `DELETE /materials/{id}`.

**Frontend**

- New page: [frontend/pages/account/materials.vue](frontend/pages/account/materials.vue) (or [frontend/pages/materials/index.vue](frontend/pages/materials/index.vue)) under app layout: list of assets by type (logos, images), upload area (drag-and-drop or button), delete. Use Card grid and icons (Image, Upload, Trash2). This page will be linked from the Account dropdown and optionally from a "My Materials" entry in the app nav or dashboard.

---

## 5. Account dropdown (top right) and account sections

**Goal**: Top-right "My Account" control in the app header; dropdown with Preferences, Materials, Profile, Connected Platforms; each with its own UI/section.

**App layout**

- In [frontend/layouts/app.vue](frontend/layouts/app.vue): keep logo left and "Back to website" link. Add on the **right** an account trigger (e.g. User icon or avatar) that opens a dropdown (reuse [frontend/components/ui/Dropdown.vue](frontend/components/ui/Dropdown.vue) or build a small popover). Dropdown items:
  - **Profile** – link to `/account/profile`
  - **Preferences** – link to `/account/preferences`
  - **My Materials** – link to `/account/materials`
  - **Connected Platforms** – link to `/account/connected-platforms`
  - (Optional) **Sign out** – call Supabase signOut and redirect.
- Style dropdown to match the site (surface-9xx, border-surface-7xx, primary/accent for hover/active). Use Icon (User, Settings, Image, Link2, LogOut) for each item.

**Account pages (each with its own UI)**

- **Profile** [frontend/pages/account/profile.vue](frontend/pages/account/profile.vue): display name, email, avatar (from Supabase user); edit name/avatar if desired. Same card/layout style as rest of app.
- **Preferences** [frontend/pages/account/preferences.vue](frontend/pages/account/preferences.vue): settings such as language (if not in header), timezone for scheduling, notification preferences, theme (dark/light if you add it later). Form with labels and save button.
- **My Materials** [frontend/pages/account/materials.vue](frontend/pages/account/materials.vue): as in section 3.
- **Connected Platforms** [frontend/pages/account/connected-platforms.vue](frontend/pages/account/connected-platforms.vue): move the current "Connected Accounts" block from [frontend/pages/publish/index.vue](frontend/pages/publish/index.vue) (or duplicate) here: list Instagram, TikTok, YouTube, Facebook with PlatformIcon, connect/disconnect buttons, status. Publish page can show a short summary + "Manage in Account" link.

All account pages use `layout: 'app'` and `middleware: 'auth'`. Optional: shared [frontend/layouts/account.vue](frontend/layouts/account.vue) with a sidebar (Profile, Preferences, Materials, Connected Platforms) for larger screens, or simple full-width pages with a back link to dashboard.

---

## 6. Dashboard: replace Connected Platforms with Posting Schedule (Notion-style)

**Goal**: Remove "Connected Platforms" from the dashboard. Add a **Posting Schedule** card (Notion-style): compact by default, expands on click, with an option to "Open full schedule" / full screen that navigates to the schedule page.

**Dashboard**

- In [frontend/pages/dashboard.vue](frontend/pages/dashboard.vue): remove the "Connected Platforms" card. Add a new **Schedule** card in the same grid position (e.g. next to Recent Videos).
- **Schedule card behaviour**:
  - **Collapsed**: Title "Posting Schedule", short summary (e.g. "3 posts scheduled" or "No upcoming posts"), small Calendar icon, "View schedule" link. Clicking the card (or a chevron) **expands** the card in place.
  - **Expanded**: Show a compact list of next N scheduled posts (e.g. from `api.posts.scheduled()` or a new dashboard endpoint): date/time, platform, video title. Button/link: "Open full schedule" or "View in full screen" that navigates to `/schedule`.
- Style: same Card, borders, and spacing as the rest of the dashboard; optional left border or icon in primary/accent to match Notion-like blocks.

**Schedule page**

- New page [frontend/pages/schedule/index.vue](frontend/pages/schedule/index.vue) (or [frontend/pages/publish/schedule.vue](frontend/pages/publish/schedule.vue)): full-screen view of the posting schedule.
  - Fetch scheduled posts via `GET /posts/scheduled` (already in [backend/app/api/v1/endpoints/posts.py](backend/app/api/v1/endpoints/posts.py)).
  - Display: list or calendar-like view by date; each item shows platform (with PlatformIcon), video, scheduled time, actions (Edit time, Cancel).
  - **Per-platform management**: tabs or filters (All, Instagram, TikTok, YouTube, Facebook) to filter scheduled posts by platform. Option to add new scheduled post (link to Publish flow with "Schedule" path).
  - Match site style (cards, mono font, primary/accent, no emojis).

---

## 7. Frontend for each main functionality

Ensure each area has a complete, usable UI with icons and consistent styling:


| Area           | Current                        | Add/Fix                                                                                                                                                                                                                               |
| -------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Videos**     | List, upload modal             | Ensure list shows thumbnails, status, actions (analyze, delete); upload uses Icon; detail or inline pattern summary if needed.                                                                                                        |
| **Strategies** | List, generate modal (stub)    | **Replace with chatbot + cards**: left = chat (LLM), right = result cards (schedule changes, scripts, strategy docs). Backend: chat endpoint with LLM + tool use (MCP). Strategy detail page strategies/[id].vue for export. |
| **Scripts**    | List, generate modal (stub)    | Wire generate to API; list refresh. Chat can create scripts via tools; "Save to Scripts" from chat cards. Script detail or expand inline; export.                                                                                   |
| **Publish**    | Connect accounts, publish form | Keep connect UI; add link "Manage connections in Account". Schedule flow: after choosing "Schedule", redirect to schedule page or show success + link to schedule.                                                                    |
| **Analytics**  | Dashboard stats, trends?       | Ensure charts/table use colours and icons; link to analytics from dashboard stat cards.                                                                                                                                               |
| **Schedule**   | N/A                            | New schedule page as above.                                                                                                                                                                                                           |
| **Account**    | N/A                            | Profile, Preferences, Materials, Connected Platforms pages + dropdown in app header.                                                                                                                                                  |


---

## 8. Formal requirements: feedback, detail pages, and UX polish

The following items are **in-scope** for the plan. Each has a clear goal, scope, and deliverable.

**8.1 Toasts / in-app notifications**

- **Goal**: Users receive immediate, non-blocking feedback after actions (generate, publish, schedule, save preferences, connect/disconnect, chat tool result) without relying on modals or page reloads.
- **Scope**: Success and error toasts; optional info. Auto-dismiss after a few seconds; stack or queue if multiple toasts. No emojis; use Icon (Check, X, AlertCircle) and short text.
- **Deliverables**: A composable `useToast()` (or equivalent) and a toast container component (e.g. [frontend/components/ui/Toast.vue](frontend/components/ui/Toast.vue) or shared/Toast.vue). Integrate into app layout or root so any page can trigger toasts. Use for: chat tool results, strategy/script generate, publish/schedule, preferences save, account connect/disconnect.

**8.2 Strategy detail page**

- **Goal**: Users can open a single strategy in full view and export it (Markdown/PDF).
- **Scope**: Page [frontend/pages/strategies/[id].vue](frontend/pages/strategies/[id].vue). Show full strategy content (strategy_data, platforms, goals, niche, created date). Actions: "Export as Markdown", "Export as PDF" (or link to backend export endpoint). Accessible from Strategies chat result cards and from a strategy list if we keep a compact list view elsewhere.
- **Deliverables**: Dynamic route `strategies/[id].vue`; fetch strategy by id (existing or new GET endpoint); render content with same Card/typography style; export buttons wired to backend export or client-side export.

**8.3 Script detail / expand and export**

- **Goal**: Users can view full script content and export it.
- **Scope**: Either a dedicated page [frontend/pages/scripts/[id].vue](frontend/pages/scripts/[id].vue) or an expandable row / modal on the Scripts list. Full script text (script_data), metadata (concept, platform, duration). Action: "Export" (JSON or text).
- **Deliverables**: Script detail view (page or modal); export action wired to backend or client-side export. Linked from Scripts list and from chat "Generated documents" cards when the card is a script.

**8.4 Timezone in preferences**

- **Goal**: Scheduled post times are shown and created in the user’s preferred timezone.
- **Scope**: Preferences page stores timezone (e.g. IANA string or offset). Backend accepts timezone when creating/updating scheduled posts, or stores UTC and frontend converts for display using stored preference. Schedule page and dashboard schedule card show times in user timezone.
- **Deliverables**: Preferences form field for timezone (dropdown or search); backend user preference storage (e.g. user profile or settings table); schedule list and schedule creation use this timezone for display and submission.

**8.5 Empty states (all lists)**

- **Goal**: Every list view has a consistent, actionable empty state so users know what to do next.
- **Scope**: Videos, Strategies (if list view exists), Scripts, Schedule, Materials, and any other list (e.g. analytics). Each empty state: icon (from Icon or shared/EmptyState), short title, one-line description, one primary action (e.g. "Upload first video", "Generate strategy", "Schedule a post").
- **Deliverables**: Reuse or extend [frontend/components/shared/EmptyState.vue](frontend/components/shared/EmptyState.vue). Ensure Videos, Scripts, Schedule, Materials, and any strategy list use it with appropriate copy and action.

**8.6 Loading states (lists and modals)**

- **Goal**: No blank content while data is loading; modals show loading during submit.
- **Scope**: Lists: skeleton rows or spinner (dashboard already has StatCardSkeleton; extend pattern to strategies, scripts, schedule, materials). Modals: disable submit button and show spinner or "Saving..." during API call.
- **Deliverables**: Skeleton or spinner on Videos list, Scripts list, Schedule list, Materials list, and strategy list where applicable. Loading prop/state on all modals that perform create/update (generate strategy, generate script, publish, schedule, preferences save).

**8.7 Breadcrumbs or back links**

- **Goal**: Users can return to Dashboard (or parent) from deep pages without using the browser back button only.
- **Scope**: Account pages (Profile, Preferences, Materials, Connected Platforms), Schedule page, and optionally Strategy detail, Script detail. Either a breadcrumb (Dashboard > Account > Preferences) or a single "Back to Dashboard" / "Back to Schedule" link at the top.
- **Deliverables**: A small Breadcrumb component or inline "Back to Dashboard" link on account and schedule pages; consistent placement (e.g. above page title). Optional: reusable [frontend/components/shared/Breadcrumb.vue](frontend/components/shared/Breadcrumb.vue) with configurable segments.

**8.8 Keyboard shortcut: Escape to close**

- **Goal**: Escape key closes the topmost modal or dropdown so power users can dismiss without clicking.
- **Scope**: All modals (generate strategy, generate script, publish confirm, etc.) and the account dropdown (and any other popover/dropdown). Only one layer at a time (Escape closes modal first, then dropdown if no modal).
- **Deliverables**: Global or per-component Escape listener: when Escape is pressed and a modal is open, close it; if dropdown is open and no modal, close dropdown. Implement in [frontend/components/ui/Modal.vue](frontend/components/ui/Modal.vue) and in the app header dropdown (or layout).

**8.9 Connected Platforms summary on Publish page**

- **Goal**: Publish page does not duplicate the full connect/disconnect UI; it shows a short summary and links to Account for management.
- **Scope**: On [frontend/pages/publish/index.vue](frontend/pages/publish/index.vue): replace or supplement the full "Connected Accounts" grid with a one-line summary (e.g. "3 of 4 platforms connected") and a link "Manage in Account" (or "Connected Platforms") to [frontend/pages/account/connected-platforms.vue](frontend/pages/account/connected-platforms.vue). Platform selection for publishing can still show which are connected (e.g. only connected platforms selectable) without full connect UI here.
- **Deliverables**: Publish page updated to show connection summary + link to account/connected-platforms; full connect/disconnect UI lives only on Account > Connected Platforms.

---

## 9. Implementation order (suggested)

1. **MCP tool contract and implementation** – Define MCP tools (schedule, scripts, strategies, videos, materials, connected accounts). Implement as internal FastAPI/service layer (or separate MCP server) so the chat backend can call them. Auth: scope all tools to current user.
2. **Chat backend** – `POST /chat` (or `/strategies/chat`) with LLM integration, tool definitions matching MCP, and streaming/events for "card" payloads when tools run.
3. **Strategies page redesign** – Two-column layout: chat UI (left), result cards (right). Wire chat to new endpoint; render schedule/script/strategy cards from tool results; links to Schedule, Scripts, strategy detail.
4. **Colours and icons** – Pass over dashboard, strategies (chat), scripts, publish; add accent colours and ensure every action has an icon (section 3).
5. **App header account dropdown** – Add trigger and dropdown with Profile, Preferences, Materials, Connected Platforms, Sign out (section 5).
6. **Account pages** – Profile, Preferences, Connected Platforms (move from dashboard/publish); stub Materials until backend exists (sections 4–5).
7. **Dashboard schedule card** – Replace Connected Platforms with expandable Schedule card; "Open full schedule" → `/schedule` (section 6).
8. **Schedule page** – Full schedule view, list from `/posts/scheduled`, per-platform filter, cancel/edit (section 6).
9. **My Materials backend + frontend** – Table, storage, API, then Materials page; add MCP tools for materials if not already done (section 4).
10. **Strategy detail page** – `strategies/[id].vue` for viewing/exporting strategies (requirement 8.2).
11. **Script detail / export** – Script detail view (page or modal) and export (requirement 8.3).
12. **Toasts** – useToast composable and Toast component; integrate for chat, publish, schedule, preferences, connect/disconnect (requirement 8.1).
13. **Timezone in preferences** – Store and use timezone in Preferences and in schedule display/creation (requirement 8.4).
14. **Empty states** – Ensure Videos, Scripts, Schedule, Materials (and strategy list if any) use EmptyState with copy and primary action (requirement 8.5).
15. **Loading states** – Skeleton/spinner for lists; loading state for modals (requirement 8.6).
16. **Breadcrumbs or back links** – On account and schedule pages (requirement 8.7).
17. **Escape to close** – Modal and dropdown close on Escape (requirement 8.8).
18. **Publish page connection summary** – One-line summary + link to Account > Connected Platforms (requirement 8.9).

---

## 10. File checklist (summary)


| Item                                                                                             | Action                                                                                            |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| Backend: MCP tools or MCP server                                                                 | Define and implement tools: schedule, scripts, strategies, videos, materials, connected_platforms. Auth per user. |
| Backend: chat endpoint                                                                           | POST /chat or /strategies/chat: LLM + tool calls; stream or return message + card payloads.       |
| [frontend/pages/strategies/index.vue](frontend/pages/strategies/index.vue)                       | Redesign: left = chat (message list, input); right = result cards from tool results.               |
| [frontend/pages/scripts/index.vue](frontend/pages/scripts/index.vue)                             | Wire generateScript to API; ensure icons; optional "Save to Scripts" from chat.                   |
| [frontend/layouts/app.vue](frontend/layouts/app.vue)                                             | Add account dropdown (right) with Profile, Preferences, Materials, Connected Platforms, Sign out. |
| [frontend/pages/account/profile.vue](frontend/pages/account/profile.vue)                         | Create – name, email, avatar.                                                                     |
| [frontend/pages/account/preferences.vue](frontend/pages/account/preferences.vue)                 | Create – language, timezone, notifications.                                                       |
| [frontend/pages/account/materials.vue](frontend/pages/account/materials.vue)                     | Create – list/upload/delete materials (after backend).                                            |
| [frontend/pages/account/connected-platforms.vue](frontend/pages/account/connected-platforms.vue) | Create – move connect/disconnect UI here.                                                         |
| [frontend/pages/dashboard.vue](frontend/pages/dashboard.vue)                                     | Replace Connected Platforms with expandable Schedule card; link to /schedule.                     |
| [frontend/pages/schedule/index.vue](frontend/pages/schedule/index.vue)                           | Create – full schedule, per-platform, manage posts.                                               |
| Backend: user_assets/materials                                                                   | Migration + endpoints for materials.                                                              |
| [frontend/pages/strategies/[id].vue](frontend/pages/strategies/[id].vue)                         | Create – strategy detail + export (requirement 8.2).                                              |
| [frontend/pages/scripts/[id].vue](frontend/pages/scripts/[id].vue) or script modal               | Create – script detail view + export (requirement 8.3).                                            |
| [frontend/components/ui/Toast.vue](frontend/components/ui/Toast.vue) (or shared)               | Create – toast container; useToast composable (requirement 8.1).                                  |
| Preferences: timezone                                                                           | Store timezone; use in schedule display/creation (requirement 8.4).                                |
| EmptyState usage                                                                                | Ensure all lists use EmptyState with copy + action (requirement 8.5).                              |
| Loading: lists and modals                                                                       | Skeleton/spinner for lists; loading state for modals (requirement 8.6).                           |
| Breadcrumb or back link                                                                         | Account and schedule pages (requirement 8.7).                                                      |
| Escape to close                                                                                 | Modal and Dropdown components (requirement 8.8).                                                  |
| [frontend/pages/publish/index.vue](frontend/pages/publish/index.vue)                             | Connection summary + link to Account > Connected Platforms (requirement 8.9).                     |
| Global: colours/icons                                                                            | Tailwind/card/icon pass on dashboard, strategies, scripts, publish (section 3).                   |

---

## 11. All in-scope suggestions (consolidated)

Every deliverable and suggestion from sections 1–10 in one numbered list. **Total in plan: 63 in-scope items.** Items 14 (Integrations) and 20 (Mobile) are explicitly **deferred** (out of scope for this plan).

**Strategies & chat (1–6)**

1. Strategies page: two-column layout (chat left ~40–50%, result cards right ~50–60%).
2. Chat UI: message list, input, send; optional system prompt; support streaming.
3. Result cards: Schedule changes, Generated documents, Strategy updates; append from tool results; same Card component, icons by type.
4. Backend: `POST /chat` or `POST /strategies/chat` with messages; LLM + tool definitions; stream or JSON with `message` + `cards[]`/tool_results; auth per user.
5. Frontend: strategies/index.vue redesign — chat | cards; wire to endpoint; cards link to /schedule, /scripts, /strategies/[id].
6. Scripts page: standalone list/detail; chat creates scripts via tools; "Save to Scripts" from cards; optional "Generate script" form.

**MCP (7–11)**

7. Define full MCP tool list: schedule, scripts, strategies, videos, materials, connected accounts (names, descriptions, input schemas).
8. Implement schedule tools: list_scheduled_posts, get_schedule, schedule_post, reschedule_post, cancel_scheduled_post; optional get_optimal_slots.
9. Implement script/strategy/video/materials/connected-accounts tools (list, get, create, update, export, upload, OAuth URL, etc.).
10. Implement tools as MCP server (Option A) or internal FastAPI/service layer (Option B); document if external.
11. Wire chat endpoint to MCP tools so in-app chatbot can modify schedule, create scripts/docs, refine strategies, trigger connect flows.

**Colours & icons (12–13)**

12. Colour pass: stronger icon backgrounds, coloured left borders on cards, coloured badges/links; keep dark base, add primary/accent/emerald/amber.
13. Icons: lucide-vue-next everywhere; every action has an icon; PlatformIcon for all platforms; no emojis.

**Materials (15–16)** *(14 = Integrations — deferred)*

15. Materials backend: table (user_assets/materials), storage bucket/folder, RLS; endpoints GET/POST/GET id/DELETE.
16. Materials frontend: account/materials page — list by type, upload (drag-drop or button), delete; Card grid, icons.

**Account (17–21)**

17. App header: account dropdown (Profile, Preferences, My Materials, Connected Platforms, Sign out); icons per item.
18. Profile page: display name, email, avatar; edit name/avatar.
19. Preferences page: language, timezone, notifications, theme (if added).
20. *(Mobile — deferred)*
21. Connected Platforms page: move full connect/disconnect UI from publish/dashboard; list platforms with PlatformIcon, connect/disconnect, status.
22. Optional: account layout with sidebar (Profile, Preferences, Materials, Connected Platforms) for larger screens.

**Dashboard & schedule (23–26)**

23. Dashboard: remove Connected Platforms card; add Posting Schedule card (Notion-style).
24. Schedule card: collapsed — title, summary (e.g. "3 posts scheduled"), "View schedule"; expanded — next N scheduled posts, "Open full schedule" → /schedule.
25. Schedule page: full-screen list or calendar view; fetch from GET /posts/scheduled; per-platform tabs/filters; edit time, cancel.
26. Schedule page: add new scheduled post (link to Publish flow with Schedule path).

**Frontend per area (27–33)**

27. Videos: list with thumbnails, status, actions (analyze, delete); upload with Icon; detail or inline pattern summary.
28. Strategies: replace list/modal with chat + result cards (see 1–6).
29. Scripts: wire generate to API; list refresh; "Save to Scripts" from chat; detail or expand inline; export.
30. Publish: keep connect summary; "Manage in Account" link; schedule flow → success + link to schedule.
31. Analytics: charts/table with colours and icons; link from dashboard stat cards.
32. Schedule: dedicated page (see 25–26).
33. Account: Profile, Preferences, Materials, Connected Platforms + dropdown (see 17–22).

**Formal requirements (34–42)**

34. Toasts: useToast composable + Toast container; success/error (and optional info); auto-dismiss; use for chat results, generate, publish, schedule, preferences, connect/disconnect.
35. Strategy detail page: strategies/[id].vue — full content, Export as Markdown/PDF.
36. Script detail: scripts/[id].vue or modal — full script, metadata, Export (JSON/text).
37. Timezone in preferences: store in preferences; schedule display and creation use user timezone.
38. Empty states: Videos, Strategies (if list), Scripts, Schedule, Materials, analytics — EmptyState with icon, title, description, primary action.
39. Loading states: skeleton/spinner for all lists; loading state on modals (generate, publish, schedule, preferences save).
40. Breadcrumbs or back links: account pages, schedule, strategy detail, script detail — "Back to Dashboard" or Breadcrumb component.
41. Escape to close: modal and dropdown close on Escape; one layer at a time.
42. Publish page: Connected Platforms summary (e.g. "3 of 4 connected") + "Manage in Account" link; full connect UI only on Account > Connected Platforms.

**Implementation & files (43–65)**

43. MCP tool contract and implementation (schedule, scripts, strategies, videos, materials, connected accounts); auth per user.
44. Chat backend: POST /chat with LLM, tool definitions, streaming/events for card payloads.
45. Strategies page redesign: two-column chat | cards; wire to endpoint; cards from tool results.
46. Colours and icons pass: dashboard, strategies, scripts, publish (section 3).
47. App header account dropdown (section 5).
48. Account pages: Profile, Preferences, Connected Platforms; stub Materials until backend (sections 4–5).
49. Dashboard: replace Connected Platforms with expandable Schedule card; "Open full schedule" → /schedule.
50. Schedule page: full view, list from /posts/scheduled, per-platform filter, cancel/edit.
51. Materials backend + frontend: table, storage, API, then Materials page; MCP tools for materials.
52. Strategy detail page: strategies/[id].vue, fetch by id, export Markdown/PDF.
53. Script detail/export: scripts/[id].vue or modal, export wired.
54. Toasts: useToast + Toast component; integrate across chat, publish, schedule, preferences, connect/disconnect.
55. Timezone in preferences: store and use in schedule display/creation.
56. Empty states: all lists use EmptyState with copy + primary action.
57. Loading states: skeleton/spinner for lists; loading on modals.
58. Breadcrumbs or back links on account and schedule pages.
59. Escape to close: Modal and Dropdown components.
60. Publish page: connection summary + link to Account > Connected Platforms.
61. Backend: MCP tools or MCP server; chat endpoint (POST /chat or /strategies/chat).
62. Frontend files: strategies, scripts, app layout, account/*, dashboard, schedule, Toast, preferences timezone.
63. Global: colours/icons pass on dashboard, strategies, scripts, publish.
64. Backend: analytics/summary endpoint with video_count, pattern_count, post_count (and optional change) for dashboard stat cards.
65. Frontend: dashboard wired to real API (stats, recent videos, connected platforms); loading states (skeletons).

---

## 12. All suggestions — grouped by section (reference)

Use this to find which numbered item (section 11) corresponds to each area.

- **Strategies & chat**: 1–6.
- **MCP**: 7–11.
- **Colours & icons**: 12–13.
- **Deferred**: 14 (Integrations), 20 (Mobile).
- **Materials**: 15–16.
- **Account**: 17–19, 21–22.
- **Dashboard & schedule**: 23–26.
- **Frontend per area**: 27–33.
- **Formal requirements (toasts, detail pages, timezone, empty/loading, breadcrumbs, Escape, Publish summary)**: 34–42.
- **Implementation order & file checklist**: 43–65.

---

This plan keeps the existing style (no emojis, mono font, dark base with primary/accent), adds colour and icons everywhere, fixes broken buttons, and introduces account, schedule, and materials as requested, plus concrete suggestions to make the app more complete.