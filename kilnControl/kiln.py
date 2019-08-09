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

#import rest of modac
#from modac.moKeys import *
#from modac import moData, moHardware

import trio
print("loading kiln")

from . import schedule, pidController, TempSensor

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

def getTemperature():
    ''' retrieve thermocouple values degC, avg the ones we want '''
    ktypes = moData.getValue(keyForKType())
    sum = 0
    for idx in kiln_ktypes:
        sum += ktypes[idx]
    avg = sum/len(ktypes)
    return avg

class Kiln:
    '''kiln class is the primary interface for externals.
    It provides for trio type async monitoring and data posting loop
    '''
    STATE_IDLE = "IDLE"
    STATE_RUNNING = "RUNNING"

    def __init__(self, simulate=False, time_step=kiln_timeStep):#, nursery=None):
        self.simulate = True
        self.time_step = time_step
        self.reset()
        self.runnable = True

    def reset(self):
        self.schedule = None
        self.start_time = 0
        self.runtime = 0
        self.totaltime = 0
        self.target = 0
        self.state = Kiln.STATE_IDLE
        self.set_heat(False)
        self.pid = pidController.PIDController(ki=pid_ki, kd=pid_kd, kp=pid_kp)

    def run_schedule(self, schedule, startat=0):
        log.info("Running schedule %s" % schedule.name)
        self.schedule = schedule
        self.totaltime = schedule.get_duration()
        self.start_time = datetime.datetime.now()
        self.startat = startat * 60
        log.info("Starting Schedule")
        self.state = Kiln.STATE_RUNNING

    def abort_run(self):
        self.reset()

    def terminate(self):
        self.runnable = False
        
    async def runKiln(self):
        log.debug("runKiln")
        temperature_count = 0
        last_temp = 0
        pid = 0
        while self.runnable:
            if self.state == Kiln.STATE_IDLE:
                #print("idle")
                await trio.sleep(3)
            else:
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
                    self.reset()
                    
                #Capture the last temperature value.
                last_temp = self.currTemp 
                
                self.set_heat(pid)
                
                #log, publish and put in data blackboard
                log.info("%r"%self.get_state())
                moServer.publishData(keyForKilnState(), self.get_state())
                moData.update(keyForKilnState(), self.get_state())
                
                if self.runtime >= self.totaltime:
                    log.info("schedule ended, runKiln going idle")
                    self.reset()
                    #self.terminate()

            # amount of time to sleep with the heater off
            # for example if pid = .6 and time step is 1, sleep for .4s
            if pid > 0:
                self.sleepThisStep = self.time_step * (1 - pid)
            else:
                self.sleepThisStep = self.time_step
            print("bottom of forever loop")
            # post kilnState
            await trio.sleep(self.sleepThisStep)
        #out of while runnable
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
    
    def set_state(state):
        self.runtime = state[keyForRuntime()]
        self.temperature = state[keyForTemperature()]
        self.target = state[keyForTarget()]
        self.state = state[keyForState()]
        self.heat = state[keyForHeat()]
        self.totaltime = state[keyForTotalTime()]
        
        
        
        
        
        
        