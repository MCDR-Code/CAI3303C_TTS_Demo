"""
Sky Voice Demo: speech-to-text -> answer -> text-to-speech

The full loop a voice assistant like Sky needs:

    1. LISTEN   record the question from the microphone (or load a .wav file)
    2. STT      Whisper turns the audio into text and detects the language
    3. ANSWER   TF-IDF + cosine similarity finds the closest FAQ question
                (the same similarity idea from Week 6)
    4. TTS      the F5-TTS API from Week 4 turns the answer into speech
    5. SPEAK    play the generated .wav

Every stage is timed, because in a voice assistant the wait (latency)
is what the user notices first.

Before running: start the F5-TTS API in another terminal
    Run Start-TTS.ps1 from the parent TTS folder.
    Run Start-Demo.ps1 there to use the shared .venv automatically.

Examples:
    python sky_voice_demo.py                        # record 5 seconds from the mic
    python sky_voice_demo.py --seconds 7            # record longer
    python sky_voice_demo.py --audio question.wav   # use a recorded file
    python sky_voice_demo.py --text "What is Sky?"  # skip STT, test the rest
    python sky_voice_demo.py --no-tts               # skip TTS, test STT + answer
"""

import argparse
import json
import os
import sys
import time

import numpy as np
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE_RATE = 16000          # Whisper expects 16 kHz mono audio
TTS_URL = "http://localhost:5000"
THRESHOLD = 0.5              # below this score, Sky admits it does not know
FALLBACK_EN = "Sorry, I don't know that one yet. Let me connect you with a person who can help."
FALLBACK_ES = "Lo siento, todavía no sé eso. Le voy a conectar con una persona que le pueda ayudar."


# ---------------------------------------------------------------- 1. LISTEN
def record(seconds):
    """Record from the default microphone. Returns a float32 array at 16 kHz."""
    import sounddevice as sd
    try:
        sd.query_devices(kind='input')
        sd.check_input_settings(samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    except (sd.PortAudioError, ValueError) as error:
        raise SystemExit(
            'No usable default microphone was found. Select an input device in '
            'Windows Settings > System > Sound and check microphone permissions, '
            'or use Start-Demo.ps1 -Text "What is Sky?" or -Audio with a recording.'
        ) from error
    print(f"\nRecording for {seconds} seconds... ask your question now.")
    audio = sd.rec(int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                   channels=1, dtype="float32")
    sd.wait()
    print("Done recording.")
    return audio.flatten()


# ---------------------------------------------------------------- 2. STT
def speech_to_text(model, audio):
    """
    Whisper does two jobs here:
      - transcribe: write down what was said, in the language it was said in
      - translate:  if it wasn't English, also produce an English version,
                    so it can be matched against the English FAQ
    `audio` can be a numpy array or a path to an audio file.
    """
    result = model.transcribe(audio, fp16=False)
    text = result["text"].strip()
    lang = result.get("language", "en")

    english = text
    if lang != "en":
        english = model.transcribe(audio, task="translate", fp16=False)["text"].strip()
    return text, lang, english


# ---------------------------------------------------------------- 3. ANSWER
# Filler words that appear in almost every question and carry no meaning for
# matching. Removing them keeps "What is the weather?" from matching
# "What is Sky?" just because both start with "what is".
FILLER = ["a", "an", "the", "is", "are", "am", "be", "do", "does", "can",
          "could", "would", "will", "i", "me", "my", "you", "your", "it",
          "this", "that", "of", "to", "in", "at", "on", "for", "and", "or",
          "please", "what", "how", "where", "which", "who", "when", "why",
          "tell", "about", "exactly", "has", "have"]


class FAQMatcher:
    """Turn questions into TF-IDF vectors and pick the closest one by cosine similarity."""

    def __init__(self, path):
        with open(path, encoding="utf-8") as f:
            self.faq = json.load(f)
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words=FILLER)
        # Each FAQ entry has a few rewordings of the same question, like the
        # FAQ case study from Week 6. Every rewording gets its own vector.
        self.phrasings, self.owner = [], []
        for i, entry in enumerate(self.faq):
            for q in entry["questions"]:
                self.phrasings.append(q)
                self.owner.append(i)

    def best_match(self, question):
        # The user's question is vectorized together with the FAQ, so words
        # the FAQ has never seen (like "parking") still count and pull the
        # score down, instead of being silently ignored.
        matrix = self.vectorizer.fit_transform(self.phrasings + [question])
        scores = cosine_similarity(matrix[-1], matrix[:-1])[0]
        i = int(np.argmax(scores))
        return self.faq[self.owner[i]], self.phrasings[i], float(scores[i])


