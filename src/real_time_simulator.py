# 02.01.2024
# - iterasyonlar arası kod yazabileceği bir yapı haline getireceğim while yerine for koyup istediği kadar ilerletip sonra bekletme yapısı
# for debug mode logging libary

from serial import Serial
from typing import Optional, List

from src.timertictoc import TimerTicToc as Timer
from src.schemas import PacerState, SerialStore, PacerPoint, PacerFunction, Plots

timerForLooping = Timer()  # to compute elapsed time for a process.
timerForWholeProcess = Timer()  # to compute elapsed time for all state machine algorithm.


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

class RealTimePacer:
    # Variable          Definition                                             Defaults
    # ==============    ==================================================     ============================
    # externalFunction  => process function as an argument of the class.
    # SimulationTime    => defines the simulaStion duration in seconds.         (Default = 1 seconds)
    # samplingTime      => defines the sampling period for solver in seconds.  (Default = 0.01 seconds)
    # =====================================================================================================
    def __init__(self,
                 external_function,
                 simulation_time=1,
                 sampling_time=1e-2,
                 pacer_added_function: Optional[List[PacerFunction]] = None,
                 serial_port=None,
                 serial_baudrate=9600,
                 serial_delay=0.1,
                 serial_timeout=15,
                 serial_value_mode: Optional[SerialStore] = SerialStore.LIST,
                 serial_read_wish="READ\n"
                 ):

        if simulation_time <= 0:
            raise ValueError("Simulation time must be positive!")

        if sampling_time <= 0:
            raise ValueError("Sampling time must be positive!")

        # Serial Init

        self.serial_timeout = serial_timeout
        self.serial_connection: Optional[Serial] = None
        if serial_port is not None:
            self.serial_connection = Serial(serial_port, serial_baudrate, timeout=self.serial_timeout)

        self.serial_value_mode = serial_value_mode
        self.serial_values = []
        # self.serial_delay = serial_delay
        self.serial_read_wish = self._take_bytes(serial_read_wish)

        # Pacer History, Plots
        self.pacer_history = PacerHistory()
        self.plots = Plots()

        # Pacer Added Functions
        self.pacer_functions = pacer_added_function

        # assign the externally defined process function to self object.
        self.processFunction = external_function
        self.simulationTime = simulation_time
        self.samplingTime = sampling_time
        self.INITIALIZATION = PacerState.INIT
        self.PROCESS = PacerState.PROCESS
        self.UPDATE = PacerState.UPDATE
        self.WAIT = PacerState.WAIT
        self.FINISH = PacerState.FINISH
        self.OVERRUN = PacerState.OVERRUN
        self.SERIAL = PacerState.SERIAL

        self.sampleLength = self.simulationTime / self.samplingTime
        # initialize the timer vars
        self.processCounter = 0  # defines the iteration counter
        self.elapsedTime = 0  # defines the elapsed time during the process.
        self.waitTime = 0  # defines the remaining time to reach the sampling time.
        self.totalRunTime = 0  # defines the total executed time (wait time is not included)
        self.totalSimulatedTime = 0  # defines the total simulation time including NOPs.
        self.overrunCounter = 0  # defines the total iteration number where the overrun occurs.
        self.overrunCases = 0  # defines the how many loops are over-runed

    def Pacer(self, state):

        match state:

            case self.INITIALIZATION:
                return self.pacer_init()

            case self.PROCESS:
                return self.pacer_process()

            case self.WAIT:
                return self.pacer_wait()

            case self.OVERRUN:
                return self.pacer_overrun()

            case self.UPDATE:
                return self.pacer_update()

            case self.SERIAL:
                return self.pacer_serial()

            case self.FINISH:
                return self.pacer_finish()

            case _:
                pass

    def pacer_init(self):
        if self.serial_connection is None:
            state = PacerState.PROCESS  # start the process.
        else:
            state = PacerState.SERIAL
        timerForWholeProcess.tic()  # start the timer after initialization is performed.
        return state

    def pacer_process(self):
        # start the timer
        timerForLooping.tic()
        # run the process function
        self.processFunction()
        # stop the timer
        self.elapsedTime = timerForLooping.toc()
        print("Elapsed Time: ", self.elapsedTime, " seconds.")
        state = None
        if self.elapsedTime <= self.samplingTime:
            self.processCounter += 1
            self.waitTime = self.samplingTime - self.elapsedTime
            state = PacerState.WAIT
            # print("1")
        elif self.elapsedTime > self.samplingTime:
            print("OVERRUN case occured!")
            self.overrunCases = self.elapsedTime % self.samplingTime
            # how many cycle is passed in an ovverrun case
            self.overrunCounter += 1
            # overrunCounter ve processCounter sayımı hakkında bilgim yok. https://prnt.sc/gwf0Igmq6ELq
            state = PacerState.OVERRUN
            # print("2")
        if state is None:
            raise RuntimeError("State is None in process!")
        return state

    def pacer_update(self):
        # update the simulation related parameters
        self.totalRunTime = self.totalRunTime + self.elapsedTime  # total run time is integrated.
        # Parameters are updated. Detect if the simulation is over

        # if simulation is over
        if self.processCounter >= self.sampleLength:
            state = PacerState.FINISH
        else:
            # if simulation should continue
            if self.serial_connection is None:
                state = PacerState.PROCESS
            else:
                state = PacerState.SERIAL
        return state

    def pacer_wait(self):
        # print(str(self.waitTime) + " koyduğum bu değer wait time")
        # @TODO: do not forget to take precautions for OVERRUN cases.
        # For that cases, update the necessary iteration number by an appropriate number
        # i.e. if the execution time is 0.245 seconds, and sampling time is 0.1 seconds,
        # program should wait 0.055 seconds for the next iteration, and elpasedIteration
        # should be increased by 3 = ceil((executionTime / samplingTime)),
        # and return a warning message
        timerForLooping.delay(self.waitTime)  # wait for the t(n+1) - t(n) is elapsed.
        # wait process is done!, now it is time to update simulation parameters
        state = PacerState.UPDATE
        return state

    def pacer_overrun(self):
        self.waitTime = self.samplingTime - (self.elapsedTime % self.samplingTime)

        # process counter is increased (-1 is employed to remove the increment n PROCESS state).
        # self.processCounter += self.overrunCases - 1
        self.processCounter += (self.elapsedTime // self.samplingTime) + 1

        # define the state.
        state = PacerState.WAIT

        return state

    def pacer_serial(self):
        if self.serial_connection is None:
            raise RuntimeError("Serial connection is not initialized!")
        if self.serial_connection.is_open is False:
            raise RuntimeError("Serial connection is not open!")
        self.serial_connection.write(self.serial_read_wish)
        data = self.serial_connection.readline()
        if data == b'':
            raise TimeoutError("Serial connection timeout! ({} seconds)".format(self.serial_timeout))
        if self.serial_value_mode == SerialStore.LIST:
            self.serial_values.append(data)
        elif self.serial_value_mode == SerialStore.SINGLE_VALUE:
            self.serial_values.clear()
            self.serial_values.append(data)

        state = PacerState.PROCESS
        return state

    def pacer_finish(self):
        self.totalSimulatedTime = timerForWholeProcess.toc()
        print("============================================================================")
        print(" => Simulation is over!")
        # Output the simulation related parameters
        print(" => Total simulated time: ", self.totalSimulatedTime, " seconds.")
        print(" => Total Run Time: ", self.totalRunTime, " seconds.")
        print(" => Total iteration that process is run: ", self.processCounter, " iterations")
        print(" => # of iteration that Overrun detected: ", self.overrunCounter, " iterations")
        print("============================================================================")
        state = PacerState.END
        return state

    def append_pacer_history(self, state: PacerState):
        self.pacer_history.append(state)

    @staticmethod
    def _take_bytes(data):
        if isinstance(data, str):
            return bytes(data, 'utf-8')
        elif isinstance(data, int):
            return data.to_bytes(2, byteorder='big')
        elif isinstance(data, bytes):
            return data

    @property
    def serial_values(self):
        if self.serial_value_mode == SerialStore.LIST:
            return self._serial_values
        elif self.serial_value_mode == SerialStore.SINGLE_VALUE:
            # if it has first element, return it, otherwise return None
            if self._serial_values:
                return self._serial_values[0]
            else:
                return []

    @serial_values.setter
    def serial_values(self, value):
        self._serial_values = value

    def send_serial(self, data):
        if self.serial_connection is None:
            raise RuntimeError("Serial connection is not initialized!")
        if self.serial_connection.is_open is False:
            raise RuntimeError("Serial connection is not open!")
        self.serial_connection.write(self._take_bytes(data))

    def pacer_point(self, state: PacerState, mode: PacerPoint):
        if self.pacer_functions is None:
            return  # if there is no pacer function, return.
        for f in self.pacer_functions:
            if f.state == state and f.mode == mode:
                f.function(*f.args, **f.kwargs)

    def pacer_driver(self):
        # this function is employed to run pacer state machine.
        state_in_loop = PacerState.INIT
        while True:
            current_state = state_in_loop  # eğer bu olmazsa afterda problem olur
            self.pacer_history.append(current_state)
            self.pacer_point(current_state, PacerPoint.BEFORE)
            state_in_loop = self.Pacer(state_in_loop)  # loop the pacer with state
            self.pacer_point(current_state, PacerPoint.AFTER)
            if state_in_loop is PacerState.END:
                break  # leave the pacer.


class PacerHistory:

    def __init__(self):
        self.histories = []

    def append(self, state: PacerState):
        self.histories.append(state)

    def __str__(self):
        if not self.histories:
            return "Histories are empty."
        else:
            history_str = "Pacer History:\n"
            for index, state in enumerate(self.histories, start=1):
                history_str += f"Step {index}: {state.state}\n"
            return history_str

    def __call__(self, *args, **kwargs):
        pass
