$ErrorActionPreference = 'Stop'
$ttsRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $ttsRoot '.venv\Scripts\python.exe'
if (!(Test-Path -LiteralPath $pythonPath)) { throw 'Run the TTS folder''s Setup-TTS.ps1 first.' }
& $pythonPath -m pip install -r (Join-Path $PSScriptRoot 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Demo dependency installation failed.' }
& $pythonPath -c "import whisper; whisper.load_model('base')"
if ($LASTEXITCODE -ne 0) { throw 'Whisper model download failed.' }
Write-Host 'Sky demo setup complete. Use Start-Demo.ps1 in the TTS folder.'
