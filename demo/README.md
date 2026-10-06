# Sky voice demo

This demo is now part of the TTS project. It shares the Python environment at `../.venv` and the backend started by `../Start-TTS.ps1`.

Flow: microphone or recording -> Whisper speech-to-text -> FAQ match -> F5-TTS -> speaker.

## Run from the TTS folder

For a quick text-only check (no microphone or backend needed):

```powershell
.\Start-Demo.ps1 -Text "What is Sky?" -NoTts
```

For a typed question with a spoken answer:

1. Run `.\Start-TTS.ps1` and leave that terminal open.
2. In another terminal in the TTS folder, run `.\Start-Demo.ps1 -Text "What is Sky?"`.

For microphone input, first run the one-time setup:

```powershell
.\demo\Setup-Demo.ps1
```

This installs the demo's extra packages into the shared `.venv` and downloads the Whisper base model. Then start the TTS backend and run:

```powershell
.\Start-Demo.ps1
```

Other examples:

```powershell
.\Start-Demo.ps1 -Seconds 7
.\Start-Demo.ps1 -Audio "C:\path\question.wav"
.\Start-Demo.ps1 -NoTts
```

The demo saves spoken answers in `demo/gen_audio/sky_answer.wav` and plays them on Windows. CPU speech generation can take several minutes for a longer answer.

## Files and behavior

- `sky_voice_demo.py`: records or loads audio, transcribes it, selects an answer, generates speech, and plays it.
- `faq.json`: six FAQ topics, question variations, and English/Spanish answers.
- `requirements.txt`: demo dependencies, installed into the parent TTS environment.
- `Setup-Demo.ps1`: installs dependencies and downloads the Whisper base model.

FAQ lookup uses TF-IDF and cosine similarity with a 0.5 threshold. Unmatched questions receive a fallback message. The fallback mentions connecting to a person, but this prototype does not perform a real handoff. Typed questions are treated as English; spoken Spanish can select Spanish answers. Spanish speech quality needs evaluation with this TTS model.

## Verification — October 6, 2026

The shared environment now includes all demo packages, including Whisper and sounddevice, and the Whisper base model has been downloaded. Whisper successfully transcribed `../gen_audio/output.wav` as "Good morning team, having fun testing the API." The launcher was also checked with recorded audio and speech output disabled. No default microphone was available to the verification process; live microphone recognition and speaker playback remain unverified. `Setup-TTS.ps1` now includes the demo setup for a fresh installation.

The previous setup instructions are preserved in `../older/Sky_Demo_README_previous.md`.
