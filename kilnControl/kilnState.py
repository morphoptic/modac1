# kilnState - enum of kiln control state machine
# two Enum to define the primary kiln control state and script state
#
# KilnState is of outer KilnControlProcess thread
# KilnScriptState is for script processing of one step
#####################
from enum import Enum

class KilnState(Enum):
    '''States of the KilnProcess internal to LeicaDisto Module'''
    Closed = 0 # before start and when done w no error
    Error = -1 # done and error occured
    Starting = 1 # between closed and open
    Idle = 2 # waiting for command
    RunningScript = 3

class KilnScriptState(Enum):
    NoScriptStep = 0
    Heating = 1 # heaters on ramping up
    Holding = 2 # heaters may be on or off to hold
    Cooling = 3 # heaters off, fans on
    EndRun = 10 # run is over, temp back to start. Hold this for Nsec
    


