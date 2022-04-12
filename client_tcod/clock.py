import time
import statistics
from collections import deque


class Clock:
    """Measure framerate performance and sync to a given framerate.
    Everything important is handled by `Clock.sync`.  You can use the fps
    properties to track the performance of an application.
    """

    def __init__(self) -> None:
        self.last_time = time.perf_counter()  # Last time this was synced.
        self.time_samples = deque()  # Delta time samples.
        self.max_samples = 64  # Number of fps samples to log.  Can be changed.
        self.drift_time = 0.0  # Tracks how much the last frame was overshot.

    def sync(self, fps=None) -> float:
        """Sync to a given framerate and return the delta time.
        `fps` is the desired framerate in frames-per-second.  If None is given
        then this function will track the time and framerate without waiting.
        `fps` must be above zero when given.
        """
        if fps is not None:
            # Wait until a target time based on the last time and framerate.
            desired_frame_time = 1 / fps
            target_time = self.last_time + desired_frame_time - self.drift_time
            # Sleep might take slightly longer than asked.
            sleep_time = max(0, target_time - self.last_time - 0.001)
            if sleep_time:
                time.sleep(sleep_time)
            # Busy wait until the target_time is reached.
            while (drift_time := time.perf_counter() - target_time) < 0:
                pass
            self.drift_time = min(drift_time, desired_frame_time)

        # Get the delta time.
        current_time = time.perf_counter()
        delta_time = max(0, current_time - self.last_time)
        self.last_time = current_time

        # Record the performance of the current frame.
        self.time_samples.append(delta_time)
        while len(self.time_samples) > self.max_samples:
            self.time_samples.popleft()

        return delta_time

    @property
    def min_fps(self) -> float:
        """The FPS of the slowest frame."""
        try:
            return 1 / max(self.time_samples)
        except (ValueError, ZeroDivisionError):
            return 0

    @property
    def max_fps(self) -> float:
        """The FPS of the fastest frame."""
        try:
            return 1 / min(self.time_samples)
        except (ValueError, ZeroDivisionError):
            return 0

    @property
    def mean_fps(self) -> float:
        """The FPS of the sampled frames overall."""
        if not self.time_samples:
            return 0
        try:
            return 1 / statistics.fmean(self.time_samples)
        except ZeroDivisionError:
            return 0

    @property
    def median_fps(self) -> float:
        """The FPS of the median frame."""
        if not self.time_samples:
            return 0
        try:
            return 1 / statistics.median(self.time_samples)
        except ZeroDivisionError:
            return 0

    @property
    def last_fps(self) -> float:
        """The FPS of the most recent frame."""
        if not self.time_samples or self.time_samples[-1] == 0:
            return 0
        return 1 / self.time_samples[-1]

    @property
    def last_frame_time_ms(self) -> float:
        """Time taken (in milliseconds) by the last frame."""
        return self.time_samples[-1] * 1000
