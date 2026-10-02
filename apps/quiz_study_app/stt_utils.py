"""Local, offline speech-to-text for quiz_study_app, using faster-whisper.

No API key and no network call at inference time -- only the very first
run needs network access, to download the model weights once (cached
afterward). Everything after that runs fully offline.
"""
import re
import time

import numpy as np

MODEL_SIZE = "tiny.en"
_model = None


def get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        print(f"Loading faster-whisper model ({MODEL_SIZE})... happens once per run.")
        _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return _model


def record_answer(reachy_mini, duration_s=4.0, poll_interval_s=0.0, verbose=True):
    """Record from Reachy Mini's microphone for a fixed duration.

    get_audio_sample() pulls ONE buffer per call from a live GStreamer
    appsink queue -- it does not accumulate audio between calls, so a slow
    polling loop drops audio. Poll as fast as possible (poll_interval_s=0.0
    by default, i.e. no sleep at all) to minimize dropped buffers.

    Returns a mono float32 numpy array at the mic's input sample rate (16kHz).
    """
    reachy_mini.media.start_recording()
    chunks = []
    polls = 0
    hits = 0
    start = time.time()
    while time.time() - start < duration_s:
        sample = reachy_mini.media.get_audio_sample()
        polls += 1
        if sample is not None and len(sample) > 0:
            chunks.append(sample)
            hits += 1
        if poll_interval_s > 0:
            time.sleep(poll_interval_s)
    reachy_mini.media.stop_recording()

    if verbose:
        total_samples = sum(len(c) for c in chunks)
        print(f"  [record_answer] polls={polls} non_empty={hits} total_samples={total_samples}")

    if not chunks:
        return np.zeros(0, dtype=np.float32)

    stereo = np.concatenate(chunks, axis=0)
    mono = stereo.mean(axis=1).astype(np.float32)
    return mono


def transcribe(mono_audio):
    """Transcribe a mono float32 16kHz numpy array. Returns "" for silence."""
    if len(mono_audio) == 0:
        return ""
    model = get_model()
    segments, _info = model.transcribe(mono_audio, language="en", vad_filter=True)
    return " ".join(seg.text for seg in segments).strip()


_NUMBER_WORDS = {"7": "seven", "8": "eight"}


def _normalize(text):
    text = text.lower()
    for digit, word in _NUMBER_WORDS.items():
        text = text.replace(digit, word)
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return " ".join(text.split())


def is_correct(transcript, answer):
    return _normalize(answer) in _normalize(transcript)
