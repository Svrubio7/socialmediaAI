param(
  [switch]$Detached
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if ($Detached) {
  docker compose up -d --build
  exit $LASTEXITCODE
}

docker compose up --build
exit $LASTEXITCODE
