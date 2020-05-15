# kilnScript
# when Kiln Controller is in ACTIVE State (RunningScript)
# follows a script, checking its state every N seconds
# each iteration of the Control Loop
#   gets the current status
#   compares with values in the current Script Segment
#   moves the Script and Controller state machines
#

import sys
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#
import time
import datetime, json
#
from modac.moKeys import *
from .kilnConfig import *

# JSON converted to dictionary
# { kilnScript
# }
#


from .kilnState import KilnState, KilnScriptState
#from .kiln import  kilnInstance

    # simulate = params[keyForSimulate()]
    # # moHardware tells kTypes to simulate values and Kiln to use sim processing
    # moHardware.simulateKiln(simulate)
    # targetT = params[keyForTargetTemp()]
    # displacement = params[keyForTargetDisplacement()]
    # maxTime = params[keyForMaxTime()]
    # timeStep = params[keyForTimeStep()]
    # holdTime = params[keyForKilnHoldTime()]
    #
    # kilnInstance.startScript(targetT, displacement, maxTime, timeStep, holdTime)

class KilnScript:
    # set of commands for KilnControl
    def __init__(self):
        self.name = "MODAC Kiln Script X"
        self.description = "created " +datetime.datetime.now().strftime("%Y%m%d_%H:%M:%S")
        self.segments = [
            KilnScriptSegment(),
            ] # defaults to having one
        self.curSegmentIdx = 0 # used to indicate current segment

    def getSegment(self, idx):
        l = len(self.segments)
        if idx < 0 or idx >= l:
            log.error("kilnSeg requested outOfRange idx "+ str(l))
        else:
            curSegmentIdx = idx
        return self.segments[curSegmentIdx]

    def addNewSegment(self):
        self.segments.append(KilnScriptSegment())
        self.curSegmentIdx = len(self.segments) -1
        return self.segments[curSegmentIdx]

    def insertSegmentBefore(self,beforeIdx):
        self.segments.insert(beforeIdx, KilnScriptSegment())
        self.curSegmentIdx = beforeIdx
        return self.segments[curSegmentIdx]

    def loadScript(self, filename):
        pass

    def saveScript(self, filename):
        # saves this script as JSON file
        # name, description, segments[]
        #open json file
        # build state dict for json
        # write it
        # close file
        with open(filename, "w") as jsonFile:
            txt = self.asJson()
            log.debug("write Script as Json" + txt +" toFile: "+filename)
            json.dump(self.asDict(), jsonFile, indent=4)
            jsonFile.flush()
            jsonFile.close()

    def asJson(self):
        return json.dumps(self.asDict(), indent=4)

    def asDict(self):
        d = {
            keyForScriptName(): self.name,
            keyForScriptDescription(): self.description,
            keyForScriptCurrentSegmentIdx(): self.curSegmentIdx,
            keyForScriptSegments(): self.segmentsAsDict(),
        }
        return d

    def segmentsAsDict(self):
        a = []
        for s in self.segments:
            a += s.asDict()
        print("Segments array ",self.segments)
        print("as array of dict ",a)
        return a


    def parseKilnScript(self,params):
        pass


class KilnScriptSegment:
    stepIdx = -1 # index into Script[], maybe
    
    # these are parameters you can program
    targetTemperature = 0 # deg C; temp the kiln should reach in this segment
    targetDistanceChange = 0 # if <=0 then ignore distance
    holdTimeMinutes = 0 # minutes to hold once targetTemperature is reached
    exhaustFan = 0 # off or on
    supportFan = 0 # off or on
    stepTime = default_stepTime # from kilnConfig.py

    # rest are locals for running the script
    # really only need  them for active segment so are now in the kiln object

    def asDict(self):
        d = {
            keyForSegmentIndex(): self.stepIdx,
            keyForTargetTemp(): self.targetTemperature,
            keyForSegmentIndex(): self.targetDistanceChange,
            keyForSegmentIndex(): self.holdTimeMinutes,
            keyForExhaustFan(): self.exhaustFan,
            keyForSupportFan(): self.supportFan,
            keyForPIDStepTime(): self.stepTime,
        }
        return d

    def defaultKilnScriptSegment(self):
        defaultSegment = {
            keyForIndex(): -1,
            keyForTargetTemp(): 0,
            keyForKilnHoldTime(): 0,
            keyForTargetDisplacement(): 0,
            keyForMaxTime(): 0,
        }
        return defaultSegment
