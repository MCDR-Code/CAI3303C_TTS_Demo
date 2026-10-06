# LLM Prompt Log — Week04 F5-TTS/API/Deployment Assignment

Current project location: `G:\1MDC_Education\CAI3303C_NaturalLang\01_Assignments\TTS`.
The September sessions below are historical; use `README.md` for current run instructions.

Per the assignment instructions: "Submit your prompt history and a synopsis
of what you learned and whether or not it can assist you in completing your
project." This file is that running log — one dated entry per session.

---

## Session 0 — 2026-09-01 (initial diagnosis, fix, and scoping)

**Context:** First session working on this assignment. Provided Claude with
the instructor's original code (`imv_api.py`, `AddVoiceClient.java`,
`TTSCLIENT.java`) and the instructor's explanation that the project stopped
working because F5-TTS's API changed and development was discontinued.

**What was asked, roughly in order:**
1. Organize the Canvas course folder structure and pull down all class
   materials (slides, labs, resources) for the semester.
2. Diagnose exactly why the F5-TTS assignment code was broken, fix it, and
   build a working API + front end — while preserving the original code
   for comparison — and document the process for grading.
3. Discuss whether/how this could run on a phone for an in-class demo.
4. Scope discussion: distinguish this low-stakes Week04 exercise from the
   semester presentation (subject: TTS/STT) and the semester project (the
   full implementation) — agreed the Week04 deliverable should stay a
   simple CLI, matching the assignment's actual instructions, while the
   more built-out API + web/mobile front end becomes the semester project.

**What Claude found/did:**
- Cloned the current F5-TTS repository and used `git log -S` to locate the
  exact commit (`ca6e49a`, 2025-03-12) that changed how `--model` is
  specified — the root cause of the original code's failure (it passed the
  literal string `"F5-TTS"`, which stopped being a valid model name).
- Found a second, independent bug: the code's "default" voice pointed at a
  reference audio file that was created as an empty (0-byte) file, so it
  could never have worked even before the API change.
- Wrote a fixed `imv_api.py` (current model name, CORS enabled, a `/voices`
  listing endpoint, captured CLI error output, existence checks) — kept in
  `03_Development_Environment/source_code/F5-TTS_Week04/fixed_api/`, with
  the untouched original preserved in `.../original/` for comparison.
- Built a custom mobile-responsive web front end (`frontend/index.html`) as
  an alternative to the Java clients, intended for the semester project
  rather than this assignment.
- Wrote `docs/FIX_WRITEUP.md` (technical explanation of both bugs and the
  fixes) and `docs/HOW_IT_WORKS.md` (plain-language explanation for the
  in-class presentation).
- Corrected course mid-session after starting to build a Python virtual
  environment inside the wrong (Linux sandbox) shell — deleted that
  attempt once caught, since it would not have run on Windows.

**Synopsis so far:** the LLM was useful for the parts that would otherwise
have taken real time to track down by hand — specifically, pinpointing the
exact commit/date F5-TTS's model-naming convention changed (rather than
just guessing), and catching a second latent bug (the empty reference
audio file) that wasn't mentioned by the instructor and wouldn't have been
obvious without reading the original code closely. It has not yet been
useful for the part that matters most for grading purposes — actually
running the fix end-to-end — since that has to happen in a real Python
environment on my own machine, which is still pending.

---

## Session 1 — 2026-09-13

**Prompt:** "Look in my Week04 folders. Then check in
`G:\1MDC_Education\CAI3303C_NaturalLang\03_Development_Environment\source_code`
and tell me what I am missing to complete the assignment. Create a
`missing.md` document in Week04 assignments."

**Response summary:** Codex compared the Week04 assignment folder against
the F5-TTS source-code folder. It found that the slides, instructions,
original Java/API files, fixed API files, F5-TTS source, setup notes, and
writeups were present. The missing work was the actual local run: creating
the virtual environment, installing dependencies, copying the fixed API into
the F5-TTS folder, running the API, compiling/running Java, generating audio,
and finishing the prompt log/synopsis. Codex created `missing.md` with that
checklist.

---

## Session 2 — 2026-09-13

**Prompt:** "Ok, complete the assignment."

**Response summary:** Codex created a Week04 Python virtual environment,
installed F5-TTS and the API dependencies, copied the fixed `imv_api.py`
into the F5-TTS folder, started the Flask API, confirmed `/health`, compiled
and ran the Java text-to-speech client, and generated audio successfully.
Two local problems had to be fixed during the run:

1. `pip` and Hugging Face downloads initially failed SSL certificate checks.
   `pip` was run with trusted PyPI hosts, and `python-certifi-win32` was
   installed so Python could use the Windows certificate store for Hugging
   Face downloads.
2. F5-TTS failed on Windows while loading the reference WAV through
   TorchCodec. Codex patched the local Week04 F5-TTS source so the command
   line path reads WAV files with `soundfile` instead of `torchaudio.load`.

The final Java client output was:

```text
Audio file saved successfully to ./gen_audio/test_output.wav
```

Generated audio was saved in:

```text
gen_audio\test_output.wav
gen_audio\output.wav
```

---

## Final synopsis

