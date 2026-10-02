"""Standalone sanity check -- run this BEFORE touching quiz_study_app.

Records a few seconds from Reachy Mini's microphone and transcribes it,
so we can confirm get_audio_sample() behaves as documented on your
installed SDK version before wiring it into the full study app.

Usage:
    cd apps/quiz_study_app
    python test_recording.py
"""
import time

import numpy as np
import soundfile as sf

from reachy_mini import ReachyMini
from stt_utils import record_answer, transcribe

with ReachyMini(media_backend="default") as mini:
    mini.media.start_playing()

    print("Get ready to say a word out loud...")
    time.sleep(1.5)
    print("Recording for 4 seconds now -- say something like 'Earth'.")

    audio = record_answer(mini, duration_s=4.0)
    print(f"Captured audio: shape={audio.shape}, dtype={audio.dtype}")

    if len(audio) > 0:
        peak = float(np.max(np.abs(audio)))
        rms = float(np.sqrt(np.mean(audio.astype(np.float64) ** 2)))
        print(f"Peak amplitude: {peak:.6f}   RMS: {rms:.6f}   (near-zero on both = likely silence)")
        sf.write("debug_capture.wav", audio, 16000)
        print("Saved to debug_capture.wav -- open it in Finder/QuickTime to listen back.")

    text = transcribe(audio)
    print(f"Transcript: {text!r}")

    mini.media.stop_playing()
