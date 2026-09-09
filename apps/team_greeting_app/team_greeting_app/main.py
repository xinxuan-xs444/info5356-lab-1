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
from datetime import datetime

import numpy as np

from reachy_mini import ReachyMini, ReachyMiniApp
from reachy_mini.utils import create_head_pose


# TODO: define your named parameters here, e.g.:
# GREETING_DURATION_S: float = 2.0   # seconds
# NOD_AMPLITUDE_DEG: float = 15.0    # degrees


class TeamGreetingApp(ReachyMiniApp):
    custom_app_url: str | None = None
    request_media_backend: str | None = None

    def run(self, reachy_mini: ReachyMini, stop_event: threading.Event) -> None:
        # TODO: Stage 1 - ORIENT

        # TODO: Stage 2 - GREET

        # TODO: Stage 3 - RETURN TO NEUTRAL

        pass


if __name__ == "__main__":
    app = TeamGreetingApp()
    try:
        app.wrapped_run()
    except KeyboardInterrupt:
        app.stop()
