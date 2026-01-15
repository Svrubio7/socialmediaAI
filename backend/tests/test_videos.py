"""
Video endpoint tests.
"""

import pytest
from io import BytesIO


def test_list_videos_empty(client, auth_headers):
    """Test listing videos when none exist."""
    response = client.get(
        "/api/v1/videos",
        headers=auth_headers,
    )
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
    response = client.get(
        "/api/v1/videos/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_delete_video_not_found(client, auth_headers):
    """Test deleting a non-existent video."""
    response = client.delete(
        "/api/v1/videos/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_analyze_video_not_found(client, auth_headers):
    """Test analyzing a non-existent video."""
    response = client.post(
        "/api/v1/videos/00000000-0000-0000-0000-000000000000/analyze",
        headers=auth_headers,
    )
    assert response.status_code == 404
