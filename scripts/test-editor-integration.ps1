$ErrorActionPreference = 'Stop'

Write-Host '[editor-integration] Running unified verify harness...'
& "$PSScriptRoot/verify-editor.ps1"
