# TTS run results

Verified: October 6, 2026.

Current project: `G:\1MDC_Education\CAI3303C_NaturalLang\01_Assignments\TTS`.

- The relocated `.venv` loads Flask, Flask-CORS, Torch, SoundFile, and the relocated editable F5-TTS source.
- Installed Python launchers were regenerated for the new location; `pip --version` resolves to this environment.
- All three PowerShell scripts pass syntax validation.
- The root `imv_api.py` was started from a temporary directory outside TTS to verify that its data paths do not depend on the terminal's working directory.
- `/health` returned HTTP 200 with `{"model":"F5TTS_v1_Base","status":"running"}`.
- Invalid JSON array and null bodies returned HTTP 400.
- `Test-TTS.ps1` was invoked from outside TTS. It compiled both Java clients, ran `TTSClient`, called the live API, and saved fresh audio successfully.
- Test duration, including Java compilation: 94.8 seconds on CPU.
- Output: `gen_audio/output.wav`, 223,788 bytes, mono, 24,000 Hz, 4.661 seconds. SoundFile decoded it successfully and confirmed a nonzero signal. Listening quality was not assessed.
- The verification server was stopped after the test. Start it with `Start-TTS.ps1` for your next run.

The September output is preserved as `gen_audio/previous_output_20260913.wav`.
Machine-readable verification is in `data/latest_verification.json`.

Custom voice upload and browser interactions were not tested end-to-end in this run. The browser's API field now defaults to `http://localhost:5000` when opened locally.


## GitHub and browser demo verification — October 6, 2026

- Added a browser demo served by the same API at `/`, `/demo`, and `/demo/`. The voice studio is at `/studio`.
- Five automated API tests passed: known/unknown FAQ behavior, validation, Spanish answer selection, empty/unsupported uploads, and generation locking/error recovery.
- All installed dependency requirements passed `pip check`.
- The saved WAV compatibility patch applied successfully to a clean checkout of the pinned upstream F5-TTS commit. That commit was confirmed accessible on GitHub.
- In the in-app browser, a typed known question displayed the correct FAQ answer and browser voice playback completed; an unknown question displayed the fallback.
- A recorded WAV upload passed through the HTTP Whisper endpoint and produced the expected English transcription, with a 3.907-second transcription/answer total on the first request. The browser file chooser and upload submission were also exercised.
- The updated `/tts` endpoint generated a new valid mono WAV for "Hello Sky." in 52.8 seconds: 45,100 bytes, 24,000 Hz, and 0.939 seconds.
- Live microphone recording was not exercised. Microphone access remains dependent on the user's browser and input device.
- Codespaces configuration and cross-platform setup are included, but no cloud container or paid service was started or tested.
- Runtime data, environment files, personal reference recordings, generated audio, and the older archive are excluded from GitHub.
