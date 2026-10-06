param(
    [string]$Text,
    [string]$Audio,
    [switch]$NoTts,
    [double]$Seconds = 5,
    [string]$Voice = 'default'
)
$ErrorActionPreference = 'Stop'
$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (!(Test-Path -LiteralPath $pythonPath)) { throw 'Run Setup-TTS.ps1 first.' }
$demoArgs = @((Join-Path $PSScriptRoot 'demo\sky_voice_demo.py'), '--seconds', "$Seconds", '--voice', $Voice)
if ($Text) { $demoArgs += @('--text', $Text) }
if ($Audio) { $demoArgs += @('--audio', $Audio) }
if ($NoTts) { $demoArgs += '--no-tts' }
if (!$Text) {
    & $pythonPath -c "import whisper, sounddevice"
    if ($LASTEXITCODE -ne 0) { throw 'Voice-input dependencies are missing. Run .\demo\Setup-Demo.ps1 once.' }
}
if (!$NoTts) {
    try { Invoke-RestMethod 'http://localhost:5000/health' -TimeoutSec 5 | Out-Null }
    catch { throw 'Start Start-TTS.ps1 in another terminal before running the voice demo.' }
}
& $pythonPath @demoArgs
if ($LASTEXITCODE -ne 0) { throw 'The Sky demo failed. See the message above.' }
