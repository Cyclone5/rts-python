# Test4

from src.real_time_simulator import RealTimePacer as RTP
from src.real_time_simulator import SerialStore
from src.real_time_simulator import PacerFunction, PacerState

import time
from simple_pid import PID

i = 0

counters = []


# define the process as external function
def someFunction():  # temporary function to mimic the env. to simulate.
    # buranın içerisinde sadece counter değerini al kaydet işlem yapma motoru bir kere u verip döndüreceğim
    # counter 0 problemi için kontrol
    time.sleep(0.001)  # @TODO implement this in rts.py
    global i
    global counters
    counter = int.from_bytes(rtp.serial_values[i].replace(b'\n', b''), byteorder='big')
    print(i, counter)
    counters.append(counter)
    i = i + 1



SIMULATION_TIME = 5  # seconds
SAMPLING_PERIOD = 0.1  # seconds
rtp = RTP(someFunction, SIMULATION_TIME, SAMPLING_PERIOD,
          serial_port='COM3', serial_baudrate=115200)


def giveMax():
    rtp.send_serial("DFS")
    rtp.send_serial(50)
    rtp.send_serial("\n")
    time.sleep(0.1)


import matplotlib.pyplot as plt


def finish_pwm():
    global counters
    rtp.send_serial("NNS")
    rtp.send_serial(0)
    rtp.send_serial("\n")
    x_values = range(1, len(counters) + 1)
    plt.plot(x_values, counters, marker='o', linestyle='-')
    for j in counters:
        if j == 0:
            print(rtp.serial_values[j])
    plt.xlabel('Index')
    plt.ylabel('Counters')
    plt.title('Graph')
    plt.show()


rtp.pacer_functions = [
    PacerFunction(state=PacerState.INIT, mode=1, function=giveMax),
    PacerFunction(state=PacerState.FINISH, mode=0, function=finish_pwm)
]
rtp.pacer_driver()
