# modac Kiln Controller, built on generic modac data acq & control
#  runs as trio thread on ModacServer having direct control of BinaryOut
#  links into the modac.moData blackboard of shared data for sensors
#  most configuration is in kilnControl.py
#  kilnState.py defines enum class for stateMachine
#
#  7may20- revaming for multi step sequence/scripts
#  old: currently only does single PID run defined as
#  Heat to Temp, hold till displacement, cool down
#  single or 3 ktypes optional config, all heaters gang on/off
#
# External API:
#  startKilnControlProcess(nursery) creates Kiln obj, sets up thread
#  endKilnControlProcess() terminates thread
#  emergencyShutoff() shuts down kiln (12vrelay power)
#  runKilnScript(params): Cmd handler to run a kiln cycle. params is Dict with array of KilnStep
#

import sys
this = sys.modules[__name__]
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import time
import datetime
from enum import Enum

import trio

from . import pidController

from modac import moData, moHardware, moServer
from modac.moKeys import *
from .kilnConfig import *
from .kilnState import *
from .kilnScript import *

#####################
# singleton really
kilnInstance = None
# are we allowing control?  some tools may not want kiln process to run at all
enableKilnControl = True
# are we using EStop (software only at present)
enableEStop = True# False

# heater on/off via relays  relays are ActiveLow, which is handled in BinaryOutputs.py
HeaterOn = True
HeaterOff = False

#####################
def emergencyShutOff():
    log.warn("EMERGENCY OFF tiggered")
    # shut off 12v power
    # turn on exhaust fan
    # shut off heaters
    moHardware.binaryCmd(relayPower, False)
    moHardware.binaryCmd(heater_lower, HeaterOff)
    moHardware.binaryCmd(heater_middle, HeaterOff)
    moHardware.binaryCmd(heater_upper, HeaterOff)
    moHardware.binaryCmd(fan_exhaust, True)
    # ring alarm bell (dont have one, yet)
    this.kilnInstance.state = KilnState.Error
    this.kilnInstance.processRunnable = False
    endKilnControlProcess() #terminate thread
    # error state tells it we not running


#####################
# use command to start kiln process
async def startKilnControlProcess(nursery=None):
    if not this.kilnInstance == None:
        log.error("StartKilnCmd but Kiln already instanced")
        return
    if nursery == None:
        nursery = moData.getNursery()
        
    if enableKilnControl:
        log.debug("startKiln soon")
        this.kilnInstance = Kiln() #simulate=True)
        nursery.start_soon(this.kilnInstance.kilnControlProcess)
        # ugh how to kill off Kiln object. Singleton?
    else:
        log.debug("Kiln Control Disabled")
        
def endKilnControlProcess():
    '''terminate the kiln thread'''
    if this.kilnInstance == None:
        log.debug("endKiln, no kiln")
        return
    this.kilnInstance.terminateScript()  #  stops run, doesnt terminate thread
    this.kilnInstance.processRunnable = False  #  this should terminate thread
    this.kilnInstance.state = KilnState.Closed
    this.kilnInstance.publishStatus() # one last time
    this.kilnInstance = None # can we throw it away now?
    #
    log.debug("endKiln executed")

def handleRunKilnScriptCmd(params):
    '''handler for interprocess command to run a kiln script. params is dictionary of Keys'''
    # TODO in process of conversion - old one step run; new multi-step script
    # each kilnStep has a TargetTemp, and two end conditions: HoldTime, SlumpDistance
    # REVISING: multiple steps in kilnScript now
    print("\n\n*****runKilnScriptCmd", params)
    if this.kilnInstance == None:
        log.error("No Kiln found")
        return
    try:
        this.kilnInstance.runKilnScript(params)
    except:
        log.error("Bad Parameters: "+ params.ToString())

def handleEndKilnScriptCmd():
    # tell script to stop and set status back to KilnState.Idle
    pass

#####################

def setRelayPower(onOff= False):
    moHardware.binaryCmd(relayPower, onOff)

#####################
# kilnTemps is array of reported temps for our 3 Tcouple + average
# this should be dependent on Num Ktype in kiln but not needed yet

# simulation of Temps is controlled by this var/func
# and code is down below normal loop
simulation = False
def setSimulation(onOff):
    this.simulation = onOff
    log.info("Kiln setSimulation "+str(onOff)+ " this.simulation:"+str(this.simulation ))

