"""
Video Editor MCP Server.
Exposes foundation editor ops and edit templates as MCP tools.
Calls ElevoAI backend API (env: ELEVO_API_URL, ELEVO_API_TOKEN).
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from fastmcp import FastMCP

API_URL = os.environ.get("ELEVO_API_URL", "http://localhost:8000/api/v1").rstrip("/")
API_TOKEN = os.environ.get("ELEVO_API_TOKEN", "")

mcp = FastMCP(
    "video-editor",
    instructions="Video editor tools: trim, clip, duplicate, reverse, export; edit templates CRUD.",
)


def _headers() -> dict[str, str]:
    h = {"Content-Type": "application/json"}
    if API_TOKEN:
        h["Authorization"] = f"Bearer {API_TOKEN}"
    return h


def _post(path: str, json: dict[str, Any]) -> dict[str, Any]:
    with httpx.Client(timeout=60.0) as c:
        r = c.post(f"{API_URL}{path}", json=json, headers=_headers())
        r.raise_for_status()
        return r.json() if r.content else {}


def _get(path: str) -> dict[str, Any]:
    with httpx.Client(timeout=30.0) as c:
        r = c.get(f"{API_URL}{path}", headers=_headers())
        r.raise_for_status()
        return r.json() if r.content else {}


def _delete(path: str) -> None:
    with httpx.Client(timeout=30.0) as c:
        c.delete(f"{API_URL}{path}", headers=_headers())


# --- Editor ops ---


@mcp.tool()
def trim_clip(video_id: str, start: float, end: float) -> dict[str, Any]:
    """Trim video to [start, end] seconds."""
    return _post(f"/editor/{video_id}/op", {"op": "trim_clip", "params": {"start": start, "end": end}})


@mcp.tool()
def clip_out(video_id: str, start: float, end: float) -> dict[str, Any]:
    """Remove segment [start, end] from video."""
    return _post(f"/editor/{video_id}/op", {"op": "clip_out", "params": {"start": start, "end": end}})


@mcp.tool()
def duplicate_clip(video_id: str) -> dict[str, Any]:
    """Duplicate the video clip."""
    return _post(f"/editor/{video_id}/op", {"op": "duplicate_clip", "params": {}})


@mcp.tool()
def reverse_clip(video_id: str) -> dict[str, Any]:
    """Reverse video playback."""
    return _post(f"/editor/{video_id}/op", {"op": "reverse_clip", "params": {}})


@mcp.tool()
def set_clip_speed(video_id: str, speed: float = 1.0) -> dict[str, Any]:
    """Set playback speed (e.g. 0.5, 2.0)."""
    return _post(f"/editor/{video_id}/op", {"op": "set_clip_speed", "params": {"speed": speed}})


@mcp.tool()
def export_video(
    video_id: str,
    width: int = 1920,
    height: int = 1080,
) -> dict[str, Any]:
    """Export video to target resolution."""
    return _post(
        f"/editor/{video_id}/op",
        {"op": "export_video", "params": {"width": width, "height": height}},
    )


# --- Edit templates ---


@mcp.tool()
def list_edit_templates(limit: int = 50, offset: int = 0) -> dict[str, Any]:
    """List edit templates (reusable edit styles)."""
    return _get(f"/edit-templates?limit={limit}&offset={offset}")


@mcp.tool()
def get_edit_template(template_id: str) -> dict[str, Any]:
    """Get an edit template by ID."""
    return _get(f"/edit-templates/{template_id}")


@mcp.tool()
def create_edit_template(name: str, description: str = "", style_spec: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create an edit template."""
    return _post(
        "/edit-templates",
        {"name": name, "description": description, "style_spec": style_spec or {}},
    )


@mcp.tool()
def delete_edit_template(template_id: str) -> dict[str, Any]:
    """Delete an edit template."""
    _delete(f"/edit-templates/{template_id}")
    return {"ok": True, "id": template_id}


@mcp.tool()
def apply_edit_template(template_id: str, video_id: str) -> dict[str, Any]:
    """Apply an edit template to a video. Queues apply (implementation in progress)."""
    return _post(f"/edit-templates/{template_id}/apply", {"video_id": video_id})


if __name__ == "__main__":
    mcp.run()
