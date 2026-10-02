"""
quiz_study_app -- Lab 2, Section 3 custom app (full quiz study version).

Combines two existing Reachy Mini components:
  1. Reachy Mini App Template (this ReachyMiniApp structure) + the SDK's
     built-in audio output (mini.media.push_audio_sample) for scripted
     verbal feedback and questions.
  2. pollen-robotics/reachy_mini_dances_library -- "yeah_nod" for correct
     answers, "side_to_side_sway" for incorrect -- for the non-verbal
     feedback gesture.

Each participant completes 2 sessions (quiz set 1, then quiz set 2),
5 questions each. CONDITION_SEQUENCE sets which condition (A or B)
applies to each session: "AB", "BA", "AA", or "BB".
  Condition A -> verbal feedback only  (amplitude 0.0)
  Condition B -> verbal + non-verbal gesture feedback (amplitude 1.0)

WIZARD-OF-OZ DESIGN: the robot asks each question out loud, then the
facilitator listens to the participant's spoken answer themselves and
types in the judgment (correct / incorrect / repeat / interrupted /
failed) -- the robot does not capture or process audio input at all.
This sidesteps mic/STT reliability entirely and keeps the study focused
on how participants react to the robot's feedback, not on speech
recognition accuracy.

Run `generate_audio.py` once before the first real session to create
every audio clip referenced below.

Usage (run once per participant, in the lab, connected to the physical
robot -- do not start your own daemon against the Wireless robot, it
already runs one):

    python main.py --participant P01 --sequence AB
    python main.py --participant P02 --sequence BA
    python main.py --participant P03 --sequence AA
    python main.py --participant P04 --sequence BB

(With exactly 4 participants, one of each sequence gives full
counterbalancing across all 4 condition-order combinations.)
"""

import argparse
import csv
import datetime
import time
from pathlib import Path

import numpy as np
from reachy_mini import ReachyMini, ReachyMiniApp
from reachy_mini.utils import create_head_pose
from reachy_mini_dances_library.collection.dance import AVAILABLE_MOVES

from quiz_content import QUESTION_SETS

# ---------------- Named parameters -- set these before each session ----------------
PARTICIPANT_ID = "P01"          # de-identified ID, e.g. P01-P04
CONDITION_SEQUENCE = "AB"       # one of "AB", "BA", "AA", "BB"

MOVE_NAME_CORRECT = "yeah_nod"          # affirmative nod, played when correct
MOVE_NAME_INCORRECT = "side_to_side_sway"  # "no" headshake, played when incorrect
MOVE_CYCLES = 2                 # ~1s at 120 BPM -- brief, visible acknowledgment
BPM = 120.0
CONTROL_TS = 0.01               # 100 Hz control loop, matches dance_demo.py

NEUTRAL_POS = np.array([0.0, 0.0, 0.0])
NEUTRAL_EUL = np.zeros(3)

AUDIO_DIR = Path(__file__).parent / "audio"
LOG_DIR = Path(__file__).parent / "logs"


def timestamp():
    return datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]


def load_clip(path):
    import soundfile as sf
    samples, samplerate = sf.read(str(path), dtype="float32")
    return samples, samplerate


def parse_args():
    parser = argparse.ArgumentParser(description="Run one participant's quiz study session.")
    parser.add_argument("--participant", required=True, help="De-identified participant ID, e.g. P01")
    parser.add_argument("--sequence", required=True, choices=["AB", "BA", "AA", "BB"],
                         help="Condition sequence for this participant's two sessions")
    return parser.parse_args()


def preflight_check():
    """Verify every audio clip and dependency is in place BEFORE a real
    participant sits down -- far better to catch a missing file here than
    mid-session with someone waiting."""
    problems = []

    if not AUDIO_DIR.exists():
        problems.append(f"audio folder missing: {AUDIO_DIR}")
    else:
        existing = {p.name for p in AUDIO_DIR.glob("*.wav")}
        expected = {"fb_correct.wav"}
        for items in QUESTION_SETS.values():
            for item in items:
                expected.add(f"q_{item['id']}.wav")
                expected.add(f"fb_incorrect_{item['id']}.wav")
        missing_clips = sorted(expected - existing)
        if missing_clips:
            problems.append(f"missing audio clips ({len(missing_clips)}): {missing_clips}")

    try:
        import soundfile  # noqa: F401
        import scipy  # noqa: F401
    except ImportError as e:
        problems.append(f"missing dependency: {e}")

    for name in (MOVE_NAME_CORRECT, MOVE_NAME_INCORRECT):
        if name not in AVAILABLE_MOVES:
            problems.append(f"move '{name}' not found in reachy_mini_dances_library AVAILABLE_MOVES")

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    if problems:
        print("PRE-FLIGHT CHECK FAILED -- fix these before running a real session:")
        for p in problems:
            print(f"  - {p}")
        raise SystemExit(1)

    print(f"[{timestamp()}] PRE-FLIGHT CHECK PASSED")


