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
class TIMER_TIC_TOC:

    def __init__(self):
        self.ticStartTime = 0

    def tic(self):  # initialize the timer start point
        self.ticStartTime = time.time()

    def toc(self):  # computes the elapsed time between tic() and toc()
        return time.time() - self.ticStartTime

    def delay(self, delayTime):
        time.sleep(delayTime)
