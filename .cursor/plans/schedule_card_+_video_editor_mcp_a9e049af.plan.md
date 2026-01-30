---
name: Schedule Card + Video Editor MCP
overview: "Fix the Dashboard Posting Schedule card (layout, colors, navigation to /schedule), then add a video editing and generation section: a CapCut-like in-app editor, edit templates in the content library, and a video-editor MCP server exposing granular edit tools for LLMs and users."
todos: []
isProject: false
---

# Posting Schedule Card Fixes + Video Editing Section and MCPs

## Part 1: Posting Schedule Card (Dashboard)

### 1.1 Layout and spacing (“everything super tight”)

**File:** [frontend/pages/dashboard.vue](frontend/pages/dashboard.vue)

- **Calendar grid:** The mini-calendar uses `grid-cols-7 gap-px`, `aspect-square`, `py-1` / `py-1.5`, `text-xs`, and `mb-4`. This makes it very compact.
  - Increase spacing: e.g. `gap-1` or `gap-1.5` instead of `gap-px`, `py-2` for day labels and cells, `text-sm` for labels.
  - Slightly relax aspect ratio or use `min-h` instead of `aspect-square` so cells are less cramped.
- **Header block:** The title/summary block uses `gap-4 mb-4` and `mt-0.5`. Add a bit more vertical rhythm (e.g. `mb-5` or `mb-6`) between header and calendar.
- **Scheduled posts list:** Posts use `p-3`, `mb-3`, `gap-3`. Increase padding and gaps (e.g. `p-4`, `gap-4`, `mb-4`) for breathing room.
- **“View schedule” CTA:** Give it more space (e.g. `mt-4` or `mt-5`) so it’s clearly separated from the list.

### 1.2 Lighter schedule colors

- **Calendar:** Replace `bg-surface-700` (grid container), `bg-surface-800/80` (day headers), and `bg-surface-800/50` (date cells) with lighter alternatives that still fit the dark theme, e.g.:
  - Grid container: `bg-surface-600/30` or `bg-surface-700/40`.
  - Day headers: `bg-surface-700/50` or `bg-surface-600/40`.
  - Date cells: `bg-surface-700/30` or `bg-surface-600/25`.
- **Scheduled post rows:** Same idea—use lighter fills than `bg-surface-800/50` (e.g. `bg-surface-700/40`) so the schedule area feels lighter overall.

### 1.3 Navigation to Schedule section

- The card uses `Card` with `variant="interactive"` and `:to="localePath('/schedule')"`. [Card](frontend/components/ui/Card.vue) renders a `NuxtLink` when `to` is set, so the **entire** card is the link to `/schedule`.
- **Verify:** Confirm that clicking anywhere on the card (including “View schedule”) actually navigates to [frontend/pages/schedule/index.vue](frontend/pages/schedule/index.vue). Check for:
  - Overlays or positioning that block clicks.
  - `localePath('/schedule')` resolving correctly with i18n (`strategy: 'prefix_except_default'`; default locale has no prefix).
- **If navigation still fails:** Ensure no `@click` or other handlers swallow events. Consider wrapping the “View schedule” label in a `NuxtLink` to `/schedule` as an explicit CTA. That would require **not** making the whole card a link (avoid nested `<a>`): turn the card into a `div` and add a dedicated “View schedule” `NuxtLink` button/link. Prefer fixing the whole-card link first; only switch to “card + separate link” if needed.

---

## Part 2: Video Editing and Generation Section

### 2.1 Scope (per PRD and your requirements)

- **PRD:** Automated video editing (FFmpeg), pattern/script-based edits, platform-specific outputs ([PRD §7.5](PRD.md)), “Advanced video editing UI with timeline and preview” as future.
- **Your direction:** A **video editing and generation** section as a main app pillar: “small CapCut” in-app editor, **edit templates** in the content library that apply the same edit style to raw materials, and **MCPs** so LLMs can perform edits via tools.

### 2.2 New app section: Video Editor

- **Place in app:** New section distinct from “Videos” (upload/list/analyze). Options:
  - **A)** New sidebar item “Editor” (or “Video Editor”) linking to `/editor` (or `/video-editor`), with optional `?video=id` or project-based routing.
  - **B)** Sub-section under Videos: e.g. “Videos” → “Editor” tab or `/videos/editor`, `/videos/editor/:projectId`.
- **Dashboard:** Add an overview card for “Video Editor” (or “Edit & Generate”) that links to this section, similar to Schedule / Videos / Analytics.

