from app.core.config import settings


def _create_project(client, auth_headers, **payload):
    response = client.post("/api/v1/projects", headers=auth_headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_elevo_editor_project_round_trip_preserves_raw_state(client, auth_headers):
    previous_enabled = settings.EDITOR_ELEVO_ENABLED
    settings.EDITOR_ELEVO_ENABLED = True
    try:
        project = _create_project(
            client,
            auth_headers,
            name="Elevo Editor Test",
            editor_engine="elevo-editor",
        )

        assert project["editor_engine"] == "elevo-editor"
        assert project["schema_version"] == 6

        raw_state = {
            "version": 42,
            "metadata": {
                "id": project["id"],
                "name": "Elevo Editor Test",
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
                "editor_engine": "elevo-editor",
                "schema_version": 42,
                "state": raw_state,
            },
        )
        assert updated.status_code == 200, updated.text

        payload = updated.json()
        assert payload["editor_engine"] == "elevo-editor"
        assert payload["schema_version"] == 42
        assert payload["state"]["version"] == 42
        assert payload["state"]["custom"] == {"keep": ["this", "as-is"]}
    finally:
        settings.EDITOR_ELEVO_ENABLED = previous_enabled


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
    previous_enabled = settings.EDITOR_ELEVO_ENABLED
    settings.EDITOR_ELEVO_ENABLED = True
    try:
        _create_project(client, auth_headers, name="Legacy A")
        _create_project(client, auth_headers, name="Elevo Editor A", editor_engine="elevo-editor")

        legacy = client.get("/api/v1/projects?editor_engine=legacy", headers=auth_headers)
        assert legacy.status_code == 200, legacy.text
        assert all(item["editor_engine"] == "legacy" for item in legacy.json()["items"])

        elevo_editor = client.get("/api/v1/projects?editor_engine=elevo-editor", headers=auth_headers)
        assert elevo_editor.status_code == 200, elevo_editor.text
        assert all(item["editor_engine"] == "elevo-editor" for item in elevo_editor.json()["items"])
    finally:
        settings.EDITOR_ELEVO_ENABLED = previous_enabled


def test_elevo_editor_disabled_rejects_new_elevo_editor_projects(client, auth_headers):
    previous_enabled = settings.EDITOR_ELEVO_ENABLED
    settings.EDITOR_ELEVO_ENABLED = False
    try:
        response = client.post(
            "/api/v1/projects",
            headers=auth_headers,
            json={"name": "Elevo Editor Disabled", "editor_engine": "elevo-editor"},
        )
        assert response.status_code == 409
    finally:
        settings.EDITOR_ELEVO_ENABLED = previous_enabled
