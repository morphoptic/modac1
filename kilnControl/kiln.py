# modac Kiln Controller, built on generic modac data acq & control
#  runs as trio thread on ModacServer having direct control of BinaryOut
#  links into the modac.moData blackboard of shared data for sensors
#  most configuration is in kilnControl.py
#  kilnState.py defines enum class for stateMachine
#
#  currently only does single PID run defined as
#  Heat to Temp, hold till displacement, cool down
#  single or 3 ktypes optional config, all heaters gang on/off
#
# External API:
#  startKiln(nursery) creates Kiln obj, sets up thread
#  endKiln() terminates thread
#  emergencyShutoff() shuts down kiln (12vrelay power)
#  runKilnCmd(params): Cmd handler to run a kiln cycle. params is dictionary of Keys
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
from .kilnState import KilnState

#####################
# singleton really
kiln = None
# are we allowing control
#enableKilnControl = False
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
    endKiln() #terminate thread
    # error state tells it we not running
    this.kiln.state = KilnState.Error
    this.kiln.runnable = False

#####################
# use command to start kiln process
async def startKilnCmd(nursery=None):
    if not this.kiln == None:
        log.error("StartKilnCmd but Kiln already instanced")
        return
    if nursery == None:
        nursery = moData.getNursery()
    await startKiln(nursery)
        

async def startKiln(nursery):
    '''start kiln thread in nursery'''
    if enableKilnControl:
        log.debug("startKiln soon")
        this.kiln = Kiln()#simulate=True)
        nursery.start_soon(this.kiln.runKiln)
    else:
        log.debug("Kiln Control Disabled")

def closeKiln():
    endKiln()
    kiln = None
    log.debug("kiln closed")
    
def endKiln():
    '''terminate the kiln thread'''
    if this.kiln == None:
        log.debug("endKiln, no kiln")
        return
    this.kiln.end_run() #stops run, doesnt terminate thread
    this.kiln.runnable = False # this should terminate thread
    this.kiln.state = KilnState.Closed
    this.kiln.publishStatus() 
    # 
    log.debug("endKiln executed")

#####################

def setRelayPower(onOff= False):
    moHardware.binaryCmd(relayPower, onOff)


def getHeaterStates():
    bouts = moData.getValue(keyForBinaryOut())
    this.lowerHeaterState = bouts[heater_lower]
    this.middleHeaterState = bouts[heater_middle]
    this.upperHeaterState = bouts[heater_upper]
    reportedHeaterStates[1] = this.lowerHeaterState
    reportedHeaterStates[2] = this.middleHeaterState
    reportedHeaterStates[3] = this.upperHeaterState
    
#    if this.lowerHeaterState:
#        heaterStateStr = "lower ON "
#    else:
#        heaterStateStr = "lower OFF "
#    if this.middleHeaterState:
#        heaterStateStr += "middle ON "
#    else:
#        heaterStateStr += "middle OFF "
#    if this.upperHeaterState:
#        heaterStateStr += "upper ON "
#    else:
#        heaterStateStr += "upper OFF "
    return reportedHeaterStates

