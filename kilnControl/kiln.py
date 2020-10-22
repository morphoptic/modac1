# modac Kiln Controller, built on generic modac data acq & control
#  runs as trio thread on ModacServer having direct control of BinaryOut
#  links into the modac.moData blackboard of shared data for sensors
#  posts several datum to toplevel moData so it gets to CSV, rest as normal
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

# TODO: why does the kilnTemp here lag the ktypes by several seconds?
# TODO cont: because the read/publish loop is different time than kiln/PID
# TODO: split the read/publish into two trio tasks; add moData locking

import sys
this = sys.modules[__name__]
import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import trio

from . import pidController

from modac import moData, moHardware, moServer
from modac import ad16
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

criticalTemp = 700

def init():
    log.info("Init KilnControl.Kiln Package")
    this.kilnInstance = Kiln()
    this.kilnInstance.publishStatus()


#####################
# use command to start kiln process
async def startKilnControlProcess(nursery=None):
    if this.kilnInstance is None:
        this.init()

    if nursery is None:
        nursery = moData.getNursery()

    if enableKilnControl:
        log.debug("startKiln soon")
        nursery.start_soon(this.kilnInstance.kilnControlProcess)
        # ugh how to kill off Kiln object. Singleton?
    else:
        log.debug("Kiln Control Disabled")

def endKilnControlProcess():
    '''terminate the kiln thread'''
    if this.kilnInstance is None:
        log.debug("endKiln, no kiln")
        return
    this.kilnInstance.terminateScript()  #  stops run, doesnt terminate thread
    this.kilnInstance.processRunnable = False  #  this should terminate thread
    this.kilnInstance.state = KilnState.Closed
    this.kilnInstance.publishStatus() # one last time
    this.kilnInstance = None # can we throw it away now?
    log.debug("endKiln executed")

def handleRunKilnScriptCmd(params):
    '''handler for interprocess command to run a kiln script. params is dictionary of Keys'''
    log.info("\n\n*****runKilnScriptCmd" +params)
    if this.kilnInstance is None:
        log.error("No Kiln found")
        return
    try:
        this.kilnInstance.runKilnScript(params)
    except:
        log.error("Bad Parameters: "+ params.ToString())

def handleEndKilnScriptCmd():
    # tell script to stop and set status back to KilnState.Idle
    log.info("\n*****handleEndKilnScriptCmd")
    if this.kilnInstance is None:
        log.error("No Kiln found")
        return
    this.kilnInstance.terminateScript()

#####################

