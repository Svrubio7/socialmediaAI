param(
  [string]$BaseUrl = "http://127.0.0.1:3000"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$env:VERIFY_APP_BASE_URL = $BaseUrl
node ./scripts/verify-app.mjs
exit $LASTEXITCODE
