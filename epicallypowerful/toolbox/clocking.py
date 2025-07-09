"""
epicallypowerful clocking module
Authors: Jennifer Leestma (jleestma@gatech.edu), Siddharth Nathella (snathella@gatech.edu), Christoph Nuesslein (cnuesslein3@gatech.edu)
Date: 08/19/2023

This module contains the classes and commands for creating a set
frequency clock within the main while loop of your top level script.
"""

import time


class LoopTimer:
    """Class for creating a simple timed loop manager. This object will attempt to enforece a set frequency when used in a looped script.
    NOTE: this frequency cannot be guaranteed, and the actual frequency should be recorded if this is important for your application. Please
    see the benchmarks for expected maximum performance.

    Example:
        .. code-block:: python

            
            from epicpower.utils.clocking import LoopTimer
            looper = LoopTimer(operating_rate=200)

            while True:
                if looper.continue_loop():
                    # do something every 5ms
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

class TimedLoop():
    def __init__(self, rate: float, err_tol: float=0.25, verbose: bool=False):
        """Class for creating a simple timed loop. This object will attempt to enforce a set frequency, using a deadline scheduling approach.
        Some example of other implementations of this is the ROS1 Rate::sleep function. You can manually call done() to break the loop.

        Args:
            rate (float): The desired operating frequency in Hz.
            err_tol (float, optional): The proportion tolerance for which the object will consider the loop "out of rate". Defaults to 0.1.
            verbose (bool, optional): If True, warnings will be periodically printed to the terminal . Defaults to False.
        """
        self.rate = rate
        self.err_tol = err_tol

        self.verbose = verbose
        self.period = 1 / rate # Expected cycle time in seconds
        self.sched_start = time.perf_counter()  # Start time of the loop

        self.error_limit = (1 + err_tol) * self.period  # Error limit for the loop cycle time

        self.is_slow = False  # Flag to indicate if the loop is running late
        self.true_duration = 0  # Actual time taken for the loop cycle
        self._avg_rate = rate

        self._real_start = self.sched_start
        self.done = False  # Flag to indicate if the loop should stop

    def done(self):
        """Releases the loop timer, allowing the loop to break. Next __call__ will return False"""
        self.done = True

    def __call__(self):
        """Checks if the loop should continue based on the current time and the desired rate, sleeping if necessary to maintain the rate.
        Returns:
            float | bool: The current time if the loop continues or False if the loop is done
        """
        if self.done: return False

        prev_start = self._real_start  # Store the previous start time for avg rate calculation

        desired_end = self.sched_start + self.period
        current_time = time.perf_counter()

        self.true_duration = current_time - self.sched_start

        self.sched_start = desired_end # Reset the loop such that the next loop attempts to keep the whole schedule on track
        self.is_slow = self.true_duration > self.error_limit

        # Sleep or return early if the loop is running late
        if current_time >= desired_end:
            if self.is_slow : self.sched_start = current_time  # Reset the loop start time to current time if running late
            return time.perf_counter()

        time.sleep(desired_end - current_time)  
        # print(f'sleep duraition: {desired_end - current_time:.6f} seconds')
        if self.verbose and self.is_slow:
            print(f"WARNING: Loop is running late! Expected {self.period*1000:.3f} ms, actual {self.true_duration*1000:.3f} ms")
    
        self._real_start = time.perf_counter()  # Update the real loop start time for average rate calculation
        self._avg_rate = 0.99*self._avg_rate + 0.01*(1 / (self._real_start - prev_start))

        return time.perf_counter()

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
    # print("===Testing LoopTimer at 2Hz for 10 seconds===")
    # looper = LoopTimer(2, verbose=True)
    # t0 = time.perf_counter()
    # while time.perf_counter() - t0 < 10:
    #     if looper.continue_loop():
    #         print(time.perf_counter()-t0)

    # print("===timed_loop at 2Hz for 10 seconds in for loop===")
    # for i in timed_loop(operating_rate=2, total_time=10):
    #     print(i)

    # print("===timed_loop at 2Hz for 10 seconds in while loop===")
    # looper = timed_loop(operating_rate=2, total_time=10)
    # while looper():
    #     print(looper.prev_iter)

    print("===Testing TimedLoop at 200Hz for 5 seconds===")
    looper = TimedLoop(1000, verbose=True)
    print(looper.period, looper.error_limit)
    times = []
    tog = time.perf_counter()
    while myt := looper():
        print(looper._avg_rate)
        times.append(myt)
        if len(times) > 1000:
            break

    # Calculate the average loop time
    times = [times[i] - times[i-1] for i in range(1, len(times))]
    print(times[0:10])
    print(f"Average loop time: {sum(times)/len(times)*1000:.6f} ms")
    print(f"Average loop rate: {1/(sum(times)/len(times)):.2f} Hz")
    print(f"Total time: {time.perf_counter() - tog:.6f} seconds")
