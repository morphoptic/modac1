# kilnScript
# when Kiln Controller is in ACTIVE State,
# follows a script, checking its state every N seconds
# each iteration of the Control Loop
#   gets the current status
#   compares with values in the current Script Segment
#   moves the Script and Controller state machines
#

#import sys
#this = sys.modules[__name__]
#import logging, logging.handlers, traceback
#log = logging.getLogger(__name__)
#log.setLevel(logging.DEBUG)
#
#import time
#import datetime
#

from .kilnState import KilnState, KilnScriptState
#from .kiln import  kilnInstance

def parseKilnScript(params):
    # JSON converted to dictionary
# { kilnScript
# }
#
    simulate = params[keyForSimulate()]
    # moHardware tells kTypes to simulate values and Kiln to use sim processing
    moHardware.simulateKiln(simulate)
    targetT = params[keyForTargetTemp()]
    displacement = params[keyForTargetDisplacement()]
    maxTime = params[keyForMaxTime()]
    timeStep = params[keyForTimeStep()]
    holdTime = params[keyForKilnHoldTime()]

    kilnInstance.startScript(targetT, displacement, maxTime, timeStep, holdTime)

class KilnScriptSegment:
    stepIdx = -1 # index into Script[], maybe
    
    # these are parameters you can program
    targetTemperature = 0 # deg C; temp the kiln should reach in this segment
    targetDistanceChange = 0 # if <=0 then ignore distance
    holdTimeMinutes = 0 # minutes to hold once targetTemperature is reached
    exhaustFan = 0 # off or on
    supportFan = 0 # off or on
    
    # these are locals for running the script
    segmentState = KilnScriptState.NoScriptStep
    holdTimeSeconds = holdTimeMinutes * 60
    segmentStartTime = 0 #datetime.time.now() # when this segment started
    runTimeSeconds = 0  # how long this segment has been running
    holdStartTime = 0 # datetime.time.now() when hold starts
    
    def doIteration(self):
        '''handle one iteration of the segment'''
        #   gets the current status
        #   compares with values in the current Script Segment
        #   moves the Script and Controller state machines
        pass

    def getStatus(self):
        # get temp, distance, update times
        pass


