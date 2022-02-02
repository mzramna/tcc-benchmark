import time
#from time import TimerError
class Timer:

    def __init__(self):

        self._start_time = None


    def inicio(self):

        """Start a new timer"""

        if self._start_time is not None:

            raise TimerError(f"Timer is running. Use .stop() to stop it")


        self._start_time = time.perf_counter()


    def fim(self,print_=False):

        """Stop the timer, and report the elapsed time"""

        if self._start_time is None:

            raise TimerError(f"Timer is not running. Use .start() to start it")


        elapsed_time = time.perf_counter() - self._start_time

        self._start_time = None
        if print_:
            print(f"Elapsed time: {elapsed_time:0.4f} seconds")
        return float(f"{elapsed_time:0.6f}")
