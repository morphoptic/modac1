# moCommand: commands for moClient to send to moServer
#
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
# other system imports
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import json

#import rest of modac
from .moKeys import *
from . import moData, moNetwork, moClient

def cmdBinary(binOutIdx, onOff):
    assert isinstance(binOutIdx, int)
    assert isinstance(onOff, bool)
    body = (binOutIdx, onOff)
    log.debug("cmdBinary "+keyForBinaryCmd()+" " +str(body))
    moClient.sendCommand(keyForBinaryCmd(), body)
    
def cmdAllOff():
    body = () # no body
    moClient.sendCommand(keyForAllOffCmd(), body)    

def cmdResetLeica():
    body = ()
    moClient.sendCommand(keyForResetLeica(), body)

def cmdRunKilnScript(param={}):
    # new kiln.startRun: takes holdTemp, deflectionDist, maxTime, stepTime
    # these could be fields in Kiln page
    # also should display Kiln.status
    print("cmdRunscriptKiln key=" , keyForRunKilnScript())
    moClient.sendCommand(keyForRunKilnScript(), param)
    
def cmdAbortKiln():
    moClient.sendCommand(keyForKilnAbortCmd(),())
    
def cmdResetLeica():
    moClient.sendCommand(keyForResetLeica(),())

def cmdSimulate(onOff=False):
    # currently not used, no listener. its part of RunKilnCmd
    moClient.sendCommand(keyForSimulate(),(onOff))
    #moHardware.simulateKiln(True)

def cmdEmergencyOff():
    moClient.sendCommand(keyForEmergencyOff(),())
