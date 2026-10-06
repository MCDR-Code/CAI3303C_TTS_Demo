$ErrorActionPreference = 'Stop'
$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (!(Test-Path -LiteralPath $pythonPath)) {
    throw 'Run Setup-TTS.ps1 first to create the development environment.'
}
Push-Location $PSScriptRoot
try {
    Write-Host 'Starting TTS. Leave this window open; Ctrl+C stops the server.'
    Write-Host 'Open http://localhost:5000 for the Sky browser demo.'
    Write-Host 'The Java assignment check is available with .\Test-TTS.ps1 in another window.'
    & $pythonPath (Join-Path $PSScriptRoot 'imv_api.py')
    if ($LASTEXITCODE -ne 0) { throw 'The TTS server stopped with an error.' }
} finally {
    Pop-Location
}
