"""
demo_conditions.py -- quick robot-only demo for the Section 3 deliverable:
one complete cycle under Condition A (verbal feedback only) and one
complete cycle under Condition B (verbal + non-verbal gesture feedback),
run back-to-back.

Reuses the exact same clip-playback and gesture logic as main.py (via
QuizStudyApp's own methods) so this is a true demo of the tested app, not
a re-implementation. It does NOT write to the trial log and is NOT a real
study session -- just for capturing the condition-contrast demo clip.

Usage:
    cd apps/quiz_study_app
    python demo_conditions.py
"""
import threading
import time

from reachy_mini import ReachyMini
from reachy_mini_dances_library.collection.dance import AVAILABLE_MOVES

from quiz_content import QUESTION_SETS
from main import QuizStudyApp, AUDIO_DIR, MOVE_NAME_CORRECT, MOVE_NAME_INCORRECT


def run_one_cycle(app, reachy_mini, stop_event, label, amplitude, item, correct):
    kind = "verbal only" if amplitude == 0.0 else "verbal + non-verbal"
    print(f"\n=== Condition {label} ({kind}) ===")
    print(f"Question: {item['question']!r}")
    app._play_clip(reachy_mini, AUDIO_DIR / f"q_{item['id']}.wav")

    time.sleep(1.0)  # stand-in pause for the participant's spoken answer

    move_name = MOVE_NAME_CORRECT if correct else MOVE_NAME_INCORRECT
    move_fn, base_params, _ = AVAILABLE_MOVES[move_name]
    clip_name = "fb_correct.wav" if correct else f"fb_incorrect_{item['id']}.wav"

    print(f"Feedback: {'correct' if correct else 'incorrect'} -> clip={clip_name} move={move_name}")
    app._play_clip(reachy_mini, AUDIO_DIR / clip_name)
    app._play_nonverbal_gesture(reachy_mini, stop_event, move_fn, base_params, amplitude, correct)
    app._return_to_neutral(reachy_mini)


def main():
    app = QuizStudyApp()
    stop_event = threading.Event()

    item_a = QUESTION_SETS[1][0]
    item_b = QUESTION_SETS[2][0]

    with ReachyMini(media_backend="default") as mini:
        mini.media.start_playing()

        run_one_cycle(app, mini, stop_event, "A", amplitude=0.0, item=item_a, correct=True)
        time.sleep(1.5)
        run_one_cycle(app, mini, stop_event, "B", amplitude=1.0, item=item_b, correct=True)

        mini.media.stop_playing()

    print("\nDemo complete.")


if __name__ == "__main__":
    main()
