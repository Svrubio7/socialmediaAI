from uuid import uuid4

from app.api.v1.endpoints import projects as projects_endpoint
from app.core.config import settings
from app.core.rate_limit import signed_upload_rate_limiter


def _create_project(client, auth_headers, name="Storage Test"):
    response = client.post(
        "/api/v1/projects",
        headers=auth_headers,
        json={"name": name},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_register_asset_allows_editor_assets_namespace(client, auth_headers, test_user):
    project = _create_project(client, auth_headers)
    user_scope = str(test_user.supabase_user_id)

    response = client.post(
        f"/api/v1/projects/{project['id']}/assets/register",
        headers=auth_headers,
        json={
            "kind": "image",
            "storage_path": f"editor/assets/{user_scope}/{project['id']}/{uuid4()}/poster.png",
            "filename": "poster.png",
            "metadata": {"elevo_editor_media_id": "asset-1"},
        },
    )

    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["kind"] == "image"
    assert payload["metadata"]["project_id"] == project["id"]


def test_register_asset_rejects_foreign_namespace(client, auth_headers, test_user):
    project = _create_project(client, auth_headers)

    response = client.post(
        f"/api/v1/projects/{project['id']}/assets/register",
        headers=auth_headers,
        json={
            "kind": "audio",
            "storage_path": f"editor/assets/{uuid4()}/{project['id']}/{uuid4()}/audio.mp3",
            "filename": "audio.mp3",
        },
    )

    assert response.status_code == 400
    assert "namespace" in response.json()["detail"].lower()


def test_project_only_asset_filter(client, auth_headers, test_user):
    project_a = _create_project(client, auth_headers, "Project A")
    project_b = _create_project(client, auth_headers, "Project B")
    user_scope = str(test_user.supabase_user_id)

    register = lambda project_id, media_id: client.post(
        f"/api/v1/projects/{project_id}/assets/register",
        headers=auth_headers,
        json={
            "kind": "image",
            "storage_path": f"editor/assets/{user_scope}/{project_id}/{uuid4()}/{media_id}.png",
            "filename": f"{media_id}.png",
            "metadata": {"elevo_editor_media_id": media_id},
        },
    )

    assert register(project_a["id"], "asset-a").status_code == 201
    assert register(project_b["id"], "asset-b").status_code == 201

    scoped = client.get(
        f"/api/v1/projects/{project_a['id']}/assets?project_only=true",
        headers=auth_headers,
    )
    assert scoped.status_code == 200, scoped.text
    payload = scoped.json()
    assert payload["total"] == 1
    assert payload["items"][0]["metadata"]["project_id"] == project_a["id"]


def test_create_signed_upload_url_for_project_asset(client, auth_headers, test_user):
    project = _create_project(client, auth_headers, "Signed URL project")
    user_scope = str(test_user.supabase_user_id)

    class StubStorage:
        def create_signed_upload_url(self, storage_path, *, content_type=None, upsert=False):
            return {
                "bucket": "videos",
                "storage_path": storage_path,
                "signed_url": f"https://example.test/upload/{storage_path}?token=signed",
                "token": "signed",
                "content_type": content_type or "application/octet-stream",
                "expires_in": 600,
            }

    original_storage = projects_endpoint.storage
    original_backend = settings.STORAGE_BACKEND
    try:
        projects_endpoint.storage = StubStorage()
        settings.STORAGE_BACKEND = "supabase"
        signed_upload_rate_limiter.reset()
        response = client.post(
            f"/api/v1/projects/{project['id']}/assets/signed-upload-url",
            headers=auth_headers,
            json={
                "kind": "video",
                "filename": "clip.mp4",
                "content_type": "video/mp4",
                "asset_id": "asset_1",
            },
        )
    finally:
        projects_endpoint.storage = original_storage
        settings.STORAGE_BACKEND = original_backend

    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["bucket"] == "videos"
    assert payload["storage_path"].startswith(
        f"editor/assets/{user_scope}/{project['id']}/asset_1/"
    )
    assert payload["signed_url"].startswith("https://example.test/upload/")


def test_create_signed_upload_url_rate_limited(client, auth_headers):
    project = _create_project(client, auth_headers, "Rate limited signed URL project")

    class StubStorage:
        def create_signed_upload_url(self, storage_path, *, content_type=None, upsert=False):
            return {
                "bucket": "videos",
                "storage_path": storage_path,
                "signed_url": f"https://example.test/upload/{storage_path}?token=signed",
                "token": "signed",
                "content_type": content_type or "application/octet-stream",
                "expires_in": 600,
            }

    original_storage = projects_endpoint.storage
    original_backend = settings.STORAGE_BACKEND
    original_limit = settings.EDITOR_SIGNED_UPLOAD_RATE_LIMIT
    original_window = settings.EDITOR_SIGNED_UPLOAD_RATE_WINDOW_SEC
    try:
        projects_endpoint.storage = StubStorage()
        settings.STORAGE_BACKEND = "supabase"
        settings.EDITOR_SIGNED_UPLOAD_RATE_LIMIT = 1
        settings.EDITOR_SIGNED_UPLOAD_RATE_WINDOW_SEC = 60
        signed_upload_rate_limiter.reset()

        first = client.post(
            f"/api/v1/projects/{project['id']}/assets/signed-upload-url",
            headers=auth_headers,
            json={"kind": "image", "filename": "poster.png", "content_type": "image/png"},
        )
        second = client.post(
            f"/api/v1/projects/{project['id']}/assets/signed-upload-url",
            headers=auth_headers,
            json={"kind": "image", "filename": "poster-2.png", "content_type": "image/png"},
        )
    finally:
        projects_endpoint.storage = original_storage
        settings.STORAGE_BACKEND = original_backend
        settings.EDITOR_SIGNED_UPLOAD_RATE_LIMIT = original_limit
        settings.EDITOR_SIGNED_UPLOAD_RATE_WINDOW_SEC = original_window

    assert first.status_code == 201, first.text
    assert second.status_code == 429, second.text
    assert "retry-after" in {key.lower() for key in second.headers.keys()}
