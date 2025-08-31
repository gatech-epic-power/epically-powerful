import threading
import time
import random

class MultiThreadWorker:
    def __init__(self):
        self._stop_event = threading.Event()
        self._threads = []
        self._lock = threading.Lock()

        # Shared class variables (updated by individual threads)
        self.task_one_counter = 0
        self.task_two_value = 0.0


    def start(self):
        self._start_thread(self.task_one)
        self._start_thread(self.task_two)


    def _start_thread(self, target):
        thread = threading.Thread(target=self._run_continuously, args=(target,))
        thread.daemon = True
        thread.start()
        self._threads.append(thread)


    def _run_continuously(self, task):
        while not self._stop_event.is_set():
            task()
            time.sleep(1)  # Delay between iterations


    def stop(self):
        self._stop_event.set()
        for thread in self._threads:
            thread.join()


    # === Task 1: Increment a counter ===
    def task_one(self):
        with self._lock:
            self.task_one_counter += 1
            print(f"[Task One] Counter: {self.task_one_counter}")


    # === Task 2: Simulate a sensor reading update ===
    def task_two(self):
        with self._lock:
            self.task_two_value = random.uniform(0.0, 100.0)
            print(f"[Task Two] New Sensor Value: {self.task_two_value:.2f}")


if __name__ == "__main__":
    worker = MultiThreadWorker()
    worker.start()

    try:
        for _ in range(5):
            time.sleep(2)
            # Read shared variables safely
            with worker._lock:
                print(f"[Main] Counter: {worker.task_one_counter}, Sensor: {worker.task_two_value:.2f}")
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping worker threads...")
        worker.stop()
