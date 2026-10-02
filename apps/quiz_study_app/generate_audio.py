"""Run once to pre-generate every audio clip the quiz_study_app needs.
Offline, no API key -- uses macOS's built-in `say` + `afconvert`.

Usage:
    cd apps/quiz_study_app
    python generate_audio.py
"""
import subprocess
from pathlib import Path

from quiz_content import QUESTION_SETS, CORRECT_FEEDBACK_TEXT, incorrect_feedback_text

AUDIO_DIR = Path(__file__).parent / "audio"
VOICE = "Samantha"


def say_to_wav(text, out_path):
    aiff_path = out_path.with_suffix(".aiff")
    subprocess.run(["say", "-v", VOICE, text, "-o", str(aiff_path)], check=True)
    subprocess.run(
        ["afconvert", str(aiff_path), str(out_path), "-d", "LEI16@16000", "-f", "WAVE", "-c", "1"],
        check=True,
    )
    aiff_path.unlink()
    print(f"wrote {out_path.name}")


def main():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    say_to_wav(CORRECT_FEEDBACK_TEXT, AUDIO_DIR / "fb_correct.wav")

    for items in QUESTION_SETS.values():
        for item in items:
            say_to_wav(item["question"], AUDIO_DIR / f"q_{item['id']}.wav")
            say_to_wav(incorrect_feedback_text(item), AUDIO_DIR / f"fb_incorrect_{item['id']}.wav")

    n = len(list(AUDIO_DIR.glob("*.wav")))
    print(f"Done. Generated {n} clips in {AUDIO_DIR}")


if __name__ == "__main__":
    main()
