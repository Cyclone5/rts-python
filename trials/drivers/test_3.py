# Test3
# Buranın içerisinde com bağlantı olmadan basit testlerimizden olan simülasyon periyoda yetmiyorsa sorunu çözümü için
# parametre mi ekleyeceğiz rtpye vb.

import time

from src.real_time_simulator import RealTimePacer as RTP


# define the process as external function
def someFunction():  # temporary function to mimic the env. to simulate.
    time.sleep(2)


SIMULATION_TIME = 6  # seconds
SAMPLING_PERIOD = 5  # seconds
rtp = RTP(someFunction, SIMULATION_TIME, SAMPLING_PERIOD)
rtp.pacer_driver()
