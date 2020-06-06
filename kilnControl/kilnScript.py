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
from collections import OrderedDict
#
from modac.moKeys import *
from .kilnConfig import *

# JSON converted to dictionary
# { kilnScript
# }
#


from .kilnState import KilnState, KilnScriptState


# from .kiln import  kilnInstance

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

# given a file, try to load it as Json save of KilnScript
def loadScriptFromFile( filename):
    with open(filename, "r") as jsonFile:
        dict = json.load(jsonFile)
        log.debug("Read jsonDict from file: " + filename )
        return KilnScript(dict)
    return None

def newScriptFromText(text):
    dict = json.loads(text)
    log.debug("Read jsonDict from text: " + text )
    return KilnScript(dict)

class KilnScript:
    # set of commands for KilnControl
    def __init__(self, dict= None):
        self.name = "MODAC Kiln Script X"
        self.description = "created " + datetime.datetime.now().strftime(keyForTimeFormat())
        self.segments = []  # defaults to having none
        self.curSegmentIdx = 0  # used to indicate current segment
        #self.simulate = False
        self.simulate = True
        if dict == None:
            # create a new empty one
            self.addNewSegment()
        else:
            # parse the dictionary
            #log.debug("init kilnScript from dict " + str(dict))
            self.name = dict[keyForScriptName()]
            self.description= dict[ keyForScriptDescription()]
            self.curSegmentIdx = dict [keyForScriptCurrentSegmentIdx()]
            self.simulate = dict [keyForSimulate()]
            segmentDict = dict [keyForScriptSegments()]
            # how to parse out this array?
            #log.debug("init kilnScript from dict " + str(self))
            #log.debug("do segments "+ str(segmentDict))
            for segAsDict in segmentDict:
                # create new segment from dict and add it to array - insure index is correct
                s = KilnScriptSegment()
                s.updateFromDict(segAsDict)
                self.segments.append(s)
            log.debug("initialized kilnScript from dict " + str(self))

    def __str__(self):
        return json.dumps(self.asDict(), indent=4)

    def __repr__(self):
        return json.dumps(self.asDict(), indent=4)

    def numSteps(self):
        return len(self.segments)

    def getSegment(self, idx):
        l = self.numSteps()
        if idx < 0 or idx >= l:
            log.error("kilnSeg requested outOfRange idx " + str(l))
        else:
            self.curSegmentIdx = idx
        return self.segments[self.curSegmentIdx]

    def getCurrentSegment(self):
        return self.segments[self.curSegmentIdx]

    def addNewSegment(self):
        l = len(self.segments)
        newSeg = KilnScriptSegment(l)
        self.curSegmentIdx = l
        newSeg.stepIdx = l
        #log.debug("Created New segment idx " + str(l) + ": " + str(newSeg))
        self.segments.append(newSeg)
        return newSeg

    def removeCurrentSegment(self):
        del self.segments[self.curSegmentIdx]
        self.curSegmentIdx -= 1
        if self.curSegmentIdx < 0:
            self.addNewSegment()  # cant have it empty
        # TODO - renumber segments

    def insertSegmentBefore(self, beforeIdx):
        #TODO not tested
        seg = KilnScriptSegment()
        seg.stepIdx = beforeIdx
        self.segments.insert(beforeIdx, seg)
        self.curSegmentIdx = beforeIdx
        return self.segments[curSegmentIdx]

    def saveScript(self, filename):
        # saves this script as JSON file
        # name, description, segments[]
        # open json file
        # build state dict for json
        # write it
        # close file
        with open(filename, "w") as jsonFile:
            txt = self.asJson()
            # log.debug("write Script as Json" + txt +" toFile: "+filename)
            json.dump(self.asDict(), jsonFile, indent=4)
            jsonFile.flush()
            jsonFile.close()

    def asJson(self):
        return json.dumps(self.asDict(), indent=4)

    def asDict(self):
        a =    [
                #(keyForState(), KilnState.Unknown.name), #should these be here or in kiln?
                #(keyForKilnScriptState(), KilnScriptState.Unknown.name),
                (keyForScriptName(), self.name),
                (keyForScriptDescription(), self.description),
                (keyForScriptCurrentSegmentIdx(), self.curSegmentIdx),
                (keyForSimulate(), self.simulate),
                (keyForScriptSegments(), self.segmentsAsDict()),
            ]
        d = OrderedDict(a)
        print ("script dict:",d)
        # print(str(d))
        return d

    # TODO Make this list of ScriptSegments into proper json
    def segmentsAsDict(self):
        a = []
        for s in self.segments:
            # log.info("segment s "+ " " + json.dumps(s.asDict()))
            a.append(s.asDict())
        #log.info("array of segments: " + str(a))
        return a

    def renumber(self):
        i = 0
        for s in self.segments:
            s.stepIdx= i
            i += 1

class KilnScriptSegment:
    def __init__(self, idx=0):
        self.stepIdx = idx  # index into Script[], maybe
        # these are parameters you can program
        self.targetTemperature = 100  # deg C; temp the kiln should reach in this segment
        self.targetDistanceChange = 0  # if <=0 then ignore distance
        self.holdTimeMinutes = 1  # minutes to hold once targetTemperature is reached
        self.exhaustFan = 0  # off or on
        self.supportFan = 0  # off or on
        self.v12Relay = True # default is On; turn off in last step
        self.stepTime = default_stepTime  # from kilnConfig.py
        self.maxTimeMin = default_maxTime
        #log.debug("new empty segment:"+ str(self))

    # rest are locals for running the script
    # really only need  them for active segment so are now in the kiln object

    def __str__(self):
        return json.dumps(self.asDict(), indent=4)

    def __repr__(self):
        return json.dumps(self.asDict(), indent=4)

    def asDict(self):
        # keyed dictionary for load/save/share; keep order so it is easier to read
        d = OrderedDict (
            [
                (keyForSegmentIndex(), self.stepIdx),
                (keyForTargetTemp(), self.targetTemperature),
                (keyForTargetDisplacement(), self.targetDistanceChange),
                (keyForKilnHoldTimeMin(), self.holdTimeMinutes),
                (keyForExhaustFan(), self.exhaustFan),
                (keyForSupportFan(), self.supportFan),
                (keyFor12vRelay(), self.v12Relay),
                (keyForPIDStepTime(), self.stepTime),
                (keyForMaxTime(), self.maxTimeMin),
            ]
        )
        #
        # log.info("seg "+str(self.stepIdx)+ " " + json.dumps(d, indent=4))
        return d

    def valueFromDict(self, d, key ):
        try:
            return d[key]
            pass
        except KeyError:
            return 0 # default to integer zero

    def updateFromDict(self, d):
        if d == None:
            log.error("update from Dict given None")
            return
        self.stepIdx = self.valueFromDict(d,keyForSegmentIndex())
        self.targetTemperature = self.valueFromDict(d,keyForTargetTemp())
        self.targetDistanceChange = self.valueFromDict(d,keyForTargetDisplacement())
        self.holdTimeMinutes = self.valueFromDict(d,keyForKilnHoldTimeMin())
        self.exhaustFan = self.valueFromDict(d,keyForExhaustFan())
        self.supportFan = self.valueFromDict(d,keyForSupportFan())
        self.stepTime = self.valueFromDict(d,keyForPIDStepTime())
        self.v12Relay = self.valueFromDict(d,keyFor12vRelay())
        #log.debug("update from Dict: "+ json.dumps(d, indent=4) + "\n yields: "+ str(self))



