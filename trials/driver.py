from src.real_time_simulator import RealTimePacer as RTP
from src.real_time_simulator import SerialStore

import time
from simple_pid import PID


class Motor:

    def __init__(self):
        self.speed = 50

    def update(self, value):
        pass


motor = Motor()
pid = PID(1, 0.1, 0.05, setpoint=motor.speed)


# define the process as external function
def someFunction():  # temporary function to mimic the env. to simulate.
    print(rtp.serial_values)


SIMULATION_TIME = 10  # seconds
SAMPLING_PERIOD = 4  # seconds
rtp = RTP(someFunction, SIMULATION_TIME, SAMPLING_PERIOD,
          serial_port="COM3", serial_baudrate=115200)
rtp.pacer_driver()
