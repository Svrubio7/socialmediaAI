from uuid import uuid4


def _create_project(client, auth_headers, name: str = "Test Project"):
    response = client.post(
        "/api/v1/projects",
        headers=auth_headers,
        json={"name": name},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_project_includes_schema_and_revision(client, auth_headers):
    payload = _create_project(client, auth_headers)
    assert payload["schema_version"] == 2
    assert payload["revision"] == 0
    assert payload["state"]["version"] == 2
    assert "scenes" in payload["state"]
    assert "tracks" in payload["state"]


def test_update_project_increments_revision(client, auth_headers):
    project = _create_project(client, auth_headers)
    project_id = project["id"]

    update = client.patch(
        f"/api/v1/projects/{project_id}",
        headers=auth_headers,
        json={
            "name": "Renamed",
            "revision": project["revision"],
            "schema_version": project["schema_version"],
        },
    )
    assert update.status_code == 200, update.text
    updated_payload = update.json()
    assert updated_payload["name"] == "Renamed"
    assert updated_payload["revision"] == project["revision"] + 1


def test_update_project_revision_conflict_returns_409(client, auth_headers):
    project = _create_project(client, auth_headers)
    project_id = project["id"]

    # First successful update moves revision to 1.
    first_update = client.patch(
        f"/api/v1/projects/{project_id}",
        headers=auth_headers,
        json={"name": "First", "revision": project["revision"], "schema_version": 2},
    )
    assert first_update.status_code == 200, first_update.text

    # Retry with stale revision value should fail.
    stale_update = client.patch(
        f"/api/v1/projects/{project_id}",
        headers=auth_headers,
        json={"name": "Second", "revision": project["revision"], "schema_version": 2},
    )
    assert stale_update.status_code == 409, stale_update.text
    detail = stale_update.json()["detail"]
    assert detail["code"] == "revision_conflict"
    assert detail["server_revision"] == 1


def test_register_project_video_asset(client, auth_headers, test_user):
    project = _create_project(client, auth_headers)
    project_id = project["id"]
    user_scope = str(test_user.supabase_user_id)
    storage_path = f"videos/{user_scope}/{uuid4()}.mp4"
    response = client.post(
        f"/api/v1/projects/{project_id}/assets/register",
        headers=auth_headers,
        json={
            "kind": "video",
            "storage_path": storage_path,
            "filename": "Clip",
            "metadata": {"source": "test"},
        },
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["kind"] == "video"
    assert payload["storage_path"] == storage_path
    assert payload["metadata"]["source"] == "test"


def test_export_job_lifecycle(client, auth_headers, monkeypatch):
    project = _create_project(client, auth_headers)
    project_id = project["id"]

    class _DummyTask:
        id = "celery-test-task"

    def _fake_delay(_job_id):
        return _DummyTask()

    monkeypatch.setattr(
        "app.workers.video_tasks.render_project_export_job.delay",
        _fake_delay,
    )

    create_response = client.post(
        f"/api/v1/projects/{project_id}/exports",
        headers=auth_headers,
        json={"format": "mp4", "include_audio": True},
    )
    assert create_response.status_code == 202, create_response.text
    job = create_response.json()
    assert job["status"] == "queued"
    assert job["job_id"]

    get_response = client.get(
        f"/api/v1/projects/{project_id}/exports/{job['job_id']}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200, get_response.text
    fetched = get_response.json()
    assert fetched["job_id"] == job["job_id"]
    assert fetched["status"] == "queued"

    shared_job_response = client.get(
        f"/api/v1/editor/jobs/{job['job_id']}",
        headers=auth_headers,
    )
    assert shared_job_response.status_code == 200, shared_job_response.text
    shared_job = shared_job_response.json()
    assert shared_job["job_id"] == job["job_id"]
    assert shared_job["job_type"] == "export"

    cancel_response = client.post(
        f"/api/v1/projects/{project_id}/exports/{job['job_id']}/cancel",
        headers=auth_headers,
    )
    assert cancel_response.status_code == 200, cancel_response.text
    canceled = cancel_response.json()
    assert canceled["status"] == "canceled"
    assert canceled["cancel_requested"] is True
