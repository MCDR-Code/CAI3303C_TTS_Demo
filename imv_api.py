"""
F5-TTS Voice Cloning API — FIXED VERSION
Originally written by the instructor (see older/original/imv_api.py), Jan 2025.
Fixed Sep 2026 for CAI3303C Week04 assignment.

Two bugs prevented this from working against a current F5-TTS install:

1. --model default was the literal string "F5-TTS". That was a valid,
   hardcoded special case in F5-TTS's infer_cli.py as of Jan 2025:
       model = args.model or config.get("model", "F5-TTS")
       if model == "F5-TTS": ...
   Commit ca6e49a ("1.0.0 F5-TTS v1 base model...", 2025-03-12) removed
   that hardcoded branch and switched to a config-file registry:
       model_cfg = OmegaConf.load(f"configs/{model}.yaml")
   "F5-TTS" is not a file in src/f5_tts/configs/, so every /tts call
   failed with FileNotFoundError. Valid values today: F5TTS_v1_Base,
   F5TTS_Base, F5TTS_Small, F5TTS_v1_Small, E2TTS_Base, E2TTS_Small.
   Fixed by defaulting to "F5TTS_v1_Base" (current recommended model).

2. The "default" voice profile's reference audio was created as a
   literal empty file (open(path, 'wb').write(b'')) — a 0-byte file is
   not a valid WAV and audio loading fails regardless of the model fix.
   Fixed by pointing the default voice at F5-TTS's own bundled example
   reference audio (infer/examples/basic/basic_ref_en.wav), which ships
   inside the f5-tts pip package and is auto-resolved by its CLI's own
   path-patching logic — no local audio asset needed.

Other changes: CORS enabled (so a browser front end on a different
origin/port can call this directly), a GET /voices endpoint for the
front end to populate a voice picker, and CLI stdout/stderr are now
captured and returned on failure instead of being swallowed.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import threading
import uuid

# Initialize constants
# FIX #1: was 'F5-TTS' (a literal that stopped being valid as of F5-TTS v1.0.0,
# March 2025 — see module docstring). Current valid model names live under
# src/f5_tts/configs/*.yaml: F5TTS_v1_Base, F5TTS_Base, F5TTS_Small,
# F5TTS_v1_Small, E2TTS_Base, E2TTS_Small.
DEFAULT_MODEL_PATH = os.getenv('TTS_MODEL_PATH', 'F5TTS_v1_Base')
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = str(Path(os.getenv('TTS_OUTPUT_DIR', str(BASE_DIR / 'data' / 'output'))).resolve())
DEFAULT_PORT = int(os.getenv('TTS_API_PORT', 5000))
VOICES_DIR = str(BASE_DIR / 'data' / 'voices')
VOICES_LOG_FILE = str(BASE_DIR / 'data' / 'voices_log.json')

# Ensure necessary directories exist
os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
os.makedirs(VOICES_DIR, exist_ok=True)

# Initialize voices log
if not os.path.exists(VOICES_LOG_FILE):
    with open(VOICES_LOG_FILE, 'w') as f:
        json.dump({}, f)

if os.path.exists(VOICES_LOG_FILE):
    with open(VOICES_LOG_FILE, 'r') as f:
        voices_log = json.load(f)
else:
    voices_log = {}

default_username = "default"
# FIX #2: was a locally-created EMPTY file (0 bytes = not a valid WAV).
# Now points at the real reference clip F5-TTS ships inside its own
# package. infer_cli.py auto-resolves any ref_audio path containing
# "infer/examples/" to the installed package's actual location, so this
# works out of the box with no bundled audio asset of our own.
default_audio_path = "infer/examples/basic/basic_ref_en.wav"
default_text = "Some call me nature, others call me mother nature."


def ensure_user_directory(username):
    user_output_dir = os.path.join(DEFAULT_OUTPUT_DIR, username)
    os.makedirs(user_output_dir, exist_ok=True)
    return user_output_dir


if default_username not in voices_log:
    ensure_user_directory(default_username)
    voices_log[default_username] = {
        "reference_audio": default_audio_path,
        "reference_text": default_text
    }
    with open(VOICES_LOG_FILE, 'w') as f:
        json.dump(voices_log, f, indent=4)


def load_voices_log():
    with open(VOICES_LOG_FILE, 'r') as f:
        return json.load(f)


def save_voices_log(log):
    with open(VOICES_LOG_FILE, 'w') as f:
        json.dump(log, f, indent=4)


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024
CORS(app)  # allow the browser front end (served from a different port) to call this API
from demo.web_routes import blueprint as demo_blueprint
app.register_blueprint(demo_blueprint)
generation_lock = threading.Lock()


@app.errorhandler(413)
def upload_too_large(error):
    return jsonify(error='Audio uploads must be no larger than 25 MB.'), 413


@app.route('/add_voice', methods=['POST'])
def add_voice():
    if 'username' not in request.form or 'text' not in request.form or 'file' not in request.files:
        return jsonify({"error": "username, text, and file are required"}), 400

    username = request.form['username'].strip()
    text = request.form['text'].strip()
    file = request.files['file']

    if not username or not all(c.isascii() and (c.isalnum() or c in '_-') for c in username):
        return jsonify({"error": "username must contain only letters, numbers, underscores or hyphens"}), 400
    if not text:
        return jsonify({"error": "reference text is required"}), 400

    if not file.filename.lower().endswith(('.wav', '.mp3', '.flac', '.ogg', '.m4a')):
        return jsonify({"error": "file must be an audio file (.wav, .mp3, .flac, .ogg, .m4a)"}), 400

    voices_log = load_voices_log()
    voice_file_path = os.path.join(VOICES_DIR, f"{username}.wav")
    user_output_dir = ensure_user_directory(username)

    response_message = "Voice updated successfully" if username in voices_log else "Voice added successfully"

    file.save(voice_file_path)

    voices_log[username] = {
        "reference_audio": voice_file_path,
        "reference_text": text,
        "output_dir": user_output_dir
    }
    save_voices_log(voices_log)

    return jsonify({"message": response_message, "username": username}), 200


@app.route('/voices', methods=['GET'])
def list_voices():
    """Added: lets a front end populate a voice picker without guessing usernames."""
    voices_log = load_voices_log()
    return jsonify({"voices": list(voices_log.keys())}), 200


@app.route('/tts', methods=['POST'])
def generate_audio():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "a JSON object with username and text is required"}), 400
    username = payload.get('username')
    text = payload.get('text')

    if not isinstance(username, str) or not isinstance(text, str) or not username.strip() or not text.strip():
        return jsonify({"error": "username and text are required"}), 400
    if len(text) > 2000:
        return jsonify(error='Speech text must be at most 2000 characters.'), 400

    voices_log = load_voices_log()

    if username not in voices_log:
        return jsonify({"error": "Username not found"}), 404

    reference_audio = voices_log[username]['reference_audio']
    reference_text = voices_log[username]['reference_text']
    user_output_dir = DEFAULT_OUTPUT_DIR + "/" + username

    # Added: fail fast with a clear message instead of letting the CLI
    # crash confusingly if a user-uploaded reference file went missing.
    if reference_audio.startswith(VOICES_DIR) and not os.path.exists(reference_audio):
        return jsonify({"error": f"Reference audio missing for '{username}': {reference_audio}"}), 500

    if not generation_lock.acquire(blocking=False):
        return jsonify(error='Speech generation is busy. Try again shortly.'), 429
    try:
        os.makedirs(user_output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}.wav"
        output_path = os.path.join(user_output_dir, output_filename)

        cli_command = [
            sys.executable, "-m", "f5_tts.infer.infer_cli",
            "--model", DEFAULT_MODEL_PATH,
            "--ref_audio", reference_audio,
            "--ref_text", reference_text,
            "--gen_text", text,
            "--output_dir", user_output_dir,
            "--output_file", output_filename
        ]

        # Added: capture stdout/stderr so failures are debuggable instead
        # of a bare "CLI execution failed: <exit code>".
        subprocess.run(cli_command, check=True, capture_output=True, text=True, timeout=600)

        return send_file(output_path, as_attachment=True)
    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "CLI execution failed",
            "returncode": e.returncode,
            "stdout": e.stdout,
            "stderr": e.stderr,
        }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        generation_lock.release()


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "running", "model": DEFAULT_MODEL_PATH}), 200


if __name__ == '__main__':
    # host='0.0.0.0' is already correct for LAN/mobile access — a phone on
    # the same Wi-Fi can reach this at http://<your-laptop-ip>:5000
    app.run(host='0.0.0.0', port=DEFAULT_PORT, threaded=True)
