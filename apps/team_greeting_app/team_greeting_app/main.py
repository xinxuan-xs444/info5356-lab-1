"""
team_greeting_app

TODO: Implement a three-stage greeting behavior for Reachy Mini:
  1. Orient   - turn/lift toward an implied user
  2. Greet    - a greeting gesture using at least two expressive channels
                (head, body yaw, or antennas)
  3. Neutral  - return to resting pose

Requirements to keep in mind:
  - Check stop_event during any loops/waits so the app stops gracefully.
  - Print a timestamped marker at the start of each stage.
  - Expose at least two named motion/timing parameters with documented units.
  - No camera, microphone, cloud AI, or personal data collection.
"""

import threading
import time
import signal

import numpy as np

from reachy_mini import ReachyMini, ReachyMiniApp
from reachy_mini.utils import create_head_pose

#motion paramteres------------
ORIENT_DURATION: float = 2.0  # seconds- TIME TO LIFT AND TURN TOWARD USER
GREET_DURATION: float = 3.0  # seconds- TIME TO PERFORM GREETING GESTURE
BODY_YAW_AMPLITUDE: float = 30.0  # degrees- HOW FAR THE BODY TWISTS SIDE TO SIDE
ANTENNA_WAVE_AMPLITUDE: float =30.0  # degrees- HOW FAR THE ANTENNAS WAVE
WIGGLE_FREQUENCY: float = 1.5  # Hz- FREQUENCY OF THE WIGGLE MOVEMENT
NEUTRAL_DURATION: float = 1.0  # seconds- TIME TO RETURN TO RESTING POSE

def timestamp() -> str:
    """millisecond-precision timestamp for logging"""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def _interruptible_wait(duration_s: float, stop_event: threading.Event, step_s: float = 0.05) -> bool:
    """
    Sleep for `duration_s` seconds in small increments, checking `stop_event`
    frequently so the app can stop gracefully mid-wait.
    Returns True if the wait completed normally, False if stop was requested early.
    """
    elapsed = 0.0
    while elapsed < duration_s:
        if stop_event.is_set():
            return False
        step = min(step_s, duration_s - elapsed)
        time.sleep(step)
        elapsed += step
    return True



class TeamGreetingApp(ReachyMiniApp):
    def run(self, reachy_mini: ReachyMini, stop_event: threading.Event):
        try: 
            # Stage 1: Orient
            print(f"{timestamp()} - Stage 1: Orient")
            oriented_head=create_head_pose(pitch=-10, z=15, mm=True, degrees=True)
            reachy_mini.goto_target(head=oriented_head, duration=ORIENT_DURATION)
            
            if not _interruptible_wait(ORIENT_DURATION, stop_event):
                print(f"{timestamp()} STOP requested during ORIENT")
                return

            # Stage 2: Greet
            print(
                f"{timestamp()} - Stage 2: Greet"
                f"(body_yaw_amplitude={BODY_YAW_AMPLITUDE} deg, antenna_amplitude={ANTENNA_WAVE_AMPLITUDE} deg)"
                )

            start_time = time.time()
            while time.time() - start_time < GREET_DURATION:
                if stop_event.is_set():
                    print(f"[{timestamp()}] STOP requested during GREET")
                    return
                

                t = time.time() - start_time

                #Body shimmies side to side
                body_yaw_deg = BODY_YAW_AMPLITUDE * np.sin(2 * np.pi * WIGGLE_FREQUENCY * t)
                body_yaw_rad = np.deg2rad(body_yaw_deg)

                #Antennas fultter at double speed 
                antenna_deg = ANTENNA_WAVE_AMPLITUDE * np.sin(2 * np.pi * 2 * WIGGLE_FREQUENCY * t + np.pi/4)
                antenna_rad = np.deg2rad(antenna_deg)
                antennas = np.array([antenna_rad, -antenna_rad])

                reachy_mini.set_target(body_yaw=body_yaw_rad, antennas = antennas)
                time.sleep(0.02)


        # Stage 3: Neutral
        finally:
            # either completed or interrupted, return to neutral state
            self._return_to_neutral(reachy_mini, stop_event)
            
        print(f"{timestamp()} - Waiting for Ctrl+C")
        stop_event.wait()

    def _return_to_neutral(self, reachy_mini: ReachyMini, stop_event: threading.Event) -> None:
        print(f"[{timestamp()}] STAGE 3/3: RETURN TO NEUTRAL")
        neutral_head = create_head_pose(yaw=0, pitch=0, roll=0, degrees=True)
        reachy_mini.goto_target(
            head=neutral_head,
            antennas=np.array([0.0, 0.0]),
            body_yaw=0.0,
            duration=NEUTRAL_DURATION,
        )
        print(f"[{timestamp()}] - Returned to neutral.")

if __name__ == "__main__":
    app = TeamGreetingApp()
    # try:
    #    app.wrapped_run()
    # except KeyboardInterrupt:
    #    app.stop()
    
    # turn Ctrl+C commend to a signal instead of KeyboardInterrupt
    def request_stop(signum, frame):
        app.stop()
        
    signal.signal(signal.SIGINT, request_stop)
    app.wrapped_run()
