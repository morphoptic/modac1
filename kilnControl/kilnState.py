# kilnState
#####################
from enum import Enum
class KilnState(Enum):
    '''States of the KilnProcess internal to LeicaDisto Module'''
    Closed = 0 # before start and when done w no error
    Error = -1 # done and error occured
    Starting = 1 # between closed and open
    Idle = 2
    Heating = 3
    Holding = 4
    Cooling = 5

