# modac pid Controller, built on generic modac data acq & control
# ripped from picoReflow.Oven
#
    
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
print("loading kiln.pidController")

import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import datetime

#import rest of modac
#from modac.moKeys import *
#from modac import moData, moHardware

#import trio

default_kp = 0
default_ki = 0
default_kd = 0
default_state = 0
default_minOutput = 0
default_maxOutput = 1

#mostly direct copy from timdelbruegger github
class PIDController:
    def __init__(self, ki=1, kp=1, kd=1):
        self.ki = ki
        self.kp = kp
        self.kd = kd
        self.lastNow = datetime.datetime.now()
        self.iterm = 0
        self.lastErr = 0

    def compute(self, setpoint, ispoint):
        now = datetime.datetime.now()
        timeDelta = (now - self.lastNow).total_seconds()

        error = float(setpoint - ispoint)
        self.iterm += (error * timeDelta * self.ki)
        self.iterm = sorted([-1, self.iterm, 1])[1]
        dErr = (error - self.lastErr) / timeDelta

        output = self.kp * error + self.iterm + self.kd * dErr
        output = sorted([-1, output, 1])[1]
        self.lastErr = error
        self.lastNow = now

        return output

    
# main for testing
if __name__ == "__main__":
    log.error("kiln.pid Controller has no self test")
