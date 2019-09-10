# modac Kiln Controller, built on generic modac data acq & control
#  links into the modac.moData blackboard of shared data for sensors
#  as such a separate thread could substitute simulated values for ktypes
#
# could be very complex control programming or
#   just do simple case of Heat to Temp, hold till displacement, run fans to cool?
#
#  could either use direct controls of the BinaryOutput/DA effectors
#  or use the pyNNG network commands, or perhaps the moHardware level commands
#  which would get the commands logged at that level
#
#TempControl(target, combined|separate heater|ktype)
#    used in Heating and holding
#    do we need two?
#    
#State:
#    Heating => pid to get to TargetTemp
#    Holding => pid hold TargetTemp, watch Displacement, maxTime
#    Cooling => SupportFan on, ExhaustFan On
#    Idle => wait for command
#    
#    Abort -> returns to Idle State
#    Load Plan: targetTemp, Displacement, maxTime
#
#

import sys
this = sys.modules[__name__]
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import time
import random
import datetime
from enum import Enum

import trio

from . import pidController
from . import schedule as kilnSchedule

from modac import moData, moHardware, moServer
from modac.moKeys import *

#####################
# Binary out configuration
# here we define which BinaryOut have which function

# 12v power to driver side of relays is on BO[0] (controlled power strip)
relayPower = 0  # gpio conrolled power strip

# heaters: may or may not be wired separate or combined
heater_combined = 4
heater_lower = 1
heater_middle = 2
heater_upper = 3

# fans are wired ?? as 12v? as gpio?
fan_supoort = 5  # jet to support glass
fan_exhaust = 6  # heat exhaust fan

#####################
# kType thermocouples: may or may not be wired separate or combined
kType_combined = 4 # all wired to single
kType_lower = 0
kType_middle = 1
kType_upper = 3

#####################
kiln_timeStep = 1 # seconds between kiln read/control (loop delay)

emergency_shutoff_temp = 800  # if kiln ever gets this hot, shutdown and vent

#####################
kiln = None

class KilnState(Enum):
    '''States of the KilnProcess internal to LeicaDisto Module'''
    Closed = 0 # before start and when done w no error
    Error = -1 # done and error occured
    Starting = 1 # between closed and open
    Idle = 2
    Heating = 3
    Holding = 4
    Cooling = 5

#####################
async def startKiln(nursery):
    '''start kiln thread in nursery'''
    log.debug("startKiln soon")
    this.kiln = Kiln()#simulate=True)
    nursery.start_soon(this.kiln.runKiln)

def endKiln():
    '''terminate the kiln thread'''
    if this.kiln == None:
        log.debug("endKiln, no kiln")
        return
    this.kiln.abort_run()
#    this.kiln = None
               
#def getTemperature():
#    ''' retrieve thermocouple values degC, avg the ones we want '''
#    kTemps = moData.getValue(keyForKType())
#    log.debug("kTemps = "+str(kTemps))
#    log.debug("klin uses "+str(this.kiln_ktypes))
#    sum = 0.0
#    for idx in this.kiln_ktypes:
#        sum += kTemps[idx]
#    avg = sum/len(this.kiln_ktypes)
#    log.debug("Kiln temp = %d"%(avg))
#    return avg

class Kiln:
    '''kiln class is the primary interface for externals.
    It provides for trio type async monitoring and data posting loop
    '''
    def __init__(self, time_step=kiln_timeStep):#, nursery=None):
        # simulation was removed for modac, need it for good testing
        self.state = KilnState.Closed
        self.time_step = time_step
        self.reset()
        log.debug("Kiln initialized")
        self.state = KilnState.Starting

    def reset(self):
        self.currTemp = 0
        self.startTime = 0
        self.runtime = 0
        self.totaltime = 0

        self.state = KilnState.Idle
        self.targetTemp = 0
        self.deflectionDist= -1
        self.maxTime = 0
        self.startDist = 0
        self.currDeflection = 0
        self.targetDist = 0
        # only one at present, if use separate kType/Heater, then a Pid needed too
        self.pid = pidController.PIDController()
        log.debug("Kiln reset")
        self.publishStatus()

    def abort_run(self):
        self.reset()
        log.info("abort_run")
        self.publishStatus()
        
        
    def get_status(self):
        status = {
            keyForState(): self.state.name,
            keyForTimeStep(): self.time_step,
            keyForRuntime(): self.runtime,
            keyForTemperature(): self.currTemp,
            keyForTotalTime(): self.totaltime,
            keyForTargetTemp(): self.targetTemp,
            keyForStartTime(): self.startTime,
            keyForDeflectionDist(): self.deflectionDist,
            keyForMaxTime(): self.maxTime,
            keyForStartDist(): self.startDist,
            keyForCurrDeflection(): self.currDeflection,
            keyForTargetDist(): self.targetDist,
        }
        print("KilnStatus:", status)
        return status
    
