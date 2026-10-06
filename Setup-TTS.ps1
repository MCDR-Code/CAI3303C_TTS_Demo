$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    & python 'scripts\setup_project.py'
    if ($LASTEXITCODE -ne 0) { throw 'Project setup failed. See the message above.' }
    Write-Host 'Setup complete. Run .\Start-TTS.ps1.'
} finally {
    Pop-Location
}
