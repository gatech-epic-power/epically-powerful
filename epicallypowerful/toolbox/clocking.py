"""
epicallypowerful clocking module
Authors: Jennifer Leestma (jleestma@gatech.edu), Siddharth Nathella (snathella@gatech.edu), Christoph Nuesslein (cnuesslein3@gatech.edu)
Date: 08/19/2023

This module contains the classes and commands for creating a set
frequency clock within the main while loop of your top level script.
"""

import time
try:
    from epicallypowerful.toolbox._clocking import TimedLoopC
except ImportError:
    print("WARNING: TimedLoopC not found, using fallback implementation. This may not be as efficient.")

def TimedLoop(rate, tolerance=0.1, verbose=True):
    """Creates a TimedLoop object, which can be used to enforce a set loop frequency. This uses a "scheduled" sleep method to reduce busy looping, and will adjust the 
    sleep time based on the actual time taken for each loop iteration to ensure average frequency is maintained. This means over time, the number of iterations will
    tightly match the expected number of iterations.

    Args:
        rate (int): The desired loop frequency in Hz.
        tolerance (float, optional): The acceptable time step error tolerance as a proportion of the time step. Defaults to 0.1.
        verbose (bool, optional): Whether to print verbose output. Defaults to True.

    Returns:
        TimedLoopC: A TimedLoopC object configured with the specified parameters.
    """
    return TimedLoopC(rate=rate, tolerance=tolerance, verbose=verbose)

class LoopTimer:
    """Class for creating a simple timed loop manager. This object will attempt to enforce a set frequency when used in a looped script.
    NOTE: this frequency cannot be guaranteed, and the actual frequency should be recorded if this is important for your application. Please
    see the benchmarks for expected maximum performance.

    Example:
        .. code-block:: python

            
            from epicpower.toolbox.clocking import LoopTimer
            looper = LoopTimer(operating_rate=200)

            while True:
                if looper.continue_loop():
                    # do something approximately every 5ms
                    pass

    Args:
            operating_rate (int): Desired operating frequency (in Hz)
            time_step_error_tolerance (float, optional): Tolerance for time step error, as a proporiton of the time step. i.e. 0.01 = 1% error. Defaults to 0.05.
    """

    def __init__(self, operating_rate, time_step_error_tolerance=0.1, verbose=False):
        # self.previous_time = time.perf_counter() # tracks previous time to trigger next loop
        self.previous_time = None
        self.desired_time_step = 1 / operating_rate  # calculates time step
        self.recent_time_step = 1 / operating_rate  # just initializes to this, will be updated each loop
        self.time_step_error_tolerance_ratio = time_step_error_tolerance  # tolerance for time step error
        self.time_step_error_tolerance = (1+time_step_error_tolerance) * self.desired_time_step
        print(f"Time step error tolerance: {self.time_step_error_tolerance}")
        self.verbose = verbose

    def continue_loop(self):
        """Determines when loop should continue based on current time
        and operating rate

        """
        current_time = time.perf_counter()
        if self.previous_time == None:
            self.previous_time = current_time - self.desired_time_step

        if (current_time - self.previous_time) >= self.desired_time_step:
            self.recent_time_step = current_time - self.previous_time

            if (self.recent_time_step) >= self.time_step_error_tolerance:
                if self.verbose: print(f"TIME STEP WARNING: Expected {self.desired_time_step*1000:^.3f} ms, operating at {(self.recent_time_step)*1000:^.3f} ms")
            
            self.previous_time = current_time  # reset previous time to current time
            return True
        else:
            return False

    def __call__(self):
        return self.continue_loop()

class timed_loop:
    """Timed looping module can be used either as the iterator for a for loop
    or as the conditional of a while loop. This provides less flexibility than
    the LoopTimer class but allows for simpler creation of a loop with a set
    frequency with optional end time condition.
    """

    def __init__(self, operating_rate, total_time=None):
        self.operating_rate = operating_rate
        self.increment = 1 / operating_rate
        self.prev_iter = time.perf_counter()
        self.total_time = total_time
        self.t0 = None

    def __iter__(self):
        return self

    def _hold_until_next(self):
        while time.perf_counter() - self.prev_iter < self.increment:
            pass
        self.prev_iter = time.perf_counter()
        if self.t0 == None:
            self.t0 = self.prev_iter
        if self.total_time is not None:
            return self.prev_iter - self.t0 < self.total_time
        return True

    def __next__(self):
        result = self._hold_until_next()
        if result:
            return self.prev_iter
        raise StopIteration

    def __call__(self):
        result = self._hold_until_next()
        return result


if __name__ == "__main__":
    total_time = 20 # seconds
    test_rate = 200 # Hz
    tolerance = 0.1 # %
    frames = total_time * test_rate

    print(f"===Testing TimedLoop at {test_rate}Hz for {total_time}s (aka {test_rate*total_time} frames)===")
    looper = TimedLoop(test_rate, tolerance, verbose=False)
    times = []
    tog = time.perf_counter()
    while myt := looper():
        times.append(myt)
        if len(times) >= frames: break
    # Calculate the average loop time
    times = [times[i] - times[i-1] for i in range(1, len(times))]
    print(times[0:10])
    print(f"Average loop time: {sum(times)/len(times)*1000:.6f} ms")
    print(f"Average loop rate: {1/(sum(times)/len(times)):.3f} Hz")
    print(f"Total time: {time.perf_counter() - tog:.6f} seconds")
