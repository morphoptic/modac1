# modac Kiln Controller, built on generic modac data acq & control
#
#  this is based on Oven code found in several github projects.
#  not sure which is the originator but these all seem to share very similar code
#     https://github.com/apollo-ng/picoReflow
#     https://github.com/jbruce12000/kiln-controller
#  this PID controller also looks really close to one in above projects
#     https://github.com/timdelbruegger/freecopter/blob/master/src/python3/pid.py
#  and is based on an article "Improving Beginners PID"
#     http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/
#
#  we link into the modac.moData blackboard of shared data for sensors
#  and can either use direct controls of the BinaryOutput/DA effectors
#  or use the pyNNG network commands, or perhaps the moHardware level commands
#  which would get the commands logged at that level
    
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import time
import random
import datetime

import trio

from . import pidController
from . import schedule as kilnSchedule

from modac import moData, moHardware, moServer
from modac.moKeys import *

print("continue with kiln.kln")

kiln_ktypes = [0, 1, 2] #indices of moData.ktype thermocouples to monitor
kiln_heaters = [1, 2, 3] # indices of BinaryOutput devices to control heaters
kiln_fans = [0, 4, 5] #  # indices of BinaryOutput devices to control fans
# kiln_distance is modac.leicaDisto.distance

kiln_timeStep = 1
emergency_shutoff_temp = 800

########################################################################
#
#   PID parameters

pid_kp = 25  # Proportional
pid_ki = 1088  # Integration
pid_kd = 217  # Derivative 

kiln = None
def startKiln():
    log.debug("startKiln soon")
    this.kiln = Kiln()#simulate=True)
    #nursery.start_soon(this.kiln.runKiln)

def endKiln():
    if this.kiln == None:
        log.debug("endKiln, no kiln")
        return
    this.kiln.abort_run()
    this.kiln = None
    
async def loadAndRun(delayTime= 5,filename="kilnControl/testSchedule.csv"):
    print("\n\nKiln load and run starting, delayTime=",delayTime, filename)
    await trio.sleep(delayTime)
    if this.kiln == None:
        log.error("loadAndRun, no kiln")
        return
    if this.kiln.runLoopStarted == False:
        # no thread running,
        this.kiln.runnable = True
        log.debug("Kiln not running, start it")
        moData.getNursery().start_soon(this.kiln.runKiln)
        await trio.sleep(3)    
    this.schedule = kilnSchedule.Schedule(filename)
    print("Loaded Schedule",this.schedule.timeTargetTempArray)
    this.kiln.run_schedule(this.schedule)
    print("schedule should be running")
    
async def spawnSchedule(time = 5):
    nursery=moData.getNursery()
    if nursery == None:
        log.error("spawnSchedule, no nursery")
        return
#    await trio.sleep(time)
    print("woke and try nurser startsoon %r"%(nursery))
    nursery.start_soon(this.loadAndRun, time) #,"kilnControl/testSchedule.csv")
    print("spawned Schedule")
        
def getTemperature():
    ''' retrieve thermocouple values degC, avg the ones we want '''
    kTemps = moData.getValue(keyForKType())
    log.debug("kTemps = "+str(kTemps))
    log.debug("klin uses "+str(this.kiln_ktypes))
    sum = 0.0
    for idx in this.kiln_ktypes:
        sum += kTemps[idx]
    avg = sum/len(this.kiln_ktypes)
    log.debug("Kiln temp = %d"%(avg))
    return avg

