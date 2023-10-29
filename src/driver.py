from real_time_simulator import REAL_TIME_PACER as RTP
import time


# define the process as external function
def someFunction():  # temporary function to mimic the env. to simulate.

    time.sleep(0.02)  # assume that the env. process takes 0.1 seconds.


SIMULATION_TIME = 2  # seconds
SAMPLING_PERIOD = 0.05  # seconds
rtp = RTP(someFunction, SIMULATION_TIME, SAMPLING_PERIOD)
rtp.pacerDriver()
