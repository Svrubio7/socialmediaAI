"""
Video endpoint tests.
"""

from uuid import uuid4

from fastapi.responses import Response, StreamingResponse

from app.core.config import settings
from app.api.v1.endpoints import videos as videos_endpoint
from app.models.user import User
from app.models.video import Video, VideoStatus


def test_list_videos_empty(client, auth_headers):
    """Test listing videos when none exist."""
    response = client.get("/api/v1/videos", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["limit"] == 20


def test_list_videos_unauthorized(client):
    """Test listing videos without authentication."""
    response = client.get("/api/v1/videos")
    assert response.status_code == 403


def test_get_video_not_found(client, auth_headers):
    """Test getting a non-existent video."""
    response = client.get("/api/v1/videos/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert response.status_code == 404


def test_delete_video_not_found(client, auth_headers):
    """Test deleting a non-existent video."""
    response = client.delete("/api/v1/videos/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert response.status_code == 404


def test_analyze_video_not_found(client, auth_headers):
    """Test analyzing a non-existent video."""
    response = client.post("/api/v1/videos/00000000-0000-0000-0000-000000000000/analyze", headers=auth_headers)
    assert response.status_code == 404


def test_list_videos_supabase_returns_thumbnail_proxy(client, auth_headers, test_user, db):
    """For Supabase storage, list should return thumbnail proxy URL (not per-item signed URL)."""
    video = Video(
        id=uuid4(),
        user_id=test_user.id,
        filename="demo.mp4",
        original_filename="demo.mp4",
        storage_path=f"videos/{test_user.supabase_user_id}/demo.mp4",
        status=VideoStatus.UPLOADED,
        video_metadata={"thumbnail_storage_path": f"thumbnails/{test_user.supabase_user_id}/demo.jpg"},
    )
    db.add(video)
    db.commit()

    previous_storage_backend = settings.STORAGE_BACKEND
    settings.STORAGE_BACKEND = "supabase"
    try:
        response = client.get("/api/v1/videos", headers=auth_headers)
    finally:
        settings.STORAGE_BACKEND = previous_storage_backend

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["thumbnail_url"].endswith(f"/api/v1/videos/{video.id}/thumbnail")


def test_stream_thumbnail_requires_auth_when_not_debug(client):
    """Thumbnail proxy should enforce auth in non-debug mode."""
    previous_debug = settings.DEBUG
    settings.DEBUG = False
    try:
        response = client.get(f"/api/v1/videos/{uuid4()}/thumbnail")
    finally:
        settings.DEBUG = previous_debug

    assert response.status_code == 401


def test_stream_video_requires_auth_when_not_debug(client):
    """Video stream proxy should enforce auth in non-debug mode."""
    previous_debug = settings.DEBUG
    settings.DEBUG = False
    try:
        response = client.get(f"/api/v1/videos/{uuid4()}/stream")
    finally:
        settings.DEBUG = previous_debug

    assert response.status_code == 401


def test_stream_video_get_forwards_range_header(client, auth_headers, test_user, db, monkeypatch):
    """GET /videos/{id}/stream should forward range headers to remote stream fetch."""
    video = Video(
        id=uuid4(),
        user_id=test_user.id,
        filename="demo.mp4",
        original_filename="demo.mp4",
        storage_path=f"videos/{test_user.supabase_user_id}/demo.mp4",
        status=VideoStatus.UPLOADED,
    )
    db.add(video)
    db.commit()

    calls = {}

    def fake_build_public_url(storage_path, _request):
        calls["storage_path"] = storage_path
        return "https://cdn.example.com/demo.mp4"

    async def fake_stream_remote(url, range_header):
        calls["url"] = url
        calls["range"] = range_header

        async def iterator():
            yield b"ok"

        return StreamingResponse(iterator(), status_code=206, media_type="video/mp4")

    monkeypatch.setattr(videos_endpoint.storage, "build_public_url", fake_build_public_url)
    monkeypatch.setattr(videos_endpoint, "_stream_remote", fake_stream_remote)

    previous_storage_backend = settings.STORAGE_BACKEND
    settings.STORAGE_BACKEND = "local"
    try:
        response = client.get(
            f"/api/v1/videos/{video.id}/stream",
            headers={**auth_headers, "Range": "bytes=0-255"},
        )
    finally:
        settings.STORAGE_BACKEND = previous_storage_backend

    assert response.status_code == 206
    assert calls["storage_path"] == video.storage_path
    assert calls["url"] == "https://cdn.example.com/demo.mp4"
    assert calls["range"] == "bytes=0-255"


def test_stream_video_head_forwards_range_header(client, auth_headers, test_user, db, monkeypatch):
    """HEAD /videos/{id}/stream should forward range headers to remote head fetch."""
    video = Video(
        id=uuid4(),
        user_id=test_user.id,
        filename="demo.mp4",
        original_filename="demo.mp4",
        storage_path=f"videos/{test_user.supabase_user_id}/demo.mp4",
        status=VideoStatus.UPLOADED,
    )
    db.add(video)
    db.commit()

    calls = {}

    def fake_build_public_url(storage_path, _request):
        calls["storage_path"] = storage_path
        return "https://cdn.example.com/demo.mp4"

    async def fake_head_remote(url, range_header):
        calls["url"] = url
        calls["range"] = range_header
        return Response(
            status_code=206,
            headers={
                "accept-ranges": "bytes",
                "content-range": "bytes 0-255/1000",
            },
        )

    monkeypatch.setattr(videos_endpoint.storage, "build_public_url", fake_build_public_url)
    monkeypatch.setattr(videos_endpoint, "_head_remote", fake_head_remote)

    previous_storage_backend = settings.STORAGE_BACKEND
    settings.STORAGE_BACKEND = "local"
    try:
        response = client.head(
            f"/api/v1/videos/{video.id}/stream",
            headers={**auth_headers, "Range": "bytes=0-255"},
        )
    finally:
        settings.STORAGE_BACKEND = previous_storage_backend

    assert response.status_code == 206
    assert response.headers.get("accept-ranges") == "bytes"
    assert calls["storage_path"] == video.storage_path
    assert calls["url"] == "https://cdn.example.com/demo.mp4"
    assert calls["range"] == "bytes=0-255"


def test_stream_video_supabase_redirects_to_signed_url(client, auth_headers, test_user, db, monkeypatch):
    """Supabase-backed stream should redirect to signed URL instead of proxy-streaming."""
    video = Video(
        id=uuid4(),
        user_id=test_user.id,
        filename="demo.mp4",
        original_filename="demo.mp4",
        storage_path=f"videos/{test_user.supabase_user_id}/demo.mp4",
        status=VideoStatus.UPLOADED,
    )
    db.add(video)
    db.commit()

    def fake_build_public_url(storage_path, _request):
        assert storage_path == video.storage_path
        return "https://cdn.example.com/direct.mp4"

    async def fail_stream_remote(_url, _range_header):
        raise AssertionError("_stream_remote should not be called for Supabase redirects")

    monkeypatch.setattr(videos_endpoint.storage, "build_public_url", fake_build_public_url)
    monkeypatch.setattr(videos_endpoint, "_stream_remote", fail_stream_remote)

    previous_storage_backend = settings.STORAGE_BACKEND
    settings.STORAGE_BACKEND = "supabase"
    try:
        response = client.get(
            f"/api/v1/videos/{video.id}/stream",
            headers=auth_headers,
            follow_redirects=False,
        )
    finally:
        settings.STORAGE_BACKEND = previous_storage_backend

    assert response.status_code == 307
    assert response.headers.get("location") == "https://cdn.example.com/direct.mp4"


def test_media_urls_returns_owned_items_and_deduplicates(client, auth_headers, test_user, db):
    """Batch media-url endpoint should return only owned videos and dedupe repeated IDs."""
    own_video = Video(
        id=uuid4(),
        user_id=test_user.id,
        filename="mine.mp4",
        original_filename="mine.mp4",
        storage_path=f"videos/{test_user.supabase_user_id}/mine.mp4",
        status=VideoStatus.UPLOADED,
        video_metadata={"thumbnail_storage_path": f"thumbnails/{test_user.supabase_user_id}/mine.jpg"},
    )
    other_user = User(
        id=uuid4(),
        supabase_user_id=uuid4(),
        email="other@example.com",
        name="Other User",
        is_active=True,
    )
    other_video = Video(
        id=uuid4(),
        user_id=other_user.id,
        filename="other.mp4",
        original_filename="other.mp4",
        storage_path=f"videos/{other_user.supabase_user_id}/other.mp4",
        status=VideoStatus.UPLOADED,
    )
    db.add(other_user)
    db.add(own_video)
    db.add(other_video)
    db.commit()

    response = client.post(
        "/api/v1/videos/media-urls",
        json={
            "video_ids": [str(own_video.id), str(other_video.id), str(own_video.id)],
            "include_video": True,
            "include_thumbnail": True,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 1
    item = payload["items"][0]
    assert item["id"] == str(own_video.id)
    assert "video_url" in item
    assert "thumbnail_url" in item


def test_media_urls_respects_include_flags(client, auth_headers, test_user, db):
    """Batch media-url endpoint should include only requested URL types."""
    video = Video(
        id=uuid4(),
        user_id=test_user.id,
        filename="demo.mp4",
        original_filename="demo.mp4",
        storage_path=f"videos/{test_user.supabase_user_id}/demo.mp4",
        status=VideoStatus.UPLOADED,
        video_metadata={"thumbnail_storage_path": f"thumbnails/{test_user.supabase_user_id}/demo.jpg"},
    )
    db.add(video)
    db.commit()

    response = client.post(
        "/api/v1/videos/media-urls",
        json={
            "video_ids": [str(video.id)],
            "include_video": False,
            "include_thumbnail": True,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 1
    item = payload["items"][0]
    assert item["id"] == str(video.id)
    assert item["video_url"] is None
    assert "thumbnail_url" in item


def test_media_urls_rejects_invalid_id(client, auth_headers):
    """Batch media-url endpoint should fail fast on invalid UUIDs."""
    response = client.post(
        "/api/v1/videos/media-urls",
        json={"video_ids": ["not-a-uuid"]},
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "Invalid video id" in response.json()["detail"]


def test_register_video_accepts_editor_output_namespace(client, auth_headers, test_user):
    """Register endpoint should accept editor/outputs namespace for Elevo Editor exports."""
    previous_storage_backend = settings.STORAGE_BACKEND
    settings.STORAGE_BACKEND = "supabase"
    try:
        response = client.post(
            "/api/v1/videos/register",
            headers=auth_headers,
            json={
                "storage_path": f"editor/outputs/{test_user.supabase_user_id}/projects/project-a/export.mp4",
                "filename": "export.mp4",
            },
        )
    finally:
        settings.STORAGE_BACKEND = previous_storage_backend

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["filename"] == "export.mp4"
