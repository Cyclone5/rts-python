# TODO LIST
# - Pythonic şekilde yazılacak.
# - Pacerda bulunan stateler override edilmeye uygun yazılacak. (def haline getirilecek)

from timer_tic_toc import TIMER_TIC_TOC as timer
from serial import Serial
from typing import Optional
from enum import Enum
import time

timerForLooping = timer()  # to compute elapsed time for a process.
timerForWholeProcess = timer()  # to compute elapsed time for all state machine algorithm.

# define the necessary states for state-machine pacer
INIT = 0
PROCESS = 1
UPDATE = 2
WAIT = 3
FINISH = 4
END = 5
OVERRUN = 6
SERIAL = 7


class SerialStore(int, Enum):
    LIST = 0
    SINGLE_VALUE = 1


# ---------------------------------------------------------
# Alkim GOKCEN, University of Izmir Katip Celebi
# Control Systems Lab - PhD.
# alkim.gokcen@outlook.com
# --------------------------------------------------------
# This code is to provide a script-based
# simulink-like simulation environment.
# ---------------------------------------------------------
#                          EXPLANATION
# - A real-time pacer is implemented to force the
#   simulation run in real-time.
# - Usage: Real Time Pacer computes the necessary length
#   of iteration for the given parameters by calculatin
#   the (SimulationTime / SamplingTime)
#   i.e. SimulationTime = 10 sec, SamplingTime = 0.01
# - "OVERRUN case":
#   If an iteration execution time (elapsedTime) exceeds
#   the samplingTime, iteration counter is increased by
#   a value of  ceil((executionTime / samplingTime)) which
#   defines that how many iteration it took the execute
#   the simulation. In such cases, program displays an
#   error message to user to increase the sampling time
#   i.e. Please increase your samplingTime
#        Smaller sampling frequency
# ---------------------------------------------------------

