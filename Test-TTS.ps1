$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $health = Invoke-RestMethod 'http://localhost:5000/health' -TimeoutSec 5
    if ($health.model -ne 'F5TTS_v1_Base') { throw 'The expected repaired TTS API is not running on port 5000.' }
    New-Item -ItemType Directory -Path '.build' -Force | Out-Null
    & javac -d '.build' 'TTSClient.java' 'AddVoiceClient.java'
    if ($LASTEXITCODE -ne 0) { throw 'Java compilation failed.' }
    $startedAt = Get-Date
    Write-Host 'Generating speech. CPU generation can take a few minutes.'
    & java -cp '.build' TTSClient
    $audioPath = Join-Path $PSScriptRoot 'gen_audio\output.wav'
    if (!(Test-Path -LiteralPath $audioPath)) { throw 'No audio file was generated. Check the API window.' }
    $audio = Get-Item -LiteralPath $audioPath
    if ($audio.LastWriteTime -lt $startedAt -or $audio.Length -le 44) { throw 'No new usable audio was generated. Check the API window.' }
    Write-Host "Ready to play: $audioPath"
} finally {
    Pop-Location
}