#    def set_status(self,status):
#        print("kiln set_status: ", status)
#        
#        self.runtime = status[keyForRuntime()]
#        self.currTemp = status[keyForTemperature()]
#        self.target = status[keyForTarget()]
#        self.state = status[keyForState()]
#        self.heat = status[keyForHeat()]
#        self.totaltime = status[keyForTotalTime()]
        
    def publishStatus(self):
        log.info("%r"%self.get_status())
        moData.update(keyForKilnStatus(), self.get_status())
#        moServer.publishData(keyForKilnStatus(), self.get_status())
        
    async def runKiln(self):
        self.state = KilnState.Idle
        print("runKiln starting", self.get_status())
        self.runLoopStarted = True
        log.debug("runKiln")
        temperature_count = 0
        last_temp = 0
        pid = 0
        self.runnable = True
        #await trio.sleep(0.5)
        print("\n\n******")
        print("runKiln starting loop")
        log.debug("runKiln start runnable loop")
        while self.runnable:
            self.kilnStep(temperature_count, last_temp, pid)    
            self.sleepThisStep = self.time_step
            self.publishStatus()
            #print("bottom of forever loop sleep for",self.sleepThisStep)
            # post kilnState
            print("kiln - runnable loop b4 sleep")
            await trio.sleep(self.sleepThisStep)
            print("kiln - runnable loop after sleep\n\n")
            
        log.debug("\n\n******")
        print("runKiln end runnable loop")
        log.debug("runKiln end runnable loop")
        print("\n\n******")
        
        Log.info("Kiln Loop Terminated")
        #out of while runnable
        self.reset()
        self.state = KilnState.Closed
        self.runLoopStarted = False
        self.publishStatus()
        log.info("exit runKiln thread")

    def kilnStep(self,temperature_count, last_temp, pid):
        '''kiln using one input for kType, and one binOut for heaters'''
        
        if self.state == KilnState.Idle:
            print("Kiln idle step")
            return
        # how long since last step?

        runtimeDelta = (datetime.datetime.now() - self.startTime).total_seconds()
        if self.startat > 0:
            self.runtime = self.startat + runtimeDelta;
        else:
            self.runtime = runtimeDelta

        kTemps = moData.getValue(keyForKType())
        self.currTemp = kTemps[kType_combined]
        
        # lookup the target temperature at current time
        
        self.target = self.schedule.get_target_temperature(self.runtime)
        
        pidOut = self.pid.compute(self.target,  self.currTemp)

        # FIX - this whole thing should be replaced with
        # a warning low and warning high below and above
        # set value.  If either of these are exceeded,
        # warn in the interface. DO NOT RESET.

        # if we are WAY TOO HOT, shut down
        if(self.currTemp >= emergency_shutoff_temp):
            log.error("emergency!!! temperature too high, shutting down")
            self.abort_run()
            
        #Capture the last temperature value.
        last_temp = self.currTemp 
        
        self.heat = False
        if (pidOut > 0):
            # turn heaters on
            self.heat = True
        # get current status
        bouts = moData.getValue(keyForBinaryOut())
        if not bouts[heater_combined] == self.heat:
            #change it
            moHardware.binaryCmd(idx,self.heat)
            
        # displacement
        # need to calculate start d vs current d
        
        #log, publish and put in data blackboard
        self.publishStatus()
        
        # determine next step
        deltaT = abs(self.currTemp - self.targetTemp)
        if deltaT < self.tempEpsilon:
            # reached temp, state should be Hold
            self.state = KilnState.Holding

    def startRun(holdTemp, deflectionDist, maxTime):
        self.targetTemp = holdTemp
        self.deflectionDist= deflectionDist
        self.startTime = datetime.datetime.now()
        self.maxTime = maxTime
        
        
        lData = moData.getValue(keyForLeicaDisto())
        print("startKiln Run leicaPanel.getData = ", lData)
        dist = lData[keyForDistance()]

        # test for no data
        if dist <= 0 :
            log.error("No data for Leica, cant run kiln")
            self.state = KilnState.Idle
            return;
        self.startDist = lData[keyForDistance()]
        self.targetDist = self.startDist+ self.deflectionDist
        self.state = KilnState.Heating
        

        
        
        
        
        