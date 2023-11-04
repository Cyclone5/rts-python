import time
import matplotlib.pyplot as plt

import serial
from src.timer_tic_toc import TIMER_TIC_TOC as timer

time_control = timer()

class CSerial:
    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate)

    def write(self, data):
        self.ser.write(data)

    def read(self):
        return self.ser.read()

    def close(self):
        self.ser.close()

    def __call__(self, *args, **kwargs) -> serial.Serial:
        return self.ser


ser2 = serial.Serial('COM5', 115200)
time_control.tic()
ser2.write(b'PING')
print("ok")
print(ser2.readline())
print(time_control.toc())
ser2.write(b'PING')
print(ser2.readline())
