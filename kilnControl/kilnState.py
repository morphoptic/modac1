# kilnState
#####################
from enum import Enum
class KilnState(Enum):
    '''States of the KilnProcess internal to LeicaDisto Module'''
    Closed = 0 # before start and when done w no error
    Error = -1 # done and error occured
    Starting = 1 # between closed and open
    Idle = 2 # waiting for command
    Heating = 3 # heaters on ramping up
    Holding = 4 # heaters may be on or off to hold
    Cooling = 5 # heaters off, fans on
    EndRun = 6 # run is over, temp back to start. Hold this for Nsec
    