class QuizStudyApp(ReachyMiniApp):
    # Force audio onto whatever machine runs this script (your laptop)
    # instead of WebRTC-to-the-robot, which was unreliable on this setup --
    # motor commands (gestures) still go to the real robot as normal.
    # Kept consistent across ALL participants (P01-P04) so audio source
    # is never a confound between sessions.
    request_media_backend = "local"

    def run(self, reachy_mini, stop_event):
        reachy_mini.media.start_playing()
        moves = {
            True: AVAILABLE_MOVES[MOVE_NAME_CORRECT],      # (move_fn, base_params, _)
            False: AVAILABLE_MOVES[MOVE_NAME_INCORRECT],
        }
        log_rows = []

        conditions = list(CONDITION_SEQUENCE)
        print(f"[{timestamp()}] STAGE=setup participant={PARTICIPANT_ID} sequence={CONDITION_SEQUENCE}")

        for session_idx, condition in enumerate(conditions, start=1):
            if stop_event.is_set():
                break
            amplitude = 1.0 if condition == "B" else 0.0
            question_set = QUESTION_SETS[session_idx]
            session_start = time.time()
            print(f"[{timestamp()}] STAGE=session_start session={session_idx} condition={condition}")

            for item in question_set:
                if stop_event.is_set():
                    break
                outcome, correct, repeats, note = self._run_trial(
                    reachy_mini, stop_event, item, amplitude, moves
                )
                log_rows.append({
                    "participant_id": PARTICIPANT_ID,
                    "session": session_idx,
                    "condition": condition,
                    "question_id": item["id"],
                    "trial_outcome": outcome,
                    "correct": correct,
                    "repeats": repeats,
                    "note": note,
                    "timestamp": timestamp(),
                })

            session_duration_s = time.time() - session_start
            print(f"[{timestamp()}] STAGE=session_end session={session_idx} condition={condition} duration_s={session_duration_s:.2f}")
            log_rows.append({
                "participant_id": PARTICIPANT_ID, "session": session_idx, "condition": condition,
                "question_id": "SESSION_TOTAL", "trial_outcome": "", "correct": "",
                "repeats": "", "note": f"duration_s={session_duration_s:.2f}",
                "timestamp": timestamp(),
            })

            if session_idx < len(conditions) and not stop_event.is_set():
                input(f"[{timestamp()}] Session {session_idx} complete. Press Enter when ready to start session {session_idx + 1}... ")

        reachy_mini.media.stop_playing()
        self._write_log(log_rows)
        print(f"[{timestamp()}] STAGE=done")

    def _run_trial(self, reachy_mini, stop_event, item, amplitude, moves):
        """Wizard-of-Oz trial: the robot asks the question out loud, then the
        facilitator -- who hears the participant's spoken answer directly --
        judges it themselves and types the result in. No audio is captured
        or processed by the robot."""
        repeats = 0
        while True:
            if stop_event.is_set():
                return "Interrupted", "", repeats, "stop requested"

            self._play_clip(reachy_mini, AUDIO_DIR / f"q_{item['id']}.wav")
            print(f"[{timestamp()}] STAGE=question_asked id={item['id']} text={item['question']!r} repeats={repeats}")
            print(f"[{timestamp()}] STAGE=listening (facilitator judges the spoken answer)")

            choice = self._get_judgment()

            if choice == "r":
                repeats += 1
                print(f"[{timestamp()}] STAGE=repeated id={item['id']} repeat_count={repeats}")
                continue

            if choice == "x":
                self._return_to_neutral(reachy_mini)
                return "Interrupted", "", repeats, "flagged by facilitator"

            if choice == "f":
                self._return_to_neutral(reachy_mini)
                return "Failed", "", repeats, "flagged by facilitator"

            correct = choice == "c"
            clip_name = "fb_correct.wav" if correct else f"fb_incorrect_{item['id']}.wav"
            move_fn, base_params, _ = moves[correct]
            self._play_clip(reachy_mini, AUDIO_DIR / clip_name)
            self._play_nonverbal_gesture(reachy_mini, stop_event, move_fn, base_params, amplitude, correct)
            self._return_to_neutral(reachy_mini)
            return "Completed", correct, repeats, ""

    def _get_judgment(self):
        """Reprompt on a mistyped key WITHOUT touching the robot -- only a
        real [r]epeat should make it re-ask the question out loud."""
        while True:
            choice = input(
                "  Judge the participant's answer yourself: "
                "[c]orrect / [i]ncorrect / [r]epeat / interru[x]ted / [f]ailed > "
            ).strip().lower()
            if choice in ("c", "i", "r", "x", "f"):
                return choice
            print("  (not understood -- enter c, i, r, x, or f)")

    def _play_clip(self, reachy_mini, clip_path):
        samples, sr = load_clip(clip_path)
        out_sr = reachy_mini.media.get_output_audio_samplerate()
        if sr != out_sr:
            from scipy.signal import resample
            samples = resample(samples, int(len(samples) * out_sr / sr))
        reachy_mini.media.push_audio_sample(samples)
        time.sleep(len(samples) / out_sr)

    def _play_nonverbal_gesture(self, reachy_mini, stop_event, move_fn, base_params, amplitude, correct):
        """Runs for the same duration regardless of condition; only the
        amplitude-scaled offsets differ, so Condition A and B have identical
        timing per the 5.1 'held constant' requirement. The MOVE differs by
        correctness (yeah_nod vs side_to_side_sway), not by condition."""
        current_params = base_params.copy()
        for key in current_params:
            if "amplitude" in key or key.endswith("_amp"):
                current_params[key] *= amplitude

        subcycles_per_beat = base_params.get("subcycles_per_beat", 1.0)
        target_beats = MOVE_CYCLES / subcycles_per_beat if subcycles_per_beat > 0 else MOVE_CYCLES
        duration_s = target_beats * 60.0 / BPM
        move_name = MOVE_NAME_CORRECT if correct else MOVE_NAME_INCORRECT
        print(f"[{timestamp()}] STAGE=nonverbal_feedback move={move_name} amplitude={amplitude} duration_s={duration_s:.2f}")

        t_beats = 0.0
        last_loop_time = time.time()
        while t_beats < target_beats:
            if stop_event.is_set():
                break
            loop_start = time.time()
            dt = loop_start - last_loop_time
            last_loop_time = loop_start
            t_beats += dt * (BPM / 60.0)

            offsets = move_fn(t_beats, **current_params)
            final_pos = NEUTRAL_POS + offsets.position_offset
            final_eul = NEUTRAL_EUL + offsets.orientation_offset
            final_ant = offsets.antennas_offset

            reachy_mini.set_target(
                create_head_pose(*final_pos, *final_eul, degrees=False),
                antennas=final_ant,
            )
            time.sleep(max(0, CONTROL_TS - (time.time() - loop_start)))

    def _return_to_neutral(self, reachy_mini):
        neutral_head = create_head_pose(yaw=0, pitch=0, roll=0, degrees=True)
        reachy_mini.goto_target(
            head=neutral_head,
            antennas=np.array([0.0, 0.0]),
            duration=0.5,
        )
        time.sleep(0.5)

    def _write_log(self, rows):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        fname = LOG_DIR / f"trial_log_{PARTICIPANT_ID}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        fieldnames = ["participant_id", "session", "condition", "question_id", "trial_outcome", "correct", "repeats", "note", "timestamp"]
        with open(fname, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"[{timestamp()}] STAGE=log_written path={fname}")


if __name__ == "__main__":
    args = parse_args()
    PARTICIPANT_ID = args.participant
    CONDITION_SEQUENCE = args.sequence

    preflight_check()
    print(f"[{timestamp()}] Starting session for participant={PARTICIPANT_ID} sequence={CONDITION_SEQUENCE}")

    app = QuizStudyApp()
    try:
        app.wrapped_run()
    except KeyboardInterrupt:
        app.stop()