#####################
# kilnTemps is array of reported temps for our 3 Tcouple + average
# this should be dependent on Num Ktype in kiln but not needed yet
kilnTemps = [0.0,0.0,0.0,0.0] # 0 is avg, 1 lower, 2 middle, 3 upper
def getTemperatures():
    ''' retrieve thermocouple values degC, avg the ones we want '''
    kTemps = moData.getValue(keyForKType())
    #print("Kiln ktypes read as: ", kTemps)
    sum = 0.0
    this.kilnTemps[1] = kTemps[kType_lower]
    this.kilnTemps[2] = kTemps[kType_middle]
    this.kilnTemps[3] = kTemps[kType_upper]
    sum = kilnTemps[1] + kilnTemps[2] + kilnTemps[3]
    avg = sum/3
    
    # how we get kiln temp depends on bool from kilnControl/kilnControl.py
    if kType_avgAll:
        # use the average of 3 ktype thermocouples
        this.kilnTemps[0] = avg
    else:
        # use only the lower (first) ktype = bottom
        this.kilnTemps[0] = this.kilnTemps[1] 

    tempStr = keyForKilnTemps() +":"
    for i in range(len(this.kilnTemps)):
        tempStr += "{0:5.2f} ".format(this.kilnTemps[i])
    log.debug("Kiln get temps = "+ tempStr)
    #print("KilnTemps", this.kilnTemps)
    return this.kilnTemps

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
    # we havent built 3 PID version yet
    commandedHeaterStates = [HeaterOff, HeaterOff, HeaterOff, HeaterOff]
    
    def __init__(self, time_step=default_stepTime):#, nursery=None):
        # simulation was removed for modac, need it for good testing
        self.runnable = False
        self.state = KilnState.Closed
        self.time_step = time_step
        self.reset()
        log.debug("Kiln initialized")
        self.state = KilnState.Starting
        self.tempertureEpsilon = -2.0

    def reset(self):
        self.currTemp = 0
        self.startTime = 0
        self.runtime = 0
        self.totaltime = 0

        self.state = KilnState.Idle
        self.targetTemp = 0
        self.targetDisplacement= -1
        self.currentDisplacement = 0
                
        self.targetHoldTime = 0 # minutes to hold at target temp
        self.startHoldTime = 0  # begin of hold state
        self.timeInHold = 0
        
        self.maxTimeMin = 0
        self.maxTimeSec = 0
        self.startDistance = 0
        self.currentDistance = 0
        self.targetDist = 0
        self.reportedHeaterStates = [False, False, False, False]
        self.commandedHeaterStates = [HeaterOff, HeaterOff, HeaterOff, HeaterOff]
        self.kilnStartTemps = getTemperatures()
        self.kilnTemps = self.kilnStartTemps #[0,0,0,0]
        self.pidOut = [0, 0, 0, 0]
        self.pids = [None, None, None, None]
        self.pids[0] = pidController.PIDController()
        if not self.useSinglePID:
            self.pids[1] = pidController.PIDController()
            self.pids[2] = pidController.PIDController()
            self.pids[3] = pidController.PIDController()
        log.debug("Kiln reset")
        self.publishStatus()

    def end_run(self):
        log.info("kiln.end_run()")
        # should turn off all heaters
        moHardware.binaryCmd(heater_lower, HeaterOff)
        moHardware.binaryCmd(heater_middle, HeaterOff)
        moHardware.binaryCmd(heater_upper, HeaterOff)
        self.reset()
        #self.runnable = False  # this should stop loop & kill thread
        # turn off 12v Power
        setRelayPower(False)
        # and turn off simulation
        moHardware.simulateKiln(False)
        self.publishStatus()      
        log.info("end_run")
       
    def get_status(self):
        startTimeStr =" NotStarted"
        if isinstance(self.startTime, datetime.datetime):
            startTimeStr = self.startTime.strftime("%Y-%m-%d %H:%M:%S%Z")
        
        status = {
            # a few with no shared keys - for debug purposes
            # default values set in moData so not dependent on this file
            "kilnRunnable": self.runnable,
            "kilnSimulation": this.simulation,
            "kiln CurDist": self.currentDistance,
            "kiln StartTemp0": self.kilnStartTemps[0],
            keyForTimeStamp():  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S%Z"),

            keyForState(): self.state.name,
            keyForTargetTemp(): self.targetTemp,
            keyForTargetDisplacement(): self.targetDisplacement,
            keyForTimeStep(): self.time_step,
            keyForMaxTime(): self.maxTimeMin,
            
            keyForKilnHoldTime(): self.targetHoldTime,
            keyForKilnTimeInHold(): self.timeInHold,

            keyForRuntime(): self.runtime,
            keyForStartTime(): startTimeStr,
            
            keyForStartDist(): self.startDistance,
            keyForTargetDist(): self.targetDist,
            
            keyForCurrDisplacement(): self.currentDisplacement,
            
            keyForKilnHeaters(): self.reportedHeaterStates,
            keyForKilnHeaterCmd(): self.commandedHeaterStates,
            keyForKilnTemps(): self.kilnTemps,
        }
        #print("KilnStatus:", status)
        return status
    
        
    def publishStatus(self):
        '''Put KilnStatus into moData, does NOT publish separate cmd'''
        log.info("Publish Kiln Status %r"%self.get_status())
        moData.update(keyForKilnStatus(), self.get_status())
