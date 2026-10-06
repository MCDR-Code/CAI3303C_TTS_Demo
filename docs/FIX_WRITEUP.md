# F5-TTS Assignment — What Was Broken, and How It Was Fixed

Course: CAI3303C Natural Language Processing — Week04 F5-TTS/API/Deployment assignment
Original code: instructor-provided, dated Jan 2025 (see `../older/original/`)

## Background

The instructor confirmed the original `imv_api.py` + Java client project stopped
working because the F5-TTS library's API changed after the code was written, and
development on the assignment itself was discontinued. This document explains
exactly what changed, how that was confirmed, and what was fixed.

## Investigation process

1. Read the original `imv_api.py`, `AddVoiceClient.java`, and `TTSCLIENT.java` to
   understand the intended architecture: a Flask API wraps F5-TTS's command-line
   tool (`f5-tts_infer-cli`) via `subprocess`, and two small Java programs call
   that API over HTTP (`/add_voice` to register a reference voice, `/tts` to
   generate speech).
2. Cloned the current F5-TTS repository (`github.com/SWivid/F5-TTS`) with full
   git history to compare today's CLI against what existed when the assignment
   was written.
3. Located the exact commit that changed the CLI's behavior, using `git log -S`
   to search history for the specific code that changed.

## Root cause #1: the `--model` argument's accepted values changed

`imv_api.py` invokes the CLI with `--model F5-TTS` (the literal string "F5-TTS",
taken from `DEFAULT_MODEL_PATH = os.getenv('TTS_MODEL_PATH', 'F5-TTS')`).

As of January 2025 — around when this assignment was written — F5-TTS's
`infer_cli.py` genuinely accepted that:

```python
model = args.model or config.get("model", "F5-TTS")
...
if model == "F5-TTS":
    ...
elif model == "E2-TTS":
    ...
```

Commit `ca6e49a`, **"1.0.0 F5-TTS v1 base model with better training and
inference performance"** (2025-03-12), refactored this into a config-file
registry:

```python
model_cfg = OmegaConf.load(f"configs/{model}.yaml")
```

`--model` must now be an exact filename under `src/f5_tts/configs/`. Today's
valid values are: `F5TTS_v1_Base`, `F5TTS_Base`, `F5TTS_Small`,
`F5TTS_v1_Small`, `E2TTS_Base`, `E2TTS_Small`. There is no `F5-TTS.yaml`, so
every call the old code made failed with `FileNotFoundError` before any audio
was ever generated. This is a clean, dated, verifiable breaking change — and
matches the instructor's account of the project breaking "along the way."

**Fix:** default changed to `F5TTS_v1_Base` (the current recommended model,
introduced by that same March 2025 release). Still overridable via the
`TTS_MODEL_PATH` environment variable.

## Root cause #2: the default voice's reference audio was never valid

Independent of the F5-TTS API change, the original code seeded a "default"
voice profile on first run like this:

```python
with open(default_audio_path, 'wb') as f:
    f.write(b'')  # Create an empty file
```

A zero-byte file is not a valid WAV file. Even with root cause #1 fixed, any
`/tts` call against the "default" voice (which is exactly what the provided
`TTSCLIENT.java` does with no setup) would fail trying to load that empty
file as audio.

**Fix:** the default voice now points at the short reference clip F5-TTS ships
inside its own installed package
(`infer/examples/basic/basic_ref_en.wav`), using the same path-resolution
logic F5-TTS's own CLI already uses for that file — no bundled audio asset of
our own is needed, and the reference text was corrected to match that clip's
actual transcript ("Some call me nature, others call me mother nature.")
instead of the placeholder fox/dog sentence that didn't match any real audio.

## Other changes made while fixing

- **CORS enabled** (`flask-cors`) so a browser-based front end served from a
  different origin/port can call the API directly.
- **`GET /voices`** endpoint added so a front end can list available voices
  instead of guessing usernames.
- **CLI failures are now debuggable** — `subprocess.run` captures stdout/stderr
  and returns them in the JSON error response, instead of only the bare exit
  code.
- **Reference-audio existence check** before invoking the CLI, so a missing
  uploaded file fails with a clear message rather than an opaque CLI crash.

## A minor bug not related to the API break

`TTSCLIENT.java` (the file name) contains `public class TTSClient` — different
capitalization. A compilation test on this Windows computer on October 6,
2026 failed with "class TTSClient is public, should be declared in a file
named TTSClient.java". The active file is now named `../TTSClient.java`;
the original is preserved in `../older/TTSCLIENT.java`.

## Can this be used from a mobile phone / as a mobile app?

Yes, with an important distinction:

- The Flask API is already a plain REST service bound to `0.0.0.0`, so **any**
  client that can reach your computer's IP address on the network can call it
  — a native app, a mobile browser, anything that speaks HTTP.
- The fastest path to a phone demo (used here) is a **mobile-responsive web
  front end** (`../frontend/index.html`). Run the API on a laptop, find that
  laptop's LAN IP, open the front end on a phone browser on the same Wi-Fi,
  and point it at `http://<laptop-ip>:5000`. This needs zero app-store
  distribution and works for an in-class demo today.
- For something closer to an installable app without writing native code, the
  front end can be "Added to Home Screen" from iOS Safari or Android Chrome,
  which gives a full-screen, icon-launched experience (a lightweight PWA) —
  already wired up with the relevant meta tags.
- A true native app (Swift/Kotlin) or cross-platform app (React Native/
  Flutter) is also possible later since it's just calling the same three
  endpoints (`/add_voice`, `/tts`, `/voices`) — but isn't necessary for the
  in-class demo goal stated for this assignment.

## Windows audio compatibility and current setup

The September run required a local WAV-loading fix: `infer_cli.py` and
`utils_infer.py` use `soundfile` for reference WAV loading instead of the
TorchCodec-dependent `torchaudio.load` path. That modified source is preserved
in `../F5-TTS/`.

On October 6, 2026 the repaired backend generated a valid WAV on the CPU.
The project was then consolidated into the assignment's TTS folder, including
the `.venv` environment, and its installed launchers and editable source path
were regenerated for the new location. The active API invokes inference with
its own Python interpreter and uses absolute data paths based on its file
location. Invalid JSON payloads now return 400, and upload usernames are
restricted to letters, numbers, underscores, and hyphens.

Use `../README.md` for run instructions and `../RUN_RESULTS.md` for the latest
Java-to-API verification. Custom voice uploads and the browser UI have not
been exercised end-to-end in the October review.
