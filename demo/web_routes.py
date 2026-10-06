"""Browser interface for the Sky FAQ demonstration."""
import tempfile
import threading
import time
from pathlib import Path

from flask import Blueprint, jsonify, request, send_file

from demo.sky_voice_demo import FAQMatcher, THRESHOLD, choose_answer, speech_to_text

HERE = Path(__file__).resolve().parent
blueprint = Blueprint('sky_demo', __name__)
matcher = FAQMatcher(HERE / 'faq.json')
matcher_lock = threading.Lock()
whisper_lock = threading.Lock()
whisper_model = None


def answer_question(question, english, language):
    started = time.monotonic()
    with matcher_lock:
        entry, matched, score = matcher.best_match(english)
    fallback = score < THRESHOLD
    answer = choose_answer(entry, score, language)
    if fallback:
        answer = (
            'Todavía no tengo esa respuesta. Consulte con una persona del colegio.'
            if language == 'es' else
            "I don't have that answer yet. Please ask a college staff member."
        )
    return {
        'question': question, 'english': english, 'language': language,
        'answer': answer, 'matched': matched, 'score': round(score, 3),
        'threshold': THRESHOLD, 'fallback': fallback,
        'answer_seconds': round(time.monotonic() - started, 3),
    }


@blueprint.get('/')
@blueprint.get('/demo')
@blueprint.get('/demo/')
def demo_page():
    return send_file(HERE / 'index.html')


@blueprint.get('/studio')
def voice_studio():
    return send_file(HERE.parent / 'frontend' / 'index.html')


@blueprint.post('/demo/answer')
def typed_answer():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error='Send a JSON object containing text.'), 400
    text = payload.get('text')
    language = payload.get('language', 'en')
    if not isinstance(text, str) or not text.strip() or len(text) > 2000:
        return jsonify(error='Enter a question between 1 and 2000 characters.'), 400
    if language not in ('en', 'es'):
        return jsonify(error='Answer language must be en or es.'), 400
    # Typed questions use the English FAQ; spoken audio is translated by Whisper.
    return jsonify(answer_question(text.strip(), text.strip(), language))


@blueprint.post('/demo/transcribe')
def recorded_answer():
    global whisper_model
    upload = request.files.get('file')
    if upload is None or not upload.filename:
        return jsonify(error='Upload or record an audio file first.'), 400
    suffix = Path(upload.filename).suffix.lower()
    if suffix not in ('.webm', '.wav', '.mp3', '.m4a', '.ogg', '.mp4', '.flac'):
        return jsonify(error='Use WAV, MP3, WebM, M4A, OGG, MP4, or FLAC audio.'), 400
    if not whisper_lock.acquire(blocking=False):
        return jsonify(error='Sky is transcribing another recording. Try again shortly.'), 429
    started = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix='sky-question-') as folder:
            path = Path(folder) / ('question' + suffix)
            upload.save(path)
            if not path.stat().st_size:
                return jsonify(error='The recording is empty. Please try another file.'), 400
            import whisper
            if whisper_model is None:
                whisper_model = whisper.load_model('base')
            question, language, english = speech_to_text(whisper_model, str(path))
        if not question:
            return jsonify(error='No speech was recognized. Try a clearer recording.'), 422
        result = answer_question(question, english, language)
        result['transcribe_seconds'] = round(time.monotonic() - started, 3)
        return jsonify(result)
    except ImportError:
        return jsonify(error='Speech recognition is not installed. Run the project setup.'), 503
    except Exception as error:
        return jsonify(error=f'Could not transcribe this recording: {str(error)[:500]}'), 422
    finally:
        whisper_lock.release()