class Kiln:
    '''kiln class is the primary interface for externals.
    It provides for trio type async monitoring and data posting loop
    '''
    STATE_IDLE = "IDLE"
    STATE_RUNNING = "RUNNING"

    def __init__(self, simulate=False, time_step=kiln_timeStep):#, nursery=None):
        # simulation was removed for modac, need it for good testing
        self.simulate = True
        self.time_step = time_step
        self.reset()
        self.runLoopStarted = False
        self.runnable = True
        log.debug("Kiln initialized")

    def reset(self):
        self.schedule = None
        self.currTemp = 0
        self.start_time = 0
        self.runtime = 0
        self.totaltime = 0
        self.target = 0
        self.state = Kiln.STATE_IDLE
        self.set_heat(False)
        self.pid = pidController.PIDController(ki=pid_ki, kd=pid_kd, kp=pid_kp)
        log.debug("Kiln reset")
        self.publishStatus()

    def run_schedule(self, schedule, startat=0):
        log.info("Running schedule %s" % schedule.name)
        self.runnable = True
        self.schedule = schedule
        self.totaltime = schedule.get_duration()
        self.start_time = datetime.datetime.now()
        self.startat = startat * 60
        log.info("Starting Schedule")
        self.state = Kiln.STATE_RUNNING

    def abort_run(self):
        self.reset()
        self.runnable = False
        log.info("abort_run")
        self.publishStatus()
        
    def publishStatus(self):
        log.info("%r"%self.get_state())
        moServer.publishData(keyForKilnState(), self.get_state())
        #moData.update(keyForKilnState(), self.get_state())
        #print("\nPublished status\n")
        
    def kilnStep(self,temperature_count, last_temp, pid):
        if self.state == Kiln.STATE_IDLE:
            return
        runtimeDelta = (datetime.datetime.now() - self.start_time).total_seconds()
        if self.startat > 0:
            self.runtime = self.startat + runtimeDelta;
        else:
            self.runtime = runtimeDelta

        self.currTemp = this.getTemperature()
        # lookup the target temperature at current time
        self.target = self.schedule.get_target_temperature(self.runtime)
        pid = self.pid.compute(self.target,  self.currTemp)

        # FIX - this whole thing should be replaced with
        # a warning low and warning high below and above
        # set value.  If either of these are exceeded,
        # warn in the interface. DO NOT RESET.

        # if we are WAY TOO HOT, shut down
        if(self.currTemp >= emergency_shutoff_temp):
            log.info("emergency!!! temperature too high, shutting down")
            self.abort_run()
            
        #Capture the last temperature value.
        last_temp = self.currTemp 
        
        self.set_heat(pid)
        
        #log, publish and put in data blackboard
        self.publishStatus()
        
        if self.runtime >= self.totaltime:
            log.info("schedule ended, runKiln going idle")
            self.abort_run()
        
    async def runKiln(self):
        print("runKiln starting", self.get_state())
        self.runLoopStarted = True
        log.debug("runKiln")
        temperature_count = 0
        last_temp = 0
        pid = 0
        self.runnable = True
        await trio.sleep(0.5)
        while self.runnable:
            if self.state == Kiln.STATE_IDLE:
                print("kiln loop idle")
                await trio.sleep(3)
            else:
                self.kilnStep(temperature_count, last_temp, pid)
            self.sleepThisStep = self.time_step
            self.publishStatus()
            print("bottom of forever loop sleep for",self.sleepThisStep)
            # post kilnState
            await trio.sleep(self.sleepThisStep)
        #out of while runnable
        self.reset()
        self.runLoopStarted = False
        self.publishStatus()
        log.debug("exit runKiln thread")

    def set_heat(self, value):
        if value > 0:
            self.heat = True
            #value is time to sleep
        else:
            self.heat = False
        # get current heater values
        # if not same as self.heat, change them
        log.debug("turn heat on.off %r "%self.heat)
        bouts = moData.getValue(keyForBinaryOut())
        for idx in kiln_heaters:
            if not bouts[idx] == self.heat:
                #change it
                moHardware.binaryCmd(idx,self.heat)
        
    def get_state(self):
        state = {
            keyForRuntime(): self.runtime,
            keyForTemperature(): self.currTemp,
            keyForTarget(): self.target,
            keyForState(): self.state,
            keyForHeat(): self.heat,
            keyForTotalTime(): self.totaltime,
        }
        return state
    
    def set_state(self,state):
        print("kiln set_state: ", state)
        
        self.runtime = state[keyForRuntime()]
        self.currTemp = state[keyForTemperature()]
        self.target = state[keyForTarget()]
        self.state = state[keyForState()]
        self.heat = state[keyForHeat()]
        self.totaltime = state[keyForTotalTime()]
        
        
        
        
        
        
        