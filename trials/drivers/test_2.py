# Test2
# bu counta geldiği zaman durmasını sağlamaya çalışıyoruz.
# Bilinen Problemler: verilerin bazıları uarttan 0 geliyor.

from src.real_time_simulator import RealTimePacer as RTP
from src.real_time_simulator import SerialStore
from src.real_time_simulator import PacerFunction, PacerState

import time
from simple_pid import PID

i = 0

counters = []
pid_setpoint = 3452
pid = PID(1, 0.025, 0.0, setpoint=pid_setpoint)


# define the process as external function
def someFunction():  # temporary function to mimic the env. to simulate.
    time.sleep(1)  # @TODO implement this in rts.py
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
            rtp.send_serial(100)
        elif 40 < u < 1000:
            rtp.send_serial(int(u / 20))

    i += 1
    rtp.send_serial("\n")


SIMULATION_TIME = 20  # seconds
SAMPLING_PERIOD = 1.5  # seconds
rtp = RTP(someFunction, SIMULATION_TIME, SAMPLING_PERIOD,
          serial_port='COM3', serial_baudrate=115200)


def giveMax():
    print("k")


import matplotlib.pyplot as plt


def finish_pwm():
    global counters
    rtp.send_serial("NNS")
    rtp.send_serial(0)
    rtp.send_serial("\n")
    x_values = range(1, len(counters) + 1)
    plt.plot(x_values, counters, marker='o', linestyle='-')
    j_i = 0
    for j in counters:
        if j == 0:
            print(j_i, rtp.serial_values[j])
        j_i += 1
    plt.xlabel('Index')
    plt.ylabel('Counters')
    plt.title('Graph')
    plt.show()


rtp.pacer_functions = [
    PacerFunction(state=PacerState.INIT, mode=1, function=giveMax),
    PacerFunction(state=PacerState.FINISH, mode=0, function=finish_pwm)
]
rtp.pacer_driver()
