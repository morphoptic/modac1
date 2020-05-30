# kilnState - enum of kiln control state machine
# two Enum to define the primary kiln control state and script state
#
# KilnState is of outer KilnControlProcess thread
# KilnScriptState is for script processing of one step
#####################
from enum import Enum
from collections import OrderedDict

#### use this to get current and parent directories, and append parent to Python's import path
import sys, os
__dirName__ = os.path.dirname(os.path.abspath(__file__))
__parentDirName__ = os.path.dirname(os.path.abspath(__dirName__))
print("importing " + __dirName__)
print("parentImport " + __parentDirName__)
sys.path.append(__parentDirName__)
#### now we can reference sibling folders

# from modac import moKeys
from modac.moKeys import *
from .kilnConfig import *

class KilnState(Enum):
    '''States of the KilnProcess internal to LeicaDisto Module'''
    Closed = 0  # before start and when done w no error
    Error = -1  # done and error occured
    Starting = 1  # between closed and open
    Idle = 2  # waiting for command
    RunningScript = 3  # running a kiln script
    Unknown = -4


class KilnScriptState(Enum):
    Unknown = -4
    NoScriptStep = 0
    Heating = 1  # in transition, heaters on ramping up or down; exit on temperature reached or Other
    Holding = 2  # in a temperature hold, heaters may be on or off to hold; exit on hold time|dist
    Cooling = 3  # heaters off, fans on 1 # TODO remove this cooling is just negative heating
    EndRun = 10  # run is over, temp back to start. Hold this for Nsec after script ??
    # TODO Cooling script state - supporting and cooling fan control
    # do we have a cooling phase at the end of a script, or really should just reset and Idle
    # may want two process timeSteps;
    # IdleTimeStep for fairly quick response - does nothing but allow async Command to change State (startScript)
    # ScriptTimeStep - 10 sec minimum to keep PID from going crazy

def defaultKilnRuntimeStatus():
    asArray = [  # build w array instead of dict to keep order
        # shared keys - for debug purposes
        # default values set in moData so not dependent on this file
        # record time we collected data
        (keyForTimeStamp(), "default kilnStatus"),
        ("kilnProcessRunnable", False),

        # kiln state
        (keyForState(), KilnState.Unknown.name),
        (keyForKilnScriptState(), KilnState.Unknown.name),
        (keyForSimulate(), False),

        # Script Segment Parameters
        (keyForSegmentIndex(), 0),
        (keyForTargetTemp(), 23),
        (keyForKilnHoldTimeMin(), 1),
        (keyForKilnHoldTimeSec(), 60),
        (keyForTargetDisplacement(), 0),
        (keyForExhaustFan(), False),
        (keyForSupportFan(), False),
        (keyFor12vRelay(), True),
        (keyForPIDStepTime(), 10),
        (keyForMaxTime(), default_maxTime),

        # Script Segment data
        (keyForKilnTimeInHoldSeconds(), 0),
        (keyForKilnTimeInHoldMinutes(), 0),
        (keyForKilnHoldStartTime(), "startHoldTimeStr"),
        (keyForKilnRuntime(), 0),
        (keyForKilnStartTime(), "startTimeStr"),

        (keyForStartDistance(), 0),
        (keyForTargetDisplacement(), 0),

        (keyForCurrentDistance(), 0),
        (keyForCurrentDisplacement(), 0),

        (keyForKilnHeaters(), [False, False, False, False]),
        (keyForKilnHeaterCommanded(), [False, False, False, False]),
        (keyForKilnTemperatures(), [0.0, 0.0, 0.0, 0.0]),

        # (keyForScript(), str(self.myScript)),
    ]
    def_kilnStatus = OrderedDict(asArray)

    return def_kilnStatus

