# modac pid Controller, built on generic modac data acq & control
# ripped from picoReflow.Oven
# https://github.com/apollo-ng/picoReflow
#
# pid code based on Oven code found in several github projects.
#  not sure which is the originator but these all seem to share very similar code
#     https://github.com/apollo-ng/picoReflow
#     https://github.com/jbruce12000/kiln-controller
#  this PID controller also looks really close to one in above projects
#     https://github.com/timdelbruegger/freecopter/blob/master/src/python3/pid.py
#  and is based on an article "Improving Beginners PID"
#     http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/
#
#
    
import sys
this = sys.modules[__name__]

import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import datetime

#####################
#
#   PID parameters - common for now, may need separate?
default_kp = 25  # Proportional
default_ki = 1088  # Integration
default_kd = 217  # Derivative

class PIDController:
    def __init__(self, kp = default_kp, ki=default_ki, kd=default_kd):
        self.kp = kp
        self.ki = ki
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

