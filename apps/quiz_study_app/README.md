# Quiz Study App

Lab 2 (INFO 5356), Section 3 — custom app running on the physical Reachy Mini.

This is a short quiz the robot runs with a participant, to see how they react to two different feedback styles: verbal-only vs. verbal plus a head gesture. It's built on two existing pieces rather than from scratch: the Reachy Mini SDK's audio playback, and the `yeah_nod` / `side_to_side_sway` moves from [pollen-robotics/reachy_mini_dances_library](https://github.com/pollen-robotics/reachy_mini_dances_library) (vendored in at the repo root, so a plain clone has everything it needs — no submodule setup).

## The gist

Each participant does two sessions of 5 questions, using two different quiz sets so nobody sees the same question twice. Which condition applies to which session depends on the sequence you pass in:

- **Condition A** — feedback audio only, no visible movement.
- **Condition B** — same audio, plus the head nods (correct) or shakes side to side (incorrect).

| sequence | session 1 | session 2 |
|---|---|---|
| AB | A | B |
| BA | B | A |
| AA | A | A |
| BB | B | B |

The robot doesn't listen to the participant at all — no mic, no speech-to-text. It asks the question out loud, the participant answers out loud, and whoever's running the session hears the answer and judges it themselves (correct/incorrect/repeat/interrupted/failed). We went this route after testing local STT (faster-whisper) and realizing transcription errors would become their own confound in the data — easier to just have a human judge it and log that.

## Files

```
apps/quiz_study_app/
├── main.py              the actual study app, one run per participant
├── demo_conditions.py   runs one A cycle then one B cycle back to back, for demo footage
├── quiz_content.py       the two question sets + feedback scripts
├── generate_audio.py     one-time: generates all 21 clips with macOS `say`, no API needed
├── audio/                 generated .wav files live here
└── logs/                  CSV per participant session, written automatically

reachy_mini_dances_library/   vendored dependency, see above
```

## Setting it up

```
git clone git@github.com:xinxuan-xs444/info5356-lab-1.git
cd info5356-lab-1
python3 -m venv reachy_mini_env
source reachy_mini_env/bin/activate
pip install soundfile scipy
```

Then generate the audio clips once (offline, no API key):

```
cd apps/quiz_study_app
python generate_audio.py
```

That should produce 21 `.wav` files in `audio/` — 1 shared correct-feedback clip plus 5 questions and 5 incorrect-feedback clips per quiz set.

For the robot itself: in the simulator, start `mjpython $(which reachy-mini-daemon) --sim` in its own tab. On the physical robot, you don't start a daemon yourself — just make sure it's powered on and shows as connected in the Reachy Mini Control app, not stuck on "Standby."

## Running a session

```
python main.py --participant P01 --sequence AB
```

`--sequence` is required (AB/BA/AA/BB). There's also an optional `--quiz-order`, default `12` (set 1 in session 1, set 2 in session 2) — pass `21` to flip it. It runs a pre-flight check first that catches missing clips or dependencies before anyone's sitting in front of the robot waiting.

Our actual 4 participants:

| participant | command | session 1 | session 2 |
|---|---|---|---|
| P01 | `--sequence AB` | A + Quiz 1 | B + Quiz 2 |
| P02 | `--sequence BA` | B + Quiz 1 | A + Quiz 2 |
| P03 | `--sequence AB --quiz-order 21` | A + Quiz 2 | B + Quiz 1 |
| P04 | `--sequence BA --quiz-order 21` | B + Quiz 2 | A + Quiz 1 |

Full crossing of condition order and quiz order across the 4 participants, no repeats.

As facilitator, for each question you'll see:

```
Judge the participant's answer yourself: [c]orrect / [i]ncorrect / [r]epeat / interru[x]ted / [f]ailed >
```

Typing a stray key just reprompts you, it won't make the robot re-ask the question — only `r` does that. It pauses between session 1 and 2 so you can give the participant a breather.

A CSV gets written automatically to `logs/trial_log_<participant>_<timestamp>.csv`, columns: `participant_id`, `session`, `quiz_set`, `condition`, `question_id`, `trial_outcome`, `correct`, `repeats`, `note`, `timestamp`. 12 rows per participant — 10 trials plus a session-total row for each of the two sessions.

## Demo clip

```
python demo_conditions.py
```

Runs one A cycle and one B cycle back to back using the same code `main.py` uses, just without touching the real log. This is what we used to capture the condition-contrast footage for the report.

## A few things worth knowing

The gesture always runs in both conditions — what changes is the amplitude (0 for A, full for B), not whether it happens at all. That keeps the timing identical between conditions so A and B only differ in what's visible, not how long feedback takes. Which move plays depends on whether the answer was right or wrong, independent of condition — nod for correct, sway for incorrect, either way.

Audio plays from whoever's laptop is running the script, not the robot's own speaker (`request_media_backend = "local"`). We actually got WebRTC-to-the-robot working at one point, but kept it on local so every participant had the same audio source — didn't want that varying between sessions on top of the actual A/B manipulation.

Connecting to the real robot uses the default `"auto"` connection mode. On a laptop running the Reachy Mini Control app, that's the only thing that actually reaches the robot — it goes through the Control app's own relay on localhost:8000. A direct network connection to `reachy-mini.local` just times out on this setup, for whatever reason.

## Limitations to mention in the writeup

Facilitator judges answers manually, so it's not a blind measure — worth naming directly. And obviously, 4 participants is a small sample for a class exercise — treat the results as exploratory rather than something to draw strong conclusions from.
