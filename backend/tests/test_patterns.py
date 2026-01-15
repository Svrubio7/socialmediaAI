"""
Pattern endpoint tests.
"""

import pytest


def test_list_patterns_empty(client, auth_headers):
    """Test listing patterns when none exist."""
    response = client.get(
        "/api/v1/patterns",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_patterns_unauthorized(client):
    """Test listing patterns without authentication."""
    response = client.get("/api/v1/patterns")
    assert response.status_code == 403


def test_get_pattern_not_found(client, auth_headers):
    """Test getting a non-existent pattern."""
    response = client.get(
        "/api/v1/patterns/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_get_pattern_insights_empty(client, auth_headers):
    """Test getting pattern insights when none exist."""
    response = client.get(
        "/api/v1/patterns/insights",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_patterns"] == 0
    assert data["average_score"] == 0.0
