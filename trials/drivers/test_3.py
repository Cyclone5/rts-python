# Test3
# Buranın içerisinde com bağlantı olmadan basit testlerimizden olan simülasyon periyoda yetmiyorsa sorunu çözümü için
# parametre mi ekleyeceğiz rtpye vb.

import time

from src.real_time_simulator import RealTimePacer as RTP


# define the process as external function
def someFunction():  # temporary function to mimic the env. to simulate.
    time.sleep(1)
    print("I am a function that takes 1 second to execute.")
    rtp.execute_finish(finish_counter=0)


SIMULATION_TIME = 6  # seconds
SAMPLING_PERIOD = 2  # seconds
rtp = RTP(someFunction, SIMULATION_TIME, SAMPLING_PERIOD)
rtp.pacer_driver()
