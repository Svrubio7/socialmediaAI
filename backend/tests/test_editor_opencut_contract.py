from app.core.config import settings


def _create_project(client, auth_headers, **payload):
    response = client.post("/api/v1/projects", headers=auth_headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_opencut_project_round_trip_preserves_raw_state(client, auth_headers):
    previous_enabled = settings.EDITOR_OPENCUT_ENABLED
    settings.EDITOR_OPENCUT_ENABLED = True
    try:
        project = _create_project(
            client,
            auth_headers,
            name="OpenCut Test",
            editor_engine="opencut",
        )

        assert project["editor_engine"] == "opencut"
        assert project["schema_version"] == 6

        raw_state = {
            "version": 42,
            "metadata": {
                "id": project["id"],
                "name": "OpenCut Test",
                "duration": 9.5,
                "createdAt": "2026-01-01T00:00:00Z",
                "updatedAt": "2026-01-01T00:00:00Z",
            },
            "scenes": [],
            "currentSceneId": "scene_main",
            "settings": {
                "fps": 30,
                "canvasSize": {"width": 1080, "height": 1920},
                "background": {"type": "color", "color": "#000000"},
            },
            "timelineViewState": {"zoomLevel": 1, "scrollLeft": 0, "playheadTime": 0},
            "custom": {"keep": ["this", "as-is"]},
        }

        updated = client.patch(
            f"/api/v1/projects/{project['id']}",
            headers=auth_headers,
            json={
                "revision": project["revision"],
                "editor_engine": "opencut",
                "schema_version": 42,
                "state": raw_state,
            },
        )
        assert updated.status_code == 200, updated.text

        payload = updated.json()
        assert payload["editor_engine"] == "opencut"
        assert payload["schema_version"] == 42
        assert payload["state"]["version"] == 42
        assert payload["state"]["custom"] == {"keep": ["this", "as-is"]}
    finally:
        settings.EDITOR_OPENCUT_ENABLED = previous_enabled


def test_legacy_project_rejects_newer_schema(client, auth_headers):
    project = _create_project(client, auth_headers, name="Legacy")

    response = client.patch(
        f"/api/v1/projects/{project['id']}",
        headers=auth_headers,
        json={
            "revision": project["revision"],
            "schema_version": 999,
        },
    )

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "version_unsupported"


def test_list_projects_filters_by_editor_engine(client, auth_headers):
    previous_enabled = settings.EDITOR_OPENCUT_ENABLED
    settings.EDITOR_OPENCUT_ENABLED = True
    try:
        _create_project(client, auth_headers, name="Legacy A")
        _create_project(client, auth_headers, name="OpenCut A", editor_engine="opencut")

        legacy = client.get("/api/v1/projects?editor_engine=legacy", headers=auth_headers)
        assert legacy.status_code == 200, legacy.text
        assert all(item["editor_engine"] == "legacy" for item in legacy.json()["items"])

        opencut = client.get("/api/v1/projects?editor_engine=opencut", headers=auth_headers)
        assert opencut.status_code == 200, opencut.text
        assert all(item["editor_engine"] == "opencut" for item in opencut.json()["items"])
    finally:
        settings.EDITOR_OPENCUT_ENABLED = previous_enabled


def test_opencut_disabled_rejects_new_opencut_projects(client, auth_headers):
    previous_enabled = settings.EDITOR_OPENCUT_ENABLED
    settings.EDITOR_OPENCUT_ENABLED = False
    try:
        response = client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={"name": "OpenCut Disabled", "editor_engine": "opencut"},
        )
        assert response.status_code == 409
    finally:
        settings.EDITOR_OPENCUT_ENABLED = previous_enabled