# def setRelayPower(onOff= False):
#     log.debug("kiln SetRelayPower "+str(onOff))
#     if this.simulation == False: # 12v On
#         log.debug("not simulation, so do as commanded")
#         moHardware.binaryCmd(relayPower, onOff)
#     else: # simulatoin, dont turn on 12v power
#         log.debug("simulating, dont turn on relay power")
#         moHardware.binaryCmd(relayPower, False)


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
        self.processStartTime = datetime.datetime.now() # record start time,
        self.processRunnable = False
        self.state = KilnState.Closed
        self.simulation = False

        self.overHeatTime = 10*60 # temp doenst change in N min
        self.reset()
        log.debug("Kiln initialized")
        self.state = KilnState.Starting

    def reset(self):
        self.processRuntime = 0
        self.totaltime = 0
        self.sleepThisStep = idleStateTimeStep

        self.state = KilnState.Idle
        self.scriptState = KilnScriptState.NoScriptStep

        self.myScript = None
        self.scriptIndex = -1
        self.scriptStartTime = None

        self.targetTemperature = 0
        self.targetDisplacement= -1
        self.targetHoldTimeMin = 0 # minutes to hold at target temp
        self.targetHoldTimeSec = self.targetHoldTimeMin * 60 # seconds for compare with timeDelta.seconds

        self.startHoldTime = 0  # begin of hold state
        self.startHoldTimeStr = "notHolding"
        self.timeInHoldSeconds = 0
        self.timeInHoldMinutes = 0

        self.maxTimeMin = 0
        self.maxTimeSec = 0
        self.startDistance = 0
        self.currentDistance = 0
        self.currentDisplacement = 0
        self.reportedHeaterStates = [False, False, False, False]
        self.commandedHeaterStates = [HeaterOff, HeaterOff, HeaterOff, HeaterOff]
        self.exhaustFanState = False
        self.supportFanState = False
        self.v12RelayState = False

        self.kilnTemps = default_kilnTemperatures #self.kilnStartTemps #[0,0,0,0]
        self.pidOut = [0, 0, 0, 0]
        self.pids = [None, None, None, None]
        self.pids[0] = pidController.PIDController()
        self.lastCheckHeatingTime = None
        self. lastCheckHeatingTemp = 0
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
        self.command12VRelay(False)
        # turn off fans
        self.commandExhaustFan(False)
        self.commandSupportFan(False)

        moServer.publishKilnScriptEnded() # send ScriptEnded message
        self.reset()

        # were using this but not anymore so comment out
        #self.state = KilnScriptState.EndRun # hang out in this for lil bit to let clients know

        # and turn off simulation
        moHardware.simulateKiln(False) # also calls this.setSimulation
        moServer.publishKilnScriptEnded() # send ScriptEnded message, again

        #log.debug(" status at end of terminateScript")
        self.publishStatus()
        log.info("terminateScript end")
       
    def updateStatus(self):
        # better for this to start w default and update instead of new each call
        # these are top level moData so they get t CSV easy
        moData.update(keyForKilnState(),self.state.name)
        moData.update(keyForKilnScriptState(), self.scriptState.name)
        moData.update(keyForIndex(),self.scriptIndex)

        #startTimeStr =" NotStarted"
        #if isinstance(self.processStartTime, datetime.datetime):
        startTimeStr = self.processStartTime.strftime(keyForTimeFormat())

        status = moData.getValue(keyForKilnStatus())
        if status is None:
            log.debug("first status, get default")
            status = defaultKilnRuntimeStatus()

        # step thru list updating
        # shared keys - for debug purposes
        # default values set in moData so not dependent on this file
        # record time we collected data
        status[keyForTimeStamp()] = datetime.datetime.now().strftime(keyForTimeFormat())
        status["kilnProcessRunnable"] = self.processRunnable
            
            #kiln state
        status[keyForState()] = self.state.name
        status[keyForKilnScriptState()] = self.scriptState.name
        status[keyForSimulate()]= this.simulation

        # Script Segment Parameters
        status[keyForSegmentIndex()] = self.scriptIndex
        status[keyForTargetTemp()] = self.targetTemperature
        status[keyForKilnHoldTimeMin()] = self.targetHoldTimeMin
        status[keyForKilnHoldTimeSec()] = self.targetHoldTimeSec
        status[keyForTargetDisplacement()] = self.targetDisplacement
        status[keyForPIDStepTime()] = self.sleepThisStep
        status[keyForMaxTime()] = self.maxTimeMin

            # Script Segment data
        status[keyForKilnTimeInHoldSeconds()] = self.timeInHoldSeconds
        status[keyForKilnTimeInHoldMinutes()] = self.timeInHoldMinutes
        status[keyForKilnHoldStartTime()] = self.startHoldTimeStr
        status[keyForKilnRuntime()] = self.processRuntime
        status[keyForKilnStartTime()] = startTimeStr
            
        status[keyForStartDistance()] = self.startDistance
        status[keyForTargetDisplacement()] = self.targetDisplacement
            
        status[keyForCurrentDistance()] = self.currentDistance
        status[keyForCurrentDisplacement()] = self.currentDisplacement
            
        status[keyForKilnHeaters()] = self.reportedHeaterStates
        status[keyForKilnHeaterCommanded()] = self.commandedHeaterStates
        status[keyForKilnTemperatures()] = self.kilnTemps
        status[keyForExhaustFan()] = self.exhaustFanState
        status[keyForSupportFan()] = self.supportFanState
        status[keyFor12vRelay()] = self.v12RelayState

        # (keyForScript(), str(self.myScript)),
        return status

    def publishStatus(self):
        '''Put KilnStatus into moData, does NOT publish separate cmd'''
        status = self.updateStatus()
        # moData.update(keyForKilnState(),self.state.name)
        # moData.update(keyForKilnScriptState(), self.scriptState.name)
        #log.info("Publish Kiln Status %r" % status)
        #log.info("Publish Kiln Status %s" % json.dumps(status,indent=4))
        # update Status should change the one in kiln
        #moData.update(keyForKilnStatus(), status)
        #moServer.publishData(keyForKilnStatus(), status) # separate publish? or as part of moData?
        pass

    # kilnControlProcess runs in an async Trio thread, mostly sits Idle, unless running a script
    async def kilnControlProcess(self):
        # setup basic self/instance variables, much of that delegated to self.reset()
        self.processStartTime = datetime.datetime.now() # record start time,
        self.state = KilnState.Starting # set the initial state

        log.info("\n\n****** kilnControlProcess starting; Kiln Status %r" % self.updateStatus())

        #await trio.sleep(0.5)
        print("runKiln starting loop")
        log.debug("kilnControlProcess start processRunnable loop")
        self.processRunnable = True
        self.state = KilnState.Idle
        while self.processRunnable:
            if moData.getStatus() == moData.moDataStatus.Error:
                log.error("kilnControl: noting error in moData, so kill process")
                self.processRunnable = False
                self.terminateScript()
                self.state = KilnState.Error
                self.updateStatus()
                self.publishStatus()
                break
            if ad16.isError():
                emergencyShutOff()
                break
            if self.state == KilnState.Error:
                log.error("Kiln has gone into Error state. Terminate Process")
                self.processRunnable = False
                self.publishStatus()
                break

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
                self.lastCheckHeatingTime = None
                self.lastCheckHeatingTemp = 0

        # Update Data (heaters, fans, temperture, distance)
        moHardware.updateKilnSensors()
        # these update from moData
        self.updateBinaryDevices()
        self.updateTemperatures()
        self.updateDistance()

        log.debug("KilnStep top; state: "+str(self.state)+ " curSeg:"+str(self.scriptIndex)+"\n    heaters:"+str(self.reportedHeaterStates)
                  +" temp:"+str(self.kilnTemps) +" heaters:"+str(self.reportedHeaterStates)+
                  " relays: e="+str(self.exhaustFanState)+" s="+str(self.supportFanState)+" 12v:"+str(self.v12RelayState))

        if self.scriptState == KilnScriptState.Heating:
            if self.lastCheckHeatingTime is None:
                self.lastCheckHeatingTime = currentTime
                self.lastCheckHeatingTemp = self.kilnTemps[0]
            else:
                deltaTimeSec = (currentTime - self.lastCheckHeatingTime).total_seconds()
                if deltaTimeSec > self.overHeatTime:
                    # its been a while since we checked; has temp changed?
                    if self.lastCheckHeatingTemp < self.kilnTemps[0]:
                        # its heating, so we good
                        self.lastCheckHeatingTime = currentTime
                        self.lastCheckHeatingTemp = self.kilnTemps[0]
                    else:
                        # no change in temp? something wrong
                        log.error("Temperatures didnt change but supposed to be Heating - ERROR!!! "+str(deltaTimeSec))
                        log.error("   lastCheckTemp: "+ str(self.lastCheckHeatingTemp)+" curr ktemps: "+str(self.kilnTemps))
                        #self.terminateScript()
                        #self.state = KilnState.Error
                        #self.publishStatus()
                        #moHardware.EmergencyOff()
                        self.twiddleBinaries()
                        self.lastCheckHeatingTime = currentTime
                        self.lastCheckHeatingTemp = self.kilnTemps[0]
                        return

        # if we are WAY TOO HOT, shut down kil run and turn on exhaust
        if enableEStop:
            if (self.kilnTemps[0] >= emergency_shutoff_temp):
                log.error("emergency!!! temperature too high, shutting down")
                self.terminateScript()
                moHardware.EmergencyOff()
                return
            
        if self.state == KilnState.Idle:
            #print("Kiln idle step")
            # after collecting, nothing left to do in Idle
            return
        
        #log.info("kilnStep not Idle = " + str(self.state))

        if self.kilnTemps[0] <= 1.0 and simulation == False:
            # should never get below 1C (0 is indicator of error)
            # dont kill it yet, just dot let it run non-simulated script
            log.warning("Kiln Warning: average temp is below 1C! " + str(self.kilnTemps[0]))
            # log.error("there is error somewhere, so shutdown")
            # moHardware.EmergencyOff()
            self.terminateScript()
            return

        if (self.processRuntime >= self.maxTimeSec):
            log.error("Max Time for script exceeded, abort script")
            self.terminateScript()
            return;

        # 
        # if self.scriptState == KilnScriptState.EndRun:
        #     # hold EndRun for a bit to let UI/monitors know
        #     if (self.processRuntime - self.endRunStart) >= endRunHoldTime:
        #         self.state = KilnState.Idle
        #         log.debug("Kiln state change EndRun > Idle")
        #         #anything else need reset?
        #     return

        ###################
        # now deal with Script Segment
        #log.debug("deal with Script Segment status: "+self.scriptState.name )

        # displacement test - have we reached slump distance?

        self.currentDisplacement = self.currentDistance - self.startDistance

        # if there is a targetDisplacement
        # if displacement target reached got to next segment
        # if our current is close enough to target, got to next segment
        if self.targetDisplacement >0 and self.currentDisplacement >= self.targetDisplacement:
            log.info("target displacement %f reached. next segment"%(self.currentDisplacement))
            self.nextScriptSegment()

        if self.scriptState == KilnScriptState.Holding:
            # holding at target temp, how long we been here?
            # self.targetHoldTimeSec = 0 # seconds to hold at target temp, default 0 = ignore
            log.debug("Kiln HOLDING started at "+str(self.startHoldTime) +" cur:"+str(currentTime))
            self.timeInHoldSeconds = (currentTime - self.startHoldTime).total_seconds()
            #log.debug("Kiln Holding, targetSec " + str(self.targetHoldTimeSec) + " In Hold" + str(self.timeInHoldSeconds))
            
            if self.targetHoldTimeSec > 0.0 and self.timeInHoldSeconds > self.targetHoldTimeSec :
                # hold time given and exceeded
                log.info("Hold Time reached,next step")
                self.nextScriptSegment()
 
        # test if reached hold temp +- some epsilon
        #log.debug("test if switch to hold")
        if self.scriptState == KilnScriptState.Heating and self.targetTemperature <= self.kilnTemps[0] :
            #+ self.tempertureEpsilon:
            # reached temp, state should be Hold
            self.scriptState = KilnScriptState.Holding
            self.startHoldTime = currentTime
            self.startHoldTimeStr = currentTime.strftime(keyForTimeFormat())
            log.debug("Kiln Switch to Holding State "  +str(currentTime))

        # pdate PID/Heater control
        # shouldnt get here if state isnt Heating or Holding, but test anyway
        if self.scriptState == KilnScriptState.Heating or self.scriptState == KilnScriptState.Holding:
            # only one PID, and always command relays
            self.pidOut[0] = self.pids[0].compute(self.targetTemperature, self.kilnTemps[0])
            if self.pidOut[0] > 0:
                # turn heaters on
                log.debug("single PID - all On")
                self.commandedHeaterStates = [HeaterOn, HeaterOn, HeaterOn, HeaterOn]
            else:  # shouldnt have to do this but
                log.debug("single PID - all Off")
                self.commandedHeaterStates = [HeaterOff, HeaterOff, HeaterOff, HeaterOff]

            for i in range(1,4): # should use len heaters?
                moHardware.binaryCmd(heaters[i], self.commandedHeaterStates[i])

            #log.debug("Update PIDs ")
            # if self.useSinglePID:
            #     self.doSinglePID()
            # else:
            #     self.doMultiplePID()
            # # common code to command heaters to change, but only if needed
            # for i in range(1,4): # should use len heaters?
            #     if not self.reportedHeaterStates[i] == self.commandedHeaterStates[i]:
            #         log.info("pid kiln cmd heater change %d"%i)
            #         moHardware.binaryCmd(heaters[i], self.commandedHeaterStates[i])
        # bottom of step
        #log, publish and put in data blackboard
        #self.publishStatus()
        pass

    def doSinglePID(self):
        # using only the 0 index wich may be avg or paritular ktype to control PID
        # not using this at present
        self.pidOut[0] = self.pids[0].compute(self.targetTemperature, self.kilnTemps[0])
        # log.debug("====== PID0 " + str(self.pidOut[0])+ " target: "+ str( self.targetTemperature)+ " reported:" +str(self.kilnTemps[0]))
        if self.pidOut[0] > 0:
            # turn heaters on
            log.debug("single PID - all On")
            self.commandedHeaterStates = [HeaterOn, HeaterOn, HeaterOn, HeaterOn]
        else:  # shouldnt have to do this but
            log.debug("single PID - all Off")
            self.commandedHeaterStates = [HeaterOff, HeaterOff, HeaterOff, HeaterOff]


    def doMultiplePID(self):
        log.error("MultiplePID Not Tested")
        # self.commandedHeaterStates = [HeaterOff, HeaterOff, HeaterOff, HeaterOff]
        # # compute individual pidOuts
        # # pidOut[0] true if any true
        # self.pidOut[1] = self.pids[1].compute(self.targetTemperature, self.kilnTemps[1])
        # if self.pidOut[1] > 0:
        #     # turn heaters on
        #     self.commandedHeaterStates[0] = HeaterOn
        #     self.commandedHeaterStates[1] = HeaterOn
        # self.pidOut[2] = self.pids[2].compute(self.targetTemperature, self.kilnTemps[2])
        # if self.pidOut[2] > 0:
        #     # turn heaters on
        #     self.commandedHeaterStates[0] = HeaterOn
        #     self.commandedHeaterStates[2] = HeaterOn
        # self.pidOut[3] = self.pids[3].compute(self.targetTemperature, self.kilnTemps[3])
        # if self.pidOut[3] > 0:
        #     # turn heaters on
        #     self.commandedHeaterStates[0] = HeaterOn
        #     self.commandedHeaterStates[3] = HeaterOn
        pass

    def nextScriptSegment(self):
        self.scriptIndex += 1
        log.debug("nextScriptSegment for kilnScript "+str(self.scriptIndex))
        if self.scriptIndex >= self.myScript.numSteps():
            # ran off end of script.
            # end of runScript
            log.debug("reached end - terminateScript")
            self.terminateScript()
            return
        self.loadScriptStep()
        self.scriptState = KilnScriptState.Heating
        pass

    def command12VRelay(self,cmdState):
        tmpState = cmdState
        if self.simulation == True: # 12v On
            tmpState = False #simulation is always off
        log.debug("Command 12v Relay " + str(cmdState) + " sim: "+str(this.simulation) + " actual:"+str(tmpState))
        self.v12RelayCommanded = tmpState
        moHardware.binaryCmd(relayPower, tmpState)

    def commandExhaustFan(self, cmdState):
        # turn on/off exhaust
        tmpState = cmdState
        if self.simulation == True: # 12v On
            tmpState = False
        log.debug("commandExhaustFan " + str(cmdState) + " sim: "+str(this.simulation) + " actual:"+str(tmpState))
        self.exhaustFanCommanded = tmpState
        moHardware.binaryCmd(fan_exhaust, tmpState)

    def commandSupportFan(self, cmdState):
        # turn on/off support fan
        tmpState = cmdState
        if self.simulation == True: # 12v On
            tmpState = False
        log.debug("commandSupportFan " + str(cmdState) + " sim: "+str(this.simulation) + " actual:"+str(tmpState))
        self.supportFanCommanded = tmpState
        moHardware.binaryCmd(fan_support, tmpState)

    def updateBinaryDevices(self):
        '''map MODAC Binary Output data to local variables'''
        # one call gets all the binaryOut ports and we parse out the ones neede as defined in kilnConfig.py
        binaryOutputs = moData.getValue(keyForBinaryOut())
        self.reportedHeaterStates[1] = binaryOutputs[heater_lower]
        self.reportedHeaterStates[2] = binaryOutputs[heater_middle]
        self.reportedHeaterStates[3] = binaryOutputs[heater_upper]
        self.reportedHeaterStates[0] = self.reportedHeaterStates[1] or self.reportedHeaterStates[2] or self.reportedHeaterStates[3]
        self.exhaustFanState = binaryOutputs[fan_exhaust]
        self.supportFanState = binaryOutputs[fan_support]
        self.v12RelayState = binaryOutputs[relayPower]

    def updateTemperatures(self):
        ''' retrieve thermocouple values degC, avg the ones we want '''
        kTemps = moData.getValue(keyForKType())
        # need to check if KTypes are valid, which should reflect if errors elsewhere in Thermocouple chain
        #error is all values = 0, chk ktypeStatus?

        # print("Kiln ktypes read as: ", kTemps)
        self.kilnTemps[1] = kTemps[kType_lower]
        self.kilnTemps[2] = kTemps[kType_middle]
        self.kilnTemps[3] = kTemps[kType_upper]

        # how we get kiln temp depends on bool from kilnControl/kilnControl.py
        avg = 0
        if kType_avgAll:
            # use the average of 3 ktype thermocouples
            avg = (self.kilnTemps[1] + self.kilnTemps[2] + self.kilnTemps[3]) / 3
            self.kilnTemps[0] = avg
        elif kType_avgTopBottom:
            avg = (self.kilnTemps[1] + self.kilnTemps[3]) / 2
        else:
            # use only the lower (first) ktype = bottom
            avg = self.kilnTemps[1]
        self.kilnTemps[0] = avg
        pass

    def updateDistance(self):
        if self.simulation:
            slumpRate = 0.1 # mm per loop
            if self.state == KilnState.RunningScript and self.scriptState == KilnScriptState.Holding :
                # if we are above critical temp, then slump, unless SupportFan is on
                if self.kilnTemps[0] > this.criticalTemp and self.supportFanCommanded == False:
                    self.currentDistance += slumpRate
        else:
            #lData = moData.getValue(keyForLeicaDisto())
            self.currentDistance = moData.getValue(keyForDistance())
        pass

    def runKilnScript(self, scriptAsJson):
        #log.debug("runKilnScript: "+str(scriptAsJson))
        self.myScript = newScriptFromText(scriptAsJson)
        self.scriptIndex = 0
        self.simulation = self.myScript.simulate
        log.debug("runKilnScript: simulation:"+str(self.simulation))
        moHardware.simulateKiln(self.simulation)
        # moHardware should call this.setSimulation(self.simulation) # because it is in both places
        self.loadScriptStep()

        if self.simulation:
            dist = 1000.0  # 1meter start dist in simulation
            print("Kiln Simulation start dist", dist)
        else:
            # lData = moData.getValue(keyForLeicaDisto())
            #print("startKiln Run leicaPanel.getData = ", lData)
            dist = moData.getValue(keyForDistance())

        # test for no distance data
        if dist <= 0:
            log.warning("No distance data for Distance Sensor, Script run may not work")
        self.startDistance = dist
        self.currentDistance = dist
        self.targetDist = self.startDistance + self.targetDisplacement

        self.state = KilnState.RunningScript
        self.scriptState = KilnScriptState.Heating # figure we always start by heating

        self.scriptStartTime = datetime.datetime.now()
        log.info("Starting Kiln Script .. status:" + json.dumps(self.updateStatus(), indent=4))
        log.info("async kiln loop should pick this up")

    def loadScriptStep(self):
        if self.myScript is None:
            log.error("no kiln script for loading step")
            return
        curSeg = self.myScript.getSegment(self.scriptIndex)
        log.debug("Load Script Step %d: %s"%(self.scriptIndex,str(curSeg)))
        moData.update(keyForIndex(),self.scriptIndex) # as top level moData so it gets to CSV easy

        # copy values from script to internals
        # we use internals and duplicate curSeg/kilnScript to keep it pristine
        # and also because the rest of this was written with local vars first
        # and scriptSegments/steps added later
        self.targetTemperature = curSeg.targetTemperature
        self.targetDisplacement= curSeg.targetDistanceChange
        self.segmentStartTime = datetime.datetime.now()
        self.maxTimeMin = default_maxTime # curSeg.maxTime
        self.maxTimeSec =  default_maxTime* 60 # curSeg.maxTime* 60
        self.step_time = curSeg.stepTime
        self.sleepThisStep = curSeg.stepTime
        self.targetHoldTimeMin = curSeg.holdTimeMinutes
        self.targetHoldTimeSec = self.targetHoldTimeMin * 60
        # set exhaust/support fans? command_X
        self.command12VRelay(curSeg.v12Relay)
        self.commandExhaustFan(curSeg.exhaustFan)
        self.commandSupportFan(curSeg.supportFan)
        # reset runtime vars
        self.startHoldTime = 0  # begin of hold state
        self.startHoldTimeStr = "notHolding"
        self.timeInHoldSeconds = 0
        self.timeInHoldMinutes = 0

    async def twiddleBinaries(self):
        # nasty lil hack to trip kiln heaters when system stops seeing changes
        log.warning("Twiddling heaters")
        log.warning("Initial States "+str(self.commandedHeaterStates))
        # loop several times on/off
        for i in range(5):
            self.allHeatersTo(HeaterOff)
#            await trio.sleep(0.5)
            self.allHeatersTo(HeaterOn)
            await trio.sleep(0.5)
        self.allHeatersTo(self.commandedHeaterStates[1])
        log.warning("After Twiddle States "+str(self.commandedHeaterStates))


    def allHeatersTo(self,state):
        for i in range(1, 4):  # should use len heaters?
            moHardware.binaryCmd(heaters[i], state)