def choose_answer(entry, score, lang):
    if entry is None or score < THRESHOLD:
        return FALLBACK_ES if lang == "es" else FALLBACK_EN
    if lang == "es" and entry.get("answer_es"):
        return entry["answer_es"]
    return entry["answer_en"]


# ---------------------------------------------------------------- 4. TTS
def text_to_speech(text, voice, out_path):
    """Send the answer to the Week 4 F5-TTS API and save the .wav it returns."""
    r = requests.post(f"{TTS_URL}/tts", json={"username": voice, "text": text}, timeout=300)
    if r.status_code != 200:
        raise RuntimeError(f"TTS API error {r.status_code}: {r.text[:500]}")
    with open(out_path, "wb") as f:
        f.write(r.content)
    return out_path


# ---------------------------------------------------------------- 5. SPEAK
def play(path):
    if sys.platform.startswith("win"):
        import winsound
        winsound.PlaySound(path, winsound.SND_FILENAME)
    else:
        print(f"(Open {path} to listen.)")


# ---------------------------------------------------------------- main loop
def main():
    p = argparse.ArgumentParser(description="Sky voice loop: STT -> answer -> TTS")
    p.add_argument("--audio", help="path to a recorded question (.wav/.mp3)")
    p.add_argument("--text", help="type the question instead of speaking it")
    p.add_argument("--seconds", type=float, default=5, help="recording length")
    p.add_argument("--whisper", default="base",
                   help="Whisper model size: tiny, base, small, medium, large")
    p.add_argument("--voice", default="default", help="voice name registered in the F5-TTS API")
    p.add_argument("--no-tts", action="store_true", help="skip the speech output step")
    args = p.parse_args()

    timings = {}
    matcher = FAQMatcher(os.path.join(HERE, "faq.json"))

    # Steps 1 + 2: get the question as text
    if args.text:
        question, lang, english = args.text, "en", args.text
    else:
        import whisper
        t = time.perf_counter()
        model = whisper.load_model(args.whisper)
        timings["load Whisper model (once)"] = time.perf_counter() - t

        audio = args.audio if args.audio else record(args.seconds)

        t = time.perf_counter()
        question, lang, english = speech_to_text(model, audio)
        timings["speech to text"] = time.perf_counter() - t

    print(f"\nHeard ({lang}): {question}")
    if english != question:
        print(f"In English:    {english}")

    # Step 3: find the answer
    t = time.perf_counter()
    entry, matched, score = matcher.best_match(english)
    answer = choose_answer(entry, score, lang)
    timings["find answer"] = time.perf_counter() - t

    print(f"\nClosest FAQ:   {matched}  (cosine similarity {score:.2f}, threshold {THRESHOLD})")
    print(f"Sky answers:   {answer}")

    # Steps 4 + 5: speak it
    if not args.no_tts:
        out_dir = os.path.join(HERE, "gen_audio")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "sky_answer.wav")
        t = time.perf_counter()
        text_to_speech(answer, args.voice, out_path)
        timings["text to speech"] = time.perf_counter() - t
        print(f"\nSaved audio:   {out_path}")
        play(out_path)

    print("\nTime per stage:")
    for stage, secs in timings.items():
        print(f"  {stage:<28}{secs:6.2f} s")
    total = sum(v for k, v in timings.items() if "once" not in k)
    print(f"  {'total wait for the user':<28}{total:6.2f} s")


if __name__ == "__main__":
    main()
