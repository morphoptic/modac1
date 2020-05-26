# testEnum - using kilnState - enum of kiln control state machine
# two Enum to define the primary kiln control state and script state
#
# KilnState is of outer KilnControlProcess thread
# KilnScriptState is for script processing of one step
#####################
from enum import Enum

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
# other system imports
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

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


if __name__ == "__main__":
    print("Testing Enums")
    numKilnStates = len(KilnState)
    print("Kiln state size: ", numKilnStates)
    for s in KilnState:
        print("   kiln state name: ", s.name, " value: ", s.value )
    print("")

    numKilnScriptStates = len(KilnScriptState)
    print("Kiln script state size: ", numKilnScriptStates)
    for s in KilnScriptState:
        print("   script state name: ", s.name, " value: ", s.value )
    print("")

    s = KilnScriptState.Holding
    print("should be Holding state name: ", s.name, " value: ", s.value)
    sname = s.name
    v = KilnScriptState[sname]
    print("also should be Holding state name: ", v.name, " value: ", v.value)

    def keyForHolding(): return "Holding"

    sname = keyForHolding()
    v = KilnScriptState[sname]
    print("this too         state name: ", v.name, " value: ", v.value)

    state = KilnState.Closed
    stateName = state.name
    print("state should be close : ", repr(state),state.name, stateName)
    #this works using square brackets
    dupeState = KilnState[stateName]
    # but function method doesnt
    dupState = KilnState(stateName)