**Recommendation:** Add a dedicated **Editor** (or **Video Editor**) nav item and route (e.g. `/editor`) so it’s first-class, and a dashboard card linking to it.

### 2.3 “Small CapCut” – in-app editor capabilities

Users (and later, LLMs via MCP) should be able to:

- **Timeline:** Multi-track timeline (video, audio).
- **Trimming / segmentation:** Cut, clip out, duplicate segments; move a segment from time X to time Y.
- **Insert elements:** Insert video, audio, images at a chosen position; control placement (position, layer).
- **Layers:** Work with layers (order, visibility), e.g. overlays, text, graphics.
- **Templates:** Apply an **edit template** from the content library so the same edit style (cuts, pacing, overlays, etc.) is applied to raw materials.

**Tech direction:**

- **Frontend:** No video-editor library in [frontend/package.json](frontend/package.json) today. Options:
  - Use a **timeline + playback** library (e.g. **Remotion**, **Fabric.js** + canvas, or a lightweight timeline UI) and implement trim/insert/layers on top.
  - Or **FFmpeg.wasm** (or backend FFmpeg) for actual cuts/concatenation; frontend sends edit ops to the backend, which runs FFmpeg and returns preview/export URLs.
- **Backend:** Extend [backend/app/services/video_editor.py](backend/app/services/video_editor.py) (and possibly Celery tasks in [backend/app/workers/video_tasks.py](backend/app/workers/video_tasks.py)) to execute low-level operations: clip_out, duplicate, move_segment, insert_video, insert_audio, add_overlay, layer ordering, etc. These become the **implementation** used by both the UI and the MCP server.

### 2.4 Edit templates and content library

- **Content library today:** Videos, [Materials](frontend/pages/account/materials.vue) (logos, images), [video_templates](backend/app/models/pattern.py) (pattern analysis). “Content library” in your wording = these plus **edit templates**.
- **Edit templates:** Define a **reusable edit style** (e.g. cuts, segment lengths, overlay positions, music placement) that can be applied to **raw materials** (uploaded videos). Store them in a way that:
  - Supports listing, creating, updating, deleting.
  - Can be referenced when applying edits (user UI or MCP).
- **Implementation options:**
  - **New store:** e.g. `edit_templates` table (or similar) with `user_id`, `name`, `style_spec` (JSON schema for cuts, overlays, layers, etc.), linked to materials/videos as needed.
  - **Extend existing:** e.g. store edit-style specs in `video_templates` or a new `template_data`-like structure, clearly separated from pattern-analysis data.
- **Apply flow:** User (or LLM) selects an edit template + raw video(s); editor or backend applies that style (via the same low-level edit ops used by the CapCut-like UI).

### 2.5 MCP server for video editing

- **Goal:** LLMs can edit videos through **MCP tools**. Each **edit operation** is a separate **tool** (e.g. `clip_out`, `duplicate`, `move_segment`, `insert_video`, `insert_audio`, `add_overlay`, `reorder_layers`). You can implement this as either:
  - **One MCP server** (“video-editor MCP”) exposing **many tools**, or
  - **Multiple MCP servers**, each exposing one or a small set of tools.
- **Recommendation:** **Single video-editor MCP server** with many tools. Simpler to deploy, auth, and version. Same tools can be called by Cursor, in-app chat, or other MCP clients.

**Example tools (each = one MCP tool):**


| Tool                  | Purpose                                                         |
| --------------------- | --------------------------------------------------------------- |
| `clip_out`            | Remove segment [start, end] from a track                        |
| `duplicate`           | Duplicate a segment (optionally to another time or track)       |
| `move_segment`        | Move segment from time X to time Y                              |
| `insert_video`        | Insert video asset at position, optionally with layer           |
| `insert_audio`        | Insert audio at position                                        |
| `insert_image`        | Insert image overlay at position                                |
| `add_text_overlay`    | Add text at position, with placement params                     |
| `reorder_layers`      | Change layer order                                              |
| `apply_edit_template` | Apply an edit template from the content library to raw video(s) |


- **Where it runs:** New **MCP server** process (e.g. Node or Python), separate from the FastAPI app. It implements the MCP protocol and calls:
  - **Backend REST** (or internal APIs) for auth, asset resolution (videos, materials), and **edit execution**.
  - **Edit execution** ultimately uses the same FFmpeg-based services (e.g. `VideoEditorService`) or Celery tasks that the in-app editor uses.

