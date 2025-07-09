from libc.time cimport timespec, clock_gettime, CLOCK_MONOTONIC, clock_nanosleep, TIMER_ABSTIME
from libc.stdint cimport int64_t

cdef inline int64_t to_nsec(timespec ts):
    return (ts.tv_sec * 1_000_000_000) + ts.tv_nsec

cdef inline timespec to_timespec(int64_t ns):
    cdef timespec ts
    ts.tv_sec = ns // 1_000_000_000
    ts.tv_nsec = ns % 1_000_000_000
    return ts

cdef class TimedLoop:
    cdef readonly double rate
    cdef readonly double tolerance
    cdef readonly int64_t period_ns  # in nanoseconds
    cdef readonly int64_t error_limit_ns  # in nanoseconds
    cdef timespec now
    cdef timespec next_tick

    def __cinit__(self):
        self.rate = 0.0
        self.tolerance = 0.0
        self.period_ns = 0
        self.error_limit_ns = 0

    def __init__(self, double rate, double tolerance=0.01): # rate in Hz, tolerance in % period
        if rate <= 0: raise ValueError("Rate must be greater than 0")
        self.rate = rate
        self.tolerance = tolerance
        self.period_ns = <int64_t>(1e9 / self.rate)  # Convert rate to period in nanoseconds
        self.error_limit_ns = <int64_t>(self.tolerance * self.period_ns * 1e9)  # Convert tolerance to nanoseconds

    cpdef sleep2(self): # Sleep until the next tick, adjusting for the period and tolerance, using relative time
        clock_gettime(CLOCK_MONOTONIC, &self.now)
        cdef timespec until = to_timespec(to_nsec(self.next_tick) - to_nsec(self.now))
        clock_nanosleep(CLOCK_MONOTONIC, 0, &until, NULL)
        clock_gettime(CLOCK_MONOTONIC, &self.now)
        self.next_tick = to_timespec(to_nsec(self.now) + self.period_ns)

    cpdef sleep(self): # Sleep until the next tick, adjusting for the period and tolerance, using absolute time
        # Check if we are delayed by a full period
        clock_gettime(CLOCK_MONOTONIC, &self.now)
        if to_nsec(self.now) >= (to_nsec(self.next_tick) + self.period_ns):
            self.next_tick = self.now
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &self.next_tick, NULL)
        clock_gettime(CLOCK_MONOTONIC, &self.now)
        self.next_tick = to_timespec(to_nsec(self.now) + self.period_ns)

