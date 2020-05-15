# kilnState - enum of kiln control state machine
# two Enum to define the primary kiln control state and script state
#
# KilnState is of outer KilnControlProcess thread
# KilnScriptState is for script processing of one step
#####################
from enum import Enum

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

class KilnState(Enum):
    '''States of the KilnProcess internal to LeicaDisto Module'''
    Closed = 0  # before start and when done w no error
    Error = -1  # done and error occured
    Starting = 1  # between closed and open
    Idle = 2  # waiting for command
    RunningScript = 3  # running a kiln script


class KilnScriptState(Enum):
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
    def_kilnStatus = {
        keyForTimeStamp(): "none yet",
        keyForState(): 'Closed',
        keyForPIDStepTime(): 10,
        keyForKilnRuntime(): 0,
        keyForKilnTemperatures(): [0.0, 0.0, 0.0, 0.0],
        keyForKilnHeaters(): [False, False, False, False],
        keyForKilnHeaterCommanded(): [False, False, False, False],
        keyForScript(): [], # collection of script segments


        keyForTargetTemp(): 0,
        KilnStartTime(): "Not Started",
        keyForTargetDisplacement(): -1,
        keyForMaxTime(): 0,
        keyForStartDistance(): 0,
        keyForCurrentDisplacement(): 0,
        keyForKilnHoldTime(): 0,
        keyForKilnTimeInHoldMinutes(): 0,
    }
    return def_kilnStatus

