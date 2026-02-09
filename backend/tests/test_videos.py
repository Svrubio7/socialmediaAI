"""
Video endpoint tests.
"""

from uuid import uuid4

from app.core.config import settings
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
