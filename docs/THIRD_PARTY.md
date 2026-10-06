# Sources and attribution

- F5-TTS upstream source: https://github.com/SWivid/F5-TTS, pinned to `9c614e9657089213efc6a7421b30630be138a3f5`. Its code is MIT-licensed; the upstream README states that its pretrained models use a CC-BY-NC license. Model downloads retain their original terms and are not included in this repository.
- Local audio-loading changes are stored as `patches/f5-windows-audio.patch` and applied to the pinned source by setup.
- Whisper: https://github.com/openai/whisper. Installed through the `openai-whisper` package; its upstream source and model license terms apply.
- Original Java clients and the initial Flask API were supplied for the CAI3303C classroom assignment. Their archived original versions remain locally in `older`.
- Flask, Flask-CORS, scikit-learn, requests, NumPy, sounddevice, PyTorch, and other dependencies retain their upstream licenses. Installing dependencies does not transfer ownership of their source or model assets.

The repository is an educational prototype and is not an official Miami Dade College service. FAQ answers are presentation content rather than a verified institutional knowledge base.
