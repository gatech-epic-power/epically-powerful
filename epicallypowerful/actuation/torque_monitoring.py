import time
import math
class RMSTorqueMonitor:
    def __init__(self, window: float, limit: float):
        self.window = window
        self.limit = limit
        self.vals = [] # A list of tuples (squared values, timestamp)
        self.rms = 0

    def update(self, new_val: float) -> tuple[float, bool]:
        now = time.perf_counter()
        self.vals.append( (new_val**2, now) )
        self.vals = [(t, ts) for t, ts in self.vals if (now - ts) < self.window]
        self.rms = math.sqrt(sum(t for t,_ in self.vals) / len(self.vals)) if self.vals else 0
        return self.rms, self.rms > self.limit