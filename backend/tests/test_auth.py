"""
Authentication endpoint tests.
"""

import pytest


def test_register_user(client):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "name": "New User",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newuser@example.com"


def test_register_duplicate_email(client, test_user):
    """Test registration with existing email fails."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,
            "password": "password123",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "password123",  # Note: password validation not implemented in basic auth
        },
    )
    # Login will succeed as we're not validating passwords in dev mode
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_get_current_user(client, auth_headers):
    """Test getting current user information."""
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


def test_get_current_user_unauthorized(client):
    """Test unauthorized access to user endpoint."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403  # HTTPBearer returns 403 when no credentials


def test_logout(client, auth_headers):
    """Test logout endpoint."""
    response = client.post(
        "/api/v1/auth/logout",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"
