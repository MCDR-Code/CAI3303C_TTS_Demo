# Classroom demo

## Before class

Start `Start-TTS.ps1` and open http://localhost:5000. Check that the connection indicator is ready. Keep a short recording of a FAQ question available if your microphone is unavailable. On a cloud computer use the forwarded HTTPS address and record through the browser rather than a server-side microphone.

Choose Browser voice (fast) first. Browser speech is provided by the browser's voice engine; identify it honestly in the presentation. The F5-TTS option exercises the local AI model and downloads its checkpoint if it has not been used before. Try that option ahead of class so downloads do not interrupt the presentation.

## A three-minute walkthrough

1. Type "What is Sky?". Show the answer and explain that it comes from the small FAQ.
2. Type "How much is tuition?". Show that the demo returns a fallback when similarity falls below the threshold; there is no real transfer to staff.
3. Record or upload "What languages can you speak?". Show Whisper's transcript, detected language, and matched question.
4. Optionally upload a Spanish question. Show the original transcript, English translation, and Spanish answer. Evaluate F5-TTS Spanish speech separately; it is not guaranteed to sound natural.
5. Select F5-TTS to show model-generated audio and the measured wait. Use a short answer or the Voice Studio link with "Hello Sky" to keep generation time manageable.

## Backup options

- Microphone unavailable: upload a short recording or type the question.
- F5-TTS is slow: show the answer immediately and use Browser voice (fast) for the walkthrough.
- Internet/cloud is unavailable: use the already-prepared local Windows environment and cached models.
- Browser voice is unavailable: read the on-screen answer, or generate a WAV with F5-TTS.

## What to explain

Whisper converts speech into text. TF-IDF and cosine similarity select an FAQ answer. The browser voice option is a presentation convenience; F5-TTS generates a new WAV using a reference voice. CPU inference latency, limited FAQ coverage, microphone/device access, and multilingual voice quality are current limitations.