#####################
#####################

class Kiln:
    '''kiln class is the primary interface for externals.
    It provides for trio type async monitoring and data posting loop
    '''
    useSinglePID = True # implyze avg temp and single heater on/off
    # TODO we havent built 3 PID version yet
    commandedHeaterStates = [HeaterOff, HeaterOff, HeaterOff, HeaterOff]
    
    def __init__(self, time_step=default_stepTime):#, nursery=None):
        # simulation was removed for modac, need it for good testing
        self.processRunnable = False
        self.state = KilnState.Closed
        self.reset()
        log.debug("Kiln initialized")
        self.state = KilnState.Starting

    def reset(self):
        self.processStartTime = 0
        self.processRuntime = 0
        self.totaltime = 0
        self.sleepThisStep = idleStateTimeStep

        self.state = KilnState.Idle
        self.scriptState = KilnScriptState.NoScriptStep

        self.kilnScript = None
        self.scriptIndex = -1

        self.targetTemperature = 0
        self.targetDisplacement= -1
        self.targetHoldTime = 0 # minutes to hold at target temp

        self.startHoldTime = 0  # begin of hold state
        self.timeInHoldSeconds = 0
        self.timeInHoldMinutes = 0

        self.maxTimeMin = 0
        self.maxTimeSec = 0
        self.startDistance = 0
        self.currentDistance = 0
        self.currentDisplacement = 0
        self.reportedHeaterStates = [False, False, False, False]
        self.commandedHeaterStates = [HeaterOff, HeaterOff, HeaterOff, HeaterOff]
        self.kilnTemps = default_kilnTemperatures #self.kilnStartTemps #[0,0,0,0]
        self.pidOut = [0, 0, 0, 0]
        self.pids = [None, None, None, None]
        self.pids[0] = pidController.PIDController()
        if not self.useSinglePID:
            self.pids[1] = pidController.PIDController()
            self.pids[2] = pidController.PIDController()
            self.pids[3] = pidController.PIDController()
        log.debug("Kiln reset")
        self.publishStatus()

    def terminateScript(self):
        log.info("kiln.terminateScript()")
        # should turn off all heaters
        moHardware.binaryCmd(heater_lower, HeaterOff)
        moHardware.binaryCmd(heater_middle, HeaterOff)
        moHardware.binaryCmd(heater_upper, HeaterOff)

        self.reset() # clear everything
        self.state = KilnScriptState.EndRun # hang out in this for lil bit to let clients know

        # turn off 12v Power
        setRelayPower(False)
        # and turn off simulation
        moHardware.simulateKiln(False)
        self.publishStatus()      
        log.info("terminateScript")
       
    def collectStatus(self):
        startTimeStr =" NotStarted"
        if isinstance(self.processStartTime, datetime.datetime):
            startTimeStr = self.processStartTime.strftime("%Y-%m-%d %H:%M:%S%Z")
        
        status = {
            # sha}red keys - for debug purposes
            # default values set in moData so not dependent on this file
            # record time we collected data
            keyForTimeStamp(): datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S%Z"),
            "kilnProcessRunnable": self.processRunnable,
            #kiln state
            keyForState(): self.state.name,
            keyForKilnScriptState(): self.scriptState.name,
            keyForSimulate(): this.simulation,

            # Script Segment Parameters
            keyForSegmentIndex(): self.scriptIndex,
            keyForTargetTemp(): self.targetTemperature,
            keyForKilnHoldTime(): self.targetHoldTime,
            keyForTargetDisplacement(): self.targetDisplacement,
            keyForPIDStepTime(): self.sleepThisStep,
            keyForMaxTime(): self.maxTimeMin,

            # Script Segment data
            keyForKilnTimeInHoldSeconds(): self.timeInHoldSeconds,
            keyForKilnTimeInHoldMinutes(): self.timeInHoldMinutes,
            keyForKilnHoldStartTime(): self.startHoldTime,
            keyForKilnRuntime(): self.processRuntime,
            KilnStartTime(): startTimeStr,
            
            keyForStartDistance(): self.startDistance,
            keyForTargetDisplacement(): self.targetDisplacement,
            
            keyForCurrentDistance(): self.currentDistance,
            keyForCurrentDisplacement(): self.currentDisplacement,
            
            keyForKilnHeaters(): self.reportedHeaterStates,
            keyForKilnHeaterCommanded(): self.commandedHeaterStates,
            keyForKilnTemperatures(): self.kilnTemps,
        }
        #print("KilnStatus:", status)
        return status

    def publishStatus(self):
        '''Put KilnStatus into moData, does NOT publish separate cmd'''
        status = self.collectStatus()
        log.info("Publish Kiln Status %r" % status)
        moData.update(keyForKilnStatus(), status)
        #moServer.publishData(keyForKilnStatus(), status) # separate publish? or as part of moData?

    # kilnControlProcess runs in an async Trio thread, mostly sits Idle, unless running a script
    async def kilnControlProcess(self):
        # setup basic self/instance variables, much of that delegated to self.reset()
        self.processStartTime = datetime.datetime.now() # record start time,
        self.state = KilnState.Starting # set the initial state
        # record temps at start of process - was used to return in Cooling but new multiStep scripts should not use

        log.info("\n\n****** kilnControlProcess starting Kiln Status %r" % self.collectStatus())

        #await trio.sleep(0.5)
        print("runKiln starting loop")
        log.debug("kilnControlProcess start processRunnable loop")
        self.processRunnable = True
        self.state = KilnState.Idle
        while self.processRunnable:
            self.kilnStep()
            #self.sleepThisStep = self.time_step   # TODO set this in KilnStep
            self.publishStatus()
            #print("bottom of forever loop sleep for",self.sleepThisStep)
            await trio.sleep(self.sleepThisStep)
            
        log.debug("\n\n******")
        print("kilnControlProcess end processRunnable loop")
        log.info("kilnControlProcess end forever loop")
        print("\n\n******")
        
        #out of while processRunnable
        self.reset()
        self.state = KilnState.Closed
        self.publishStatus() # one last time
        log.info("exit runKiln thread")

    # kilnStep does one iteraton of the kiln control
    def kilnStep(self):
        '''do one iteration of a kiln script'''

        # update Times
        currentTime = datetime.datetime.now()
        self.processRuntime = (currentTime - self.processStartTime).total_seconds()
        if self.state == KilnState.RunningScript:
            self.scriptRuntime = (currentTime - self.scriptStartTime).total_seconds()
            if self.scriptState == KilnScriptState.Holding:
                self.timeInHoldSeconds = (currentTime - self.startHoldTime).total_seconds()
                self.timeInHoldMinutes = self.timeInHoldSeconds/60

        # Update Data (heaters, fans, temperture, distance)
        self.updateBinaryDevices()
        self.updateTemperatures()
        self.updateDistance()

        log.debug("KilnStep top state: "+str(self.state)+" heaters:"+str(self.reportedHeaterStates)+" temp:"+str(self.kilnTemps))
        
        # if we are WAY TOO HOT, shut down kil run and turn on exhaust
        if enableEStop:
            if (self.kilnTemps[0] >= emergency_shutoff_temp):
                log.error("emergency!!! temperature too high, shutting down")
                moHardware.EmergencyOff()
                return
            
        if (self.kilnTemps[0] < 0.0):
            # should never get below zero
            log.error("Kiln ERROR: average temp is below zero! "+str(self.kilnTemps[0]))
            log.error("there is error somewhere, so shutdown")
            moHardware.EmergencyOff()
            return
    
        if self.state == KilnState.Idle:
            #print("Kiln idle step")
            # after collecting, nothing left to do in Idle
            return
        
        log.info("kilnStep not Idle = " + str(self.state))

        if (self.processRuntime >= self.maxTimeSec):
            log.error("Max Time for script exceeded, abort script")
            self.terminateScript()
            return;

        # 
        if self.state == KilnState.EndRun:
            # hold EndRun for a bit to let UI/monitors know
            if (self.processRuntime - self.endRunStart) >= endRunHoldTime:
                self.state = KilnState.Idle
                log.debug("Kiln state change EndRun > Idle")
                #anything else need reset?
            return

        ###################
        # now deal with Script Segment

        # displacement test - have we reached slump distance?

        self.currentDisplacement = self.currentDistance - self.startDistance

        # if displacement target reached got to next segment
        # if our current is close enough to target, got to next segment
        if (self.currentDisplacement + distanceEpsilon) >= self.targetDisplacement:
            self.nextScriptSegment()

        if self.state == KilnState.Holding :
            # holding at target temp, how long we been here?
            # self.targetHoldTime = 0 # minutes to hold at target temp, default 0 = ignore
            log.debug("Kiln HOLDING started at "+str(self.startHoldTime) +" cur:"+str(currentTime))
            self.timeInHold = (currentTime - self.startHoldTime).total_seconds() #/ 60.0
            log.debug("Kiln Holding, target " +str(self.targetHoldTime)+ " In Hold" +str(self.timeInHold))
            
            if self.targetHoldTime > 0.0 and self.timeInHold > self.targetHoldTime :
                # hold time given and exceeded
                log.info("Hold Time reached,next step")
                self.nextScriptSegment()
 
        # test if reached hold temp +- some epsilon
        if self.state == KilnState.Heating and self.targetTemperature <= self.kilnTemps[0] :
            #+ self.tempertureEpsilon:
            # reached temp, state should be Hold
            self.state = KilnState.Holding
            self.startHoldTime = currentTime
            log.debug("Kiln Switch to Holding State "  +str(currentTime))
            
        # pdate PID/Heater control
        # shouldnt get here if state isnt Heating or Holding, but test anyway
        if self.state == KilnState.Heating or self.state == KilnState.Holding:
            # update PIDs
            self.commandedHeaterStates = [HeaterOff, HeaterOff, HeaterOff, HeaterOff]
            if self.useSinglePID:
                #using only the 0 index wich may be avg or paritular ktype to control PID
                self.pidOut[0] = self.pids[0].compute(self.targetTemperature, self.kilnTemps[0])
                log.debug("======")
                print("PID 0: ", self.pidOut[0], self.targetTemperature, self.kilnTemps[0])
                if (self.pidOut[0] > 0):
                    # turn heaters on
                    self.commandedHeaterStates = [HeaterOn, HeaterOn, HeaterOn, HeaterOn]
            else:
                # compute individual pidOuts
                # pidOut[0] true if any true
                self.pidOut[1] = self.pids[1].compute(self.targetTemperature, self.kilnTemps[1])
                if (self.pidOut[1] > 0):
                    # turn heaters on
                    self.commandedHeaterStates[0] = HeaterOn
                    self.commandedHeaterStates[1] = HeaterOn
                self.pidOut[2] = self.pids[2].compute(self.targetTemperature, self.kilnTemps[2])
                if (self.pidOut[2] > 0):
                    # turn heaters on
                    self.commandedHeaterStates[0] = HeaterOn
                    self.commandedHeaterStates[2] = HeaterOn
                self.pidOut[3] = self.pids[3].compute(self.targetTemperature, self.kilnTemps[3])
                if (self.pidOut[3] > 0):
                    # turn heaters on
                    self.commandedHeaterStates[0] = HeaterOn
                    self.commandedHeaterStates[3] = HeaterOn
            # common code to command heaters to change, but only if needed
            self.commandHeaters()

            for i in range(1,4):
                if not self.reportedHeaterStates[i] == self.commandedHeaterStates[i]:
                    log.info("kiln cmd heater change %d"%i)
                    moHardware.binaryCmd(heaters[i], self.commandedHeaterStates[i])
        # bottom of step

        #log, publish and put in data blackboard
        #self.publishStatus()
        
    def commandHeaters(self):
        # turn on.off any reported heaters that dont match commanded values
        # ignore 0 as it is just OR of other values
        # TODO magic number here- configure NumberOfHeaters 3+1
        for i in range(1,4):
            if not self.reportedHeaterStates[i] == self.commandedHeaterStates[i]:
                log.info("kiln cmd heater change %d"%i)
                moHardware.binaryCmd(heaters[i], self.commandedHeaterStates[i])

    def commandExhaustFan(self, cmdState):
        # turn on/off exhaust
        self.exhaustFanCommanded = cmdState
        moHardware.binaryCmd(fan_exhaust, cmdState)

    def commandSupportFan(self, cmdState):
        # turn on/off support fan
        self.supportFanCommanded = cmdState
        moHardware.binaryCmd(fan_support, cmdState)

    def updateBinaryDevices(self):
        '''map MODAC Binary Output data to local variables'''
        # one call gets all the binaryOut ports and we parse out the ones neede as defined in kilnConfig.py
        binaryOutputs = moData.getValue(keyForBinaryOut())
        self.reportedHeaterStates[1] = binaryOutputs[heater_lower]
        self.reportedHeaterStates[2] = binaryOutputs[heater_middle]
        self.reportedHeaterStates[3] = binaryOutputs[heater_upper]
        self.reportedHeaterStates[0] = self.reportedHeaterStates[1] or self.reportedHeaterStates[2] or self.reportedHeaterStates[3]
        self.exhaustFanState = binaryOutputs[fan_exhaust]
        self.exhaustFanState = binaryOutputs[fan_support]

    def updateTemperatures(self):
        ''' retrieve thermocouple values degC, avg the ones we want '''
        kTemps = moData.getValue(keyForKType())
        # print("Kiln ktypes read as: ", kTemps)
        sum = 0.0
        self.kilnTemps[1] = kTemps[kType_lower]
        self.kilnTemps[2] = kTemps[kType_middle]
        self.kilnTemps[3] = kTemps[kType_upper]
        sum = self.kilnTemps[1] + self.kilnTemps[2] + self.kilnTemps[3]
        avg = sum / 3

        # how we get kiln temp depends on bool from kilnControl/kilnControl.py
        if kType_avgAll:
            # use the average of 3 ktype thermocouples
            self.kilnTemps[0] = avg
        else:
            # use only the lower (first) ktype = bottom
            self.kilnTemps[0] = self.kilnTemps[1]

        #tempStr = keyForKilnTemperatures() + ":"
        #for i in range(len(self.kilnTemps)):
        #    tempStr += "{0:5.2f} ".format(self.kilnTemps[i])
        #log.debug("Kiln get temps = " + tempStr)

    def updateDistance(self):
        if this.simulation:
            slumpRate = 0.1 # mm per loop
            if self.state == KilnState.RunningScript and self.scriptState == KilnScriptState.Holding :
                self.currentDistance += slumpRate
        else:
            lData = moData.getValue(keyForLeicaDisto())
            self.currentDistance = lData[keyForDistance()]

    def runKilnScript(self, scriptAsJson):
        log.debug("runKilnScript: "+str(scriptAsJson))
        self.kilnScript = kilnScript.newScriptFromText(scriptAsJson)
        self.scriptIndex = 0
        self.loadScriptStep()
        if this.simulation:
            dist = 1000.0  # 1meter start dist in simulation
            print("Kiln Simulation start dist", dist)
        else:
            lData = moData.getValue(keyForLeicaDisto())
            print("startKiln Run leicaPanel.getData = ", lData)
            dist = lData[keyForDistance()]

        # test for no data
        if dist <= 0:
            log.error("No data for Leica, Kiln run may not work")
            self.state = KilnState.Idle
            # return;
        self.startDistance = dist
        self.currentDistance = dist
        self.targetDist = self.startDistance + self.targetDisplacement

        setRelayPower(True)

        self.state = KilnState.Heating
        log.info("Starting Kiln run.. status:" + str(self.collectStatus()))
        log.info("async kiln loop should pick this up")

    def nextScriptSegment(self):
        self.scriptIndex += 1
        if self.scriptIndex > self.kilnScript.numSteps():
            # ran off end of script.
            # end of runScript
            log.debug("NextStep for kilnScript")
            self.terminateScript()
            return
        self.loadScriptStep()
        pass

    def loadScriptStep(self):
        if self.kilnScript == None:
            log.error("no kiln script for loading step")
            return
        curSeg = self.kilnScript.getSegment(self.scriptIndex)

        # copy values from script to internals
        # we use internals and duplicate curSeg/kilnScript to keep it pristine
        # and also because the rest of this was written with local vars first
        # and scriptSegments/steps added later
        self.targetTemperature = curSeg.targetTemperature
        self.targetDisplacement= curSeg.targetDistanceChange
        self.segmentStartTime = datetime.datetime.now()
        self.maxTimeMin = curSeg. maxTime
        self.maxTimeSec =  curSeg.maxTime* 60
        self.step_time = curSeg. stepTime
        self.targetHoldTimeMin = curSeg.holdTimeMinutes
        self.targetHoldTimeSec = self.targetHoldTimeMin * 60


  
        
        
        