# Video Editor MCP Server

MCP server exposing **video editor** tools (trim, clip, duplicate, reverse, export) and **edit template** CRUD.  
All tools call the ElevoAI backend API. Used by Cursor, Claude Code, or other MCP clients.

## Setup

```bash
cd mcp
pip install -r requirements.txt
```

## Environment

| Variable | Description | Default |
|----------|-------------|---------|
| `ELEVO_API_URL` | Backend API base (no trailing slash) | `http://localhost:8000/api/v1` |
| `ELEVO_API_TOKEN` | Bearer token for auth (e.g. Supabase JWT) | (none) |

Create a token via your app’s login; use it when running the MCP so requests are user-scoped.

## Run

**Stdio (default, for Cursor):**

```bash
fastmcp run server.py
```

Or:

```bash
python server.py
```

**HTTP (optional):**

```bash
# In server.py, use mcp.run(transport="http", host="127.0.0.1", port=8000)
```

## Add to Cursor

1. Open Cursor **Settings** → **MCP** (or `~/.cursor/mcp.json`).
2. Add a server entry, for example:

```json
{
  "mcpServers": {
    "video-editor": {
      "command": "fastmcp",
      "args": ["run", "server.py"],
      "cwd": "/path/to/your/project/mcp",
      "env": {
        "ELEVO_API_URL": "http://localhost:8000/api/v1",
        "ELEVO_API_TOKEN": "<your-jwt>"
      }
    }
  }
}
```

Or with `python`:

```json
{
  "mcpServers": {
    "video-editor": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/your/project/mcp",
      "env": {
        "ELEVO_API_URL": "http://localhost:8000/api/v1",
        "ELEVO_API_TOKEN": "<your-jwt>"
      }
    }
  }
}
```

Replace `cwd` with your project’s `mcp` directory and `ELEVO_API_TOKEN` with a valid JWT.

## Tools

- **Editor ops:** `trim_clip`, `clip_out`, `duplicate_clip`, `reverse_clip`, `set_clip_speed`, `export_video`
- **Edit templates:** `list_edit_templates`, `get_edit_template`, `create_edit_template`, `delete_edit_template`, `apply_edit_template`

All editor ops take `video_id` (UUID of a user video). Ensure the backend is running and the token matches the user that owns the video.