class REAL_TIME_PACER:
    # Variable          Definition                                             Defaults
    # ==============    ==================================================     ============================
    # externalFunction  => process function as an argument of the class.
    # SimulationTime    => defines the simulation duration in seconds.         (Default = 1 seconds)
    # samplingTime      => defines the sampling period for solver in seconds.  (Default = 0.01 seconds)
    # =====================================================================================================
    def __init__(self, externalFunction,
                 simulationTime=1,
                 samplingTime=1e-2,
                 serial_port=None,
                 serial_baudrate=9600,
                 serial_delay=0.1,
                 serial_timeout=15,
                 serial_value_mode: Optional[SerialStore] = SerialStore.SINGLE_VALUE):

        self.SoftwareVersion = "1.0.0"  # manipulate only when stable versions are changed!

        if simulationTime <= 0:
            print("Simulation time must be positive!")
            return

        if samplingTime <= 0:
            print("Sampling period must be positive!")

        self.serial_connection: Optional[Serial] = None
        if serial_port is not None:
            self.serial_connection = Serial(serial_port, serial_baudrate)

        self.serial_value_mode = serial_value_mode
        self.serial_values = []
        self.serial_timeout = serial_timeout
        self.serial_delay = serial_delay

        # assign the externally defined process function to self object.
        self.processFunction = externalFunction
        self.simulationTime = simulationTime
        self.samplingTime = samplingTime
        self.INITIALIZATION = INIT
        self.PROCESS = PROCESS
        self.UPDATE = UPDATE
        self.WAIT = WAIT
        self.FINISH = FINISH
        self.OVERRUN = OVERRUN
        self.SERIAL = SERIAL

        # Initialization phase starts
        STATE = INIT

    def getSoftwareVersion(self):  # to get sofware version
        return self.SoftwareVersion

    def Pacer(self, STATE):

        match STATE:

            case self.INITIALIZATION:
                # compute the necessary iterion number to complete the simulation
                self.sampleLength = self.simulationTime / self.samplingTime
                # initialize the timer vars
                self.processCounter = 0  # defines the iteration counter
                self.elapsedTime = 0  # defines the elapsed time during the process.
                self.waitTime = 0  # defines the remaining time to reach the sampling time.
                self.totalRunTime = 0  # defines the total executed time (wait time is not included)
                self.totalSimulatedTime = 0  # defines the total simulation time including NOPs.
                self.overrunCounter = 0  # defines the total iteration number where the overrun occurs.
                self.overrunCases = 0  # defines the how many loops are over-runed

                STATE = PROCESS  # start the process.
                timerForWholeProcess.tic()  # start the timer after initialization is performed.
                return STATE

            case self.PROCESS:
                # start the timer
                timerForLooping.tic()
                # run the process function
                self.processFunction()
                # stop the timer
                self.elapsedTime = timerForLooping.toc()
                print("Elapsed Time: ", self.elapsedTime, " seconds.")
                if self.elapsedTime <= self.samplingTime:
                    self.processCounter += 1
                    self.waitTime = self.samplingTime - self.elapsedTime
                    STATE = WAIT
                    # print("1")
                elif self.elapsedTime > self.samplingTime:
                    print("OVERRUN case occured!")
                    self.overrunCases = self.elapsedTime % self.samplingTime  # how many cycle is passed in an ovverrun case
                    self.overrunCounter += 1
                    # overrunCounter ve processCounter sayımı hakkında bilgim yok. https://prnt.sc/gwf0Igmq6ELq
                    STATE = OVERRUN
                    # print("2")
                return STATE

            case self.UPDATE:
                # update the simulation related parameters
                self.totalRunTime = self.totalRunTime + self.elapsedTime  # total run time is integrated.
                # Parameters are updated. Detect if the simulation is over

                # if simulation is over
                if self.processCounter >= self.sampleLength:
                    STATE = FINISH
                else:
                    # if simulation should continue
                    STATE = PROCESS
                return STATE

            case self.WAIT:
                # print(str(self.waitTime) + " koyduğum bu değer wait time")
                # @TODO: do not forget to take precautions for OVERRUN cases.
                # For that cases, update the necessary iteration number by an appropriate number
                # i.e. if the execution time is 0.245 seconds, and sampling time is 0.1 seconds,
                # program should wait 0.055 seconds for the next iteration, and elpasedIteration
                # should be increased by 3 = ceil((executionTime / samplingTime)),
                # and return a warning message
                timerForLooping.delay(self.waitTime)  # wait for the t(n+1) - t(n) is elapsed.
                # wait process is done!, now it is time to update simulation parameters
                STATE = UPDATE
                return STATE

            case self.OVERRUN:
                self.waitTime = self.samplingTime - (self.elapsedTime % self.samplingTime)

                # process counter is increased (-1 is employed to remove the increment n PROCESS state).
                # self.processCounter += self.overrunCases - 1
                self.processCounter += (self.elapsedTime // self.samplingTime) + 1

                # define the state.
                STATE = WAIT

                return STATE

            case self.SERIAL:
                if self.serial_connection is None:
                    raise RuntimeError("Serial connection is not initialized!")
                if self.serial_connection.is_open is False:
                    raise RuntimeError("Serial connection is not open!")
                start_time = time.time()
                while True:
                    if self.serial_connection.in_waiting > 0:
                        data = self.serial_connection.readline().decode().strip()
                        if self.serial_value_mode is SerialStore.LIST:
                            self.serial_values.append(data)
                        elif self.serial_value_mode is SerialStore.SINGLE_VALUE:
                            self.serial_values.clear()
                            self.serial_values.append(data)
                        break
                    if time.time() - start_time > self.serial_timeout:
                        raise TimeoutError("Serial connection timeout! ({} seconds)".format(self.serial_timeout))
                    time.sleep(self.serial_delay)

            case self.FINISH:
                self.totalSimulatedTime = timerForWholeProcess.toc()
                print("============================================================================")
                print(" => Simulation is over!")
                # Output the simulation related parameters
                print(" => Total simulated time: ", self.totalSimulatedTime, " seconds.")
                print(" => Total Run Time: ", self.totalRunTime, " seconds.")
                print(" => Total iteration that process is run: ", self.processCounter, " iterations")
                print(" => # of iteration that Overrun detected: ", self.overrunCounter, " iterations")
                print("============================================================================")
                STATE = END
                return STATE

            case _:
                pass

    def pacerDriver(self):
        # this function is employed to run pacer state machine.
        stateInLoop = INIT
        while True:

            stateInLoop = self.Pacer(stateInLoop)  # loop the paceer with state
            if stateInLoop is END:
                break  # leave the pacer.
