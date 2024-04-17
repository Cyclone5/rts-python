import time


# ---------------------------------------------------------
# Alkim GOKCEN, University of Izmir Katip Celebi
# Control Systems Lab - PhD.
# alkim.gokcen@outlook.com
# --------------------------------------------------------
# This code is to provide tic() and toc() built-in 
# timer functions in MATLAB. 
# ---------------------------------------------------------
#                          EXPLANATION
# - tic() function gets the current system time
# - toc() functions gets the time difference between
#   tic() and toc() (Elapsed Time between tic-toc)
# - delay(delayTime) function stops the program counter
#   for a given delayTime value in seconds.
# ---------------------------------------------------------

def high_precision_sleep(duration):
    start_time = time.perf_counter()
    while True:
        elapsed_time = time.perf_counter() - start_time
        remaining_time = duration - elapsed_time
        if remaining_time <= 0:
            break
        if remaining_time > 0.02:  # Sleep for 5ms if remaining time is greater
            time.sleep(max(remaining_time / 2, 0.0001))  # Sleep for the remaining time or minimum sleep interval
        else:
            pass


class TimerTicToc:

    def __init__(self):
        self.ticStartTime = 0

    def tic(self):
        self.ticStartTime = time.perf_counter()

    def toc(self):
        return time.perf_counter() - self.ticStartTime

    @staticmethod
    def delay(delay_time):
        high_precision_sleep(delay_time)
        # time.sleep(delayTime)