**Auth:** MCP requests must be scoped to a user (e.g. JWT or API key passed in MCP context). Backend validates and runs edits only for that user’s assets.

### 2.6 Parity between user editor and MCP

- **Single source of truth:** The same low-level edit operations (clip, move, insert, layers, etc.) are used by:
  1. **In-app “CapCut-like” editor** (user actions → same ops).
  2. **MCP tools** (LLM → MCP → backend → same ops).
- **Edit templates** are used both in the UI (“Apply template”) and via an MCP tool (`apply_edit_template`). No duplicate edit logic.

---

## Part 3: Implementation outline

### Phase 1 – Schedule card (quick wins)

1. In [dashboard.vue](frontend/pages/dashboard.vue): relax Schedule card layout (calendar grid, header, list, “View schedule” spacing) and switch schedule-related blocks to lighter colors as above.
2. Verify Schedule card navigation to `/schedule`; fix any broken link or blocked clicks (including “View schedule”).

### Phase 2 – Video editor section and backend ops

1. Add **Editor** (or **Video Editor**) to sidebar and dashboard overview; create `/editor` (or `/video-editor`) route and page.
2. Design **edit template** schema and storage (new table or extended existing). Add CRUD APIs and, if needed, content-library UI for “Edit templates.”
3. Extend [video_editor.py](backend/app/services/video_editor.py) and workers with **concrete edit operations** (clip_out, duplicate, move_segment, insert_video, insert_audio, overlay, layer order). Implement enough that both UI and MCP can call them (e.g. via REST or internal service calls).
4. Build **minimal “CapCut-like” UI**: timeline, track(s), trim/cut, insert elements, layer ordering. Use existing or new frontend packages as chosen; wire actions to backend edit ops.

### Phase 3 – MCP server and tool contract

1. Add **video-editor MCP server** (new repo or `mcp/` in monorepo). Expose tools: `clip_out`, `duplicate`, `move_segment`, `insert_video`, `insert_audio`, `insert_image`, `add_text_overlay`, `reorder_layers`, `apply_edit_template`, plus any helpers (e.g. `list_edit_templates`, `get_project`).
2. Implement **auth** (user-scoped) and **callbacks** to backend for asset resolution and edit execution.
3. Document how to run the MCP server and configure Cursor (or other clients) to use it. Optionally wire these tools into the in-app **Strategies** chat (similar to [chat_tools](backend/app/services/chat_tools.py)) so the LLM can edit videos from the app as well.

### Phase 4 – Polish

1. **Apply edit template** flow in UI: select template + raw video → apply → preview/export.
2. Iterate on timeline UX, loading states, and error handling for both editor and MCP-driven edits.

---

## Key files and references

- **Schedule card:** [frontend/pages/dashboard.vue](frontend/pages/dashboard.vue) (lines 109–164), [frontend/components/ui/Card.vue](frontend/components/ui/Card.vue).
- **Schedule page:** [frontend/pages/schedule/index.vue](frontend/pages/schedule/index.vue), route `/schedule`.
- **Video editor service:** [backend/app/services/video_editor.py](backend/app/services/video_editor.py); [backend/app/workers/video_tasks.py](backend/app/workers/video_tasks.py) (`edit_video` task).
- **Chat / tools:** [backend/app/services/chat_tools.py](backend/app/services/chat_tools.py), [backend/app/api/v1/endpoints/chat.py](backend/app/api/v1/endpoints/chat.py).
- **Content library:** Materials [backend API](backend/app/api/v1/endpoints/materials.py), [user_assets](backend/app/models/user_asset.py); [video_templates](backend/app/models/pattern.py), [template_segments](backend/app/models/pattern.py).
- **Sidebar / dashboard:** [frontend/layouts/app-sidebar.vue](frontend/layouts/app-sidebar.vue), [frontend/pages/dashboard.vue](frontend/pages/dashboard.vue).

---

## Open decisions

1. **Editor route:** `/editor` vs `/video-editor` vs `/videos/editor` (or tabs under Videos). Affects nav and dashboard.
2. **Timeline implementation:** Remotion vs FFmpeg.wasm vs custom canvas/timeline + backend FFmpeg. Trade-offs: complexity, offline vs server-side, preview fidelity.
3. **Edit template storage:** New `edit_templates` (or similar) table vs extending `video_templates` / pattern models. Prefer a dedicated store for “edit style” separate from pattern analysis.
4. **MCP placement:** Same repo (`mcp/` or `tools/`) vs separate repo. Same repo simplifies shared types and deploy orchestration.

