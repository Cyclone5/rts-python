# Test1
# kodumuzun ilk hali

from src.real_time_simulator import RealTimePacer as RTP
from src.real_time_simulator import SerialStore

import time
from simple_pid import PID

i = 0

counters = []
pid_setpoint = 2000
pid = PID(1, 0.025, 0.0025, setpoint=pid_setpoint)

# define the process as external function
def someFunction():  # temporary function to mimic the env. to simulate.
    global i
    global counters
    global pid
    counter = int.from_bytes(rtp.serial_values[i].replace(b'\n', b''), byteorder='big')
    counters.append(counter)
    u = pid(counter)
    print("c ", counter)
    print("u ", u)
    if u > 0:
        rtp.send_serial("DF")
    elif u < 0:
        rtp.send_serial("DB")

    rtp.send_serial("S")
    u = abs(u)
    if abs(pid_setpoint - counter) < 10:
        rtp.send_serial(0)
    else:
        if u > 1000:
            rtp.send_serial(40)
        elif 40 < u < 1000:
            rtp.send_serial(int(u / 20))

    i += 1
    rtp.send_serial("\n")


SIMULATION_TIME = 600  # seconds
SAMPLING_PERIOD = 0.2  # seconds
rtp = RTP(someFunction, SIMULATION_TIME, SAMPLING_PERIOD,
          serial_port='COM3', serial_baudrate=115200)

from src.real_time_simulator import PacerFunction, PacerState


def giveMax():
    print("k")


def finish_pwm():
    rtp.send_serial("NNS")
    rtp.send_serial(0)
    rtp.send_serial("\n")


rtp.pacer_functions = [
    PacerFunction(state=PacerState.INIT, mode=1, function=giveMax),
    PacerFunction(state=PacerState.FINISH, mode=0, function=finish_pwm)
]
rtp.pacer_driver()
