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
    cdef int64_t period_ns  # in nanoseconds
    cdef timespec now
    cdef timespec sched
    cdef double rate  # in Hz

    def __cinit__(self):
        self.period_ns = 0

    def __init__(self, double rate): # rate in Hz
        if rate <= 0: raise ValueError("Rate must be greater than 0")
        self.rate = rate
        self.period_ns = <int64_t>(1e9 / self.rate)  # Convert rate to period in nanoseconds
        reset(self)

    cdef reset(self): # Reset the loop to the current time
        clock_gettime(CLOCK_MONOTONIC, &self.now)
        self.sched = self.now

    cpdef sleep(self):
        self.sched = to_timespec(to_nsec(self.sched) + self.period_ns)
        clock_gettime(CLOCK_MONOTONIC, &self.now)
        
        int64_t now_nsec = to_nsec(self.now)
        int64_t sched_nsec = to_nsec(self.sched)

        if now_nsec > sched_nsec:
            if (now_nsec > (sched_nsec + self.period_ns)):
                # If we're are ahead by a full period, reset the schedule
                self.reset()
            return  # No need to sleep, we're slow
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &self.sched, NULL)

    cpdef __call__(self): self.sleep()