This exercise showed that local AI/audio projects often require more than
just copying code: the Python environment, Java compiler, ffmpeg, model
downloads, network certificates, and package compatibility all have to work
together. The original assignment code also broke because F5-TTS changed its
model naming after the assignment was written, and the original default
voice used an invalid empty reference audio file.

The LLM helped by tracing the breakage, organizing the assignment files,
creating a fixed API, documenting the setup, and completing the local run.
It also helped troubleshoot real environment problems during execution:
certificate verification, PATH access to the virtual environment, Java
compilation, and Windows audio-loading compatibility.

This can assist the larger course project because the same pattern applies:
set up a clean local environment, preserve original files, document each
change, test the API directly, test the client, and keep evidence of the
final working output.

---

## Session 3 — 2026-10-06 (review and consolidation)

**Prompts:** Review the TTS assignment folder and say whether it works or what it needs. Then consolidate everything under the actual TTS folder, create the development environment there, and move old material into `older`. Clarify which program to run.

**Response summary:** Codex found that the assignment still held the broken original API, the Java filename did not match its public class, the generated-audio folder was empty, and the completion notes referenced the previous Week04 location. The repaired backend in the development folder generated a valid WAV in a temporary review run.

Codex moved the F5-TTS source, Python environment, frontend, and documentation into this TTS folder. It placed superseded APIs, Java artifacts, and setup/completion notes in `older`; rebuilt the environment's installed launchers and editable source path; corrected the Java filename; and added a single README with setup, start, and test scripts. The API now resolves its data paths relative to its own file and invokes inference with its own environment's interpreter. Invalid JSON returns a client error instead of an internal error, and upload usernames are restricted to safe filename characters.

**Verification:** The consolidated API started successfully from outside the TTS folder. `Test-TTS.ps1` compiled both Java clients and generated `gen_audio/output.wav` through the live API. Generation and compilation took 94.8 seconds on CPU; the WAV decoded successfully as 4.661 seconds of mono audio at 24,000 Hz. The verification server was then stopped. Browser interactions and custom voice uploads were not tested end-to-end.

**What to run:** `Start-TTS.ps1` starts the backend; `Test-TTS.ps1` in a second terminal generates the test audio. `Setup-TTS.ps1` is for recreating dependencies when needed.

**What I learned:** Keeping the application, environment, launch scripts, outputs, and instructions together makes this project easier to understand and reproduce. Moving an environment also requires repairing its installed paths; moving only its folder is insufficient. A successful health check should be followed by an actual client-to-audio test.

## Session 4 — 2026-10-06 (Sky demo relocation)

**Prompt:** Move the Sky demo into the TTS folder under demo or a similar name.

**Response summary:** Moved all four demo files to `TTS/demo`, archived the previous demo README in `older`, updated the shared environment and backend instructions, and added `Start-Demo.ps1` plus `demo/Setup-Demo.ps1`. The former location now contains only a relocation notice. A directory lock prevented moving the enclosing folder, so its files were moved individually instead.

**Verification:** The root Start-Demo launcher successfully answered "What is Sky?" in text-only mode, with a similarity score of 1.00. Both new launch scripts passed PowerShell syntax checks. Whisper and sounddevice are not currently installed in the shared environment; the optional demo setup script installs them and downloads the base model. Microphone input, demo speech generation, and playback were not tested during this move.

## Session 5 — 2026-10-06 (complete missing demo dependencies)

**Prompt:** The demo failed because packages were missing.

**Response summary:** Installed openai-whisper, sounddevice, more-itertools, and tiktoken into TTS\.venv, and downloaded the Whisper base model. Updated Setup-TTS.ps1 to include the demo setup and added a clear error message when no usable default microphone is found.

**Verification:** All demo package imports passed. Start-Demo.ps1 with the existing gen_audio/output.wav and -NoTts successfully transcribed the recording, selected the expected unknown-question fallback, and completed in under one second of processing after model load. No default input device was available to the verification process; live microphone recognition and speaker playback were not tested.


## Session 6 — 2026-10-06 (repository and browser demo)

**Prompts:** Create a GitHub repository and prepare a demo; explain running it in the cloud. Use capital letters in the name, make it public for instructor access, and use the personal GitHub account MarielaCDelRio.

**Response summary:** Prepared CAI3303C_TTS_Demo with a browser interface for typed questions, audio uploads, and microphone recordings. Added Whisper transcription and FAQ endpoints, a fast browser-voice presentation option, and the actual F5-TTS model output option. Added API tests, GitHub Actions, a Codespaces devcontainer, shared cross-platform setup, upstream dependency attribution, a presentation guide, and a saved demo preview. Pinned F5-TTS as an upstream submodule and preserved the Windows compatibility patch as a setup-applied file. The local environment, downloaded models, archived material, recordings, and generated audio are excluded from the repository.

An empty repository was initially created in the currently authenticated gosharktech account. Once personal ownership was clarified, transfer of that empty repository to MarielaCDelRio was requested; no project files were uploaded to the company account.

**Verification:** Five API tests passed, pip check reported no broken requirements, the compatibility patch applied to clean upstream source, browser known/unknown question flows worked, browser voice playback completed, Whisper transcribed an uploaded recording, and the updated backend generated a valid F5-TTS WAV. Codespaces execution and live microphone recording have not been verified.
