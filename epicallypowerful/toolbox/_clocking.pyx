from libc.time cimport timespec, clock_gettime, CLOCK_MONOTONIC, clock_nanosleep, TIMER_ABSTIME
from libc.stdint cimport int64_t
from libc.stdbool cimport bool

cdef inline int64_t to_nsec(timespec ts):
    return (ts.tv_sec * 1_000_000_000) + ts.tv_nsec

cdef inline timespec to_timespec(int64_t ns):
    cdef timespec ts
    ts.tv_sec = ns // 1_000_000_000
    ts.tv_nsec = ns % 1_000_000_000
    return ts

cdef class TimedLoop:
    cdef int64_t period_ns  # in nanoseconds
    cdef int64_t tol_ns  # in nanoseconds
    cdef timespec now
    cdef timespec sched
    cdef double rate  # in Hz
    cdef double tolerance  # in %
    cdef bool slow

    def __cinit__(self):
        self.period_ns = 0
        self.tol_ns = 0
        self.now = timespec()
        self.sched = timespec()
        self.rate = 0.0
        self.tolerance = 0.0
        self.slow = False
        self.reset()

    def __init__(self, double rate, double tolerance=0.1): # rate in Hz, tolerance in %
        if rate <= 0: raise ValueError("Rate must be greater than 0")
        self.rate = rate
        self.tolerance = tolerance
        self.tol_ns = <int64_t>(1e9 * self.tolerance * self.rate)  # Convert tolerance to nanoseconds
        self.period_ns = <int64_t>(1e9 / self.rate)  # Convert rate to period in nanoseconds

    cdef reset(self): # Reset the loop to start at the current time
        clock_gettime(CLOCK_MONOTONIC, &self.now)
        self.sched = self.now

    cpdef sleep(self):
        self.sched = to_timespec(to_nsec(self.sched) + self.period_ns)
        clock_gettime(CLOCK_MONOTONIC, &self.now)
        
        int64_t now_nsec = to_nsec(self.now)
        int64_t sched_nsec = to_nsec(self.sched)
        self.slow = False

        if now_nsec > sched_nsec:
            if (now_nsec - sched_nsec) > self.tol_ns: # If we're behind by more than the tolerance, we are slow
                self.slow = True

            if (now_nsec > (sched_nsec + self.period_ns)):  # If we're are ahead by a full period, reset the schedule
                self.reset()
            return  # No need to sleep, we're slow

        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &self.sched, NULL)
        return

    cpdef __call__(self): self.sleep()
