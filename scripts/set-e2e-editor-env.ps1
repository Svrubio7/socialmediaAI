param(
  [switch]$Persist
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"

Push-Location $backendDir
try {
$json = @'
import json
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.security import create_access_token

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    user = conn.execute(text("""
        select u.id as user_id
        from public.users u
        where u.is_active = true
        order by coalesce(u.last_login, u.updated_at, u.created_at) desc
        limit 1
    """)).mappings().first()

    if user is None:
        raise SystemExit("No active users found in database")

    user_id = str(user["user_id"])

    opencut_project = conn.execute(text("""
        select p.id as project_id
        from public.projects p
        where p.user_id = :user_id and coalesce(p.editor_engine, 'legacy') = 'opencut'
        order by p.updated_at desc
        limit 1
    """), {"user_id": user["user_id"]}).mappings().first()

    legacy_project = conn.execute(text("""
        select p.id as project_id
        from public.projects p
        where p.user_id = :user_id and coalesce(p.editor_engine, 'legacy') = 'legacy'
        order by p.updated_at desc
        limit 1
    """), {"user_id": user["user_id"]}).mappings().first()

token = create_access_token(subject=user_id)

print(json.dumps({
    "legacy_project_id": str(legacy_project["project_id"]) if legacy_project else None,
    "opencut_project_id": str(opencut_project["project_id"]) if opencut_project else None,
    "user_id": user_id,
    "token": token
}))
'@ | py -3 -
}
finally {
  Pop-Location
}

$data = $json | ConvertFrom-Json

# Current shell
$env:E2E_EDITOR_PROJECT_ID = $data.opencut_project_id
$env:E2E_EDITOR_PROJECT_ID_LEGACY = $data.legacy_project_id
$env:E2E_API_BEARER_TOKEN = $data.token
$env:E2E_API_BASE_URL = "http://127.0.0.1:8000/api/v1"
$env:E2E_BASE_URL = "http://127.0.0.1:3000"

if ($Persist) {
  # Future shells
  setx E2E_EDITOR_PROJECT_ID $data.opencut_project_id | Out-Null
  setx E2E_EDITOR_PROJECT_ID_LEGACY $data.legacy_project_id | Out-Null
  setx E2E_API_BEARER_TOKEN $data.token | Out-Null
  setx E2E_API_BASE_URL "http://127.0.0.1:8000/api/v1" | Out-Null
  setx E2E_BASE_URL "http://127.0.0.1:3000" | Out-Null
}

Write-Output "E2E vars set."
Write-Output "E2E_EDITOR_PROJECT_ID=$($data.opencut_project_id)"
Write-Output "E2E_EDITOR_PROJECT_ID_LEGACY=$($data.legacy_project_id)"
Write-Output "E2E_API_BEARER_TOKEN=(length=$($data.token.Length))"
Write-Output "E2E_API_BASE_URL=$($env:E2E_API_BASE_URL)"
Write-Output "E2E_BASE_URL=$($env:E2E_BASE_URL)"
Write-Output "TOKEN_SUBJECT_USER_ID=$($data.user_id)"
if ($Persist) {
  Write-Output "Persisted with setx for future terminals."
}