#        moServer.publishData(keyForKilnStatus(), self.get_status())
    
    async def runKiln(self):
        self.state = KilnState.Idle
        log.info("\n\n****** RunKiln starting Kiln Status %r"%self.get_status())
        self.runLoopStarted = True
        log.debug("runKiln")
        
        temperature_count = 0
        last_temp = 0
        pid = 0
        self.runnable = True
        # record temps at start of run, cooling back to this sets state to Idle
        self.kilnStartTemps = getTemperatures()

        #await trio.sleep(0.5)
        print("runKiln starting loop")
        log.debug("runKiln start runnable loop")
        while self.runnable:
            self.kilnStep(temperature_count, last_temp, pid)    
            self.sleepThisStep = self.time_step
            self.publishStatus()
            #print("bottom of forever loop sleep for",self.sleepThisStep)
            # post kilnState
            
            await trio.sleep(self.sleepThisStep)
            
        log.debug("\n\n******")
        print("runKiln end runnable loop")
        log.info("runKiln end forever loop")
        print("\n\n******")
        
        #out of while runnable
        self.reset()
        self.state = KilnState.Closed
        self.runLoopStarted = False
        self.publishStatus()
        log.info("exit runKiln thread")

    def kilnStep(self,temperature_count, last_temp, pid):
        '''kiln using one input for kType, and one binOut for heaters'''
        currentTime = datetime.datetime.now()
        
        # update the inputs
        self.reportedHeaterStates = getHeaterStates()
        self.kilnTemps = getTemperatures()
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
            return
        
        log.info("kilnStep not Idle = " + str(self.state))
        
        # how long since last step?
        self.runtime = (currentTime - self.startTime).total_seconds()

        if (self.runtime >= self.maxTimeSec):
            log.error("Max Time for run exceeded, abort run")
            self.end_run()
            return;

        # 
        if self.state == KilnState.EndRun:
            # hold EndRun for a bit to let UI/monitors know
            if (self.runtime - self.endRunStart) >= endRunHoldTime:
                self.state = KilnState.Idle
                log.debug("Kiln state change EndRun > Idle")
                #anything else need reset?
            return
        
        # Cooling completes when kiln returns to avg start temp
        # drop to EndRun state
        if self.state == KilnState.Cooling :
            if self.kilnTemps[0] <= (self.kilnStartTemps[0]+0.1):
                log.info("Cooling kiln has reached start temp, switch to EndRun")
                log.debug("Kiln state change Cooling > EndRun")
                self.state = KilnState.EndRun
                self.endRunStart = self.runtime
                self.kilnTemps = self.kilnStartTemps
                moHardware.simulateKiln(False) # regardless of current state, reset this and kType
            # regardless, in cooling dont bother with PID
            return

        if self.state == KilnState.Holding :
            # holding at target temp, how long we been here?
            # self.targetHoldTime = 0 # minutes to hold at target temp, default 0 = ignore
            log.debug("Kiln HOLDING started at "+str(self.startHoldTime) +" cur:"+str(currentTime))
            self.timeInHold = (currentTime - self.startHoldTime).total_seconds() #/ 60.0
            log.debug("Kiln Holding, target " +str(self.targetHoldTime)+ " In Hold" +str(self.timeInHold))
            
            if self.targetHoldTime > 0.0 and self.timeInHold > self.targetHoldTime :
                # hold time given and exceeded
                log.info("Hold Time reached, begin Cooling")
                self.startCooling()
 
        # test if reached hold temp +- some epsilon
        if self.state == KilnState.Heating and self.targetTemp <= self.kilnTemps[0] :
            #+ self.tempertureEpsilon:
            # reached temp, state should be Hold
            self.state = KilnState.Holding
            self.startHoldTime = currentTime
            log.debug("Kiln Switch to Holding State "  +str(currentTime))
            
        # pdate PID/Heater control
        # shouldnt get here if state isnt Heating or Holding, but test anyway
        if self.state == KilnState.Heating or self.state == KilnState.Holding:
            # update PIDs
            self.commandedHeaterStates[0] = HeaterOff
            self.commandedHeaterStates[1] = HeaterOff
            self.commandedHeaterStates[2] = HeaterOff
            self.commandedHeaterStates[3] = HeaterOff
            if self.useSinglePID:
                #using only the 0 index wich may be avg or paritular ktype to control PID
                self.pidOut[0] = self.pids[0].compute(self.targetTemp,  self.kilnTemps[0])
                log.debug("======")
                print("PID 0: ", self.pidOut[0], self.targetTemp, self.kilnTemps[0])
                if (self.pidOut[0] > 0):
                    # turn heaters on
                    self.commandedHeaterStates[0] = HeaterOn
                    self.commandedHeaterStates[1] = HeaterOn
                    self.commandedHeaterStates[2] = HeaterOn
                    self.commandedHeaterStates[3] = HeaterOn
            else:
                # compute individual pidOuts
                # pidOut[0] true if any true
                self.pidOut[1] = self.pids[1].compute(self.targetTemp,  self.kilnTemps[1])
                if (self.pidOut[1] > 0):
                    # turn heaters on
                    self.commandedHeaterStates[0] = HeaterOn
                    self.commandedHeaterStates[1] = HeaterOn
                self.pidOut[2] = self.pids[2].compute(self.targetTemp,  self.kilnTemps[2])
                if (self.pidOut[2] > 0):
                    # turn heaters on
                    self.commandedHeaterStates[0] = HeaterOn
                    self.commandedHeaterStates[2] = HeaterOn
                self.pidOut[3] = self.pids[3].compute(self.targetTemp,  self.kilnTemps[3])
                if (self.pidOut[3] > 0):
                    # turn heaters on
                    self.commandedHeaterStates[0] = HeaterOn
                    self.commandedHeaterStates[3] = HeaterOn
            # common code to command heaters to change, but only if needed
            self.updateHeaters()
            for i in range(1,4):
                if not self.reportedHeaterStates[i] == self.commandedHeaterStates[i]:
                    log.info("kiln cmd heater change %d"%i)
                    moHardware.binaryCmd(heaters[i], self.commandedHeaterStates[i])
        # bottom of step

        # displacement test - have we reached slump distance?
        if this.simulation:
            slumpRate = 0.1 # mm per loop
            if self.state == KilnState.Holding:
                self.currentDistance += slumpRate
        else:
            lData = moData.getValue(keyForLeicaDisto())
            self.currentDistance = lData[keyForDistance()]
            
        self.currentDisplacement = self.currentDistance - self.startDistance
        
        # if displacement target reached state = Cooling
        # if our current is close enough to target, being cooling 
        if (self.currentDisplacement + distanceEpsilon) >= self.targetDisplacement:
            self.startCooling()
            
        #log, publish and put in data blackboard
        #self.publishStatus()
        
    def updateHeaters(self):
        for i in range(1,4):
            if not self.reportedHeaterStates[i] == self.commandedHeaterStates[i]:
                log.info("kiln cmd heater change %d"%i)
                moHardware.binaryCmd(heaters[i], self.commandedHeaterStates[i])
                
    def startCooling(self):
        # start cooling
        self.state = KilnState.Cooling
        self.commandedHeaterStates[0] = HeaterOff
        self.commandedHeaterStates[1] = HeaterOff
        self.commandedHeaterStates[2] = HeaterOff
        self.commandedHeaterStates[3] = HeaterOff
        self.updateHeaters()
        #self.target = 0 # room temp, ignore?
        # turn on exhaust
        moHardware.binaryCmd(fan_exhaust, HeaterOn)
        # turn on support
        moHardware.binaryCmd(fan_support, HeaterOn)


    def startRun(self,holdTemp=default_holdTemp,
                 targetDisplacement=default_targetDisplacement,
                 maxTime = default_maxTime,
                 stepTime= default_stepTime, holdTime=0):

        self.targetTemp = holdTemp
        self.targetDisplacement= targetDisplacement
        self.startTime = datetime.datetime.now()
        self.maxTimeMin = maxTime
        self.maxTimeSec = maxTime* 60
        self.step_time =  stepTime
        self.targetHoldTime = holdTime
        
        if this.simulation :
            dist = 1000.0 # 1meter start dist in simulation
            print("Kiln Simulation start dist", dist)
        else:
            lData = moData.getValue(keyForLeicaDisto())
            print("startKiln Run leicaPanel.getData = ", lData)
            dist = lData[keyForDistance()]

        # test for no data
        if dist <= 0 :
            log.error("No data for Leica, Kiln run may not work")
            self.state = KilnState.Idle
            #return;
        self.startDistance = dist
        self.currentDistance = dist
        self.targetDist = self.startDistance + self.targetDisplacement
        
        setRelayPower(True)

        self.state = KilnState.Heating
        log.info("Starting Kiln run.. status:"+ str(self.get_status()))
        log.info("async kiln loop should pick this up")
        
def runKilnCmd(params):
    '''handler for interprocess command to run a kiln cycle. params is dictionary of Keys'''
    print("\n\n*****runKilnCmd", params)
    if this.kiln == None:
        log.error("No Kiln found")
        return
    try:
        simulate = params[keyForSimulate()]
        # moHardware tells kTypes to simulate values and Kiln to use sim processing
        moHardware.simulateKiln(simulate)
        
        targetT = params[keyForTargetTemp()]
        displacement = params[keyForTargetDisplacement()]
        maxTime = params[keyForMaxTime()]
        timeStep = params[keyForTimeStep()]
        holdTime = params[keyForKilnHoldTime()]
        this.kiln.startRun(targetT, displacement, maxTime, timeStep, holdTime)
    except:
        log.error("Bad Parameters: "+ params.ToString())
        
    
        
        
        