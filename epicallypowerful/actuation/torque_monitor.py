import time
import math
from collections import deque

class RMSTorqueMonitor:
    """Object allows for a real-time calculation of RMS torque over a sliding time window. This can be used
    to monitor if the measured torque exceeds a specified limit, per the Acutators specification.

        Args:
            limit (float): The maximum allowable RMS torque (Nm). If the RMS torque over the window exceeds this value, the function `over_limit` will return True.
            window (float, optional): The time window over which to calculate RMS (seconds). Defaults to 20.0.
    """
    def __init__(self, limit: float, window: float=20.0):
        self.window = window # seconds
        self.limit = limit # torque limit in Nm
        self.vals = deque() # A deque of tuples (squared values, timestamp)
        self.sum_sqr = 0.0
        self.rms = 0.0

    def update(self, new_val: float) -> tuple[float, bool]:
        """Update the RMS torque value with a new measurement.

        Args:
            new_val (float): The new torque measurement (Nm).

        Returns:
            tuple[float, bool]: A tuple containing the current RMS value and a boolean indicating if the limit is exceeded.
        """
        now = time.perf_counter()
        sq = new_val ** 2
        self.vals.append((sq, now))
        self.sum_sqr += sq

        while self.vals and (now - self.vals[0][1]) > self.window:
            old_sq, _ = self.vals.popleft()
            self.sum_sqr -= old_sq

        self.rms = math.sqrt(self.sum_sqr / len(self.vals)) if self.vals else 0
        return self.rms, self.rms > self.limit

    def over_limit(self) -> bool:
        """Check if the current RMS torque exceeds the limit.

        Returns:
            bool: True if the RMS torque is over the limit, False otherwise.
        """
        return self.rms > self.limit
