# binaryOutputs = module to hold and control binary gpio output
# uses gpiozero OutputDevice

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]

#import rest of modac
#from . import module name
from .moKeys import *
from . import moData
# locally required for this module
from gpiozero import OutputDevice
import logging
from time import sleep

# gpiozero OutputDevices with Binary Values
# note GPIOZero is smart enough to turn all Off when app properly exits

__relay0 = OutputDevice(5,active_high=True) # 0 is power outlet, active on True
# 1-8 are relay board which uses active on low so use active_high=False
__relay1 = OutputDevice(21,active_high=False)
__relay2 = OutputDevice(20,active_high=False)
__relay3 = OutputDevice(16,active_high=False)
__relay4 = OutputDevice(12,active_high=False)
__relay5 = OutputDevice(7,active_high=False)
__relay6 = OutputDevice(8,active_high=False)
__relay7 = OutputDevice(25,active_high=False)
__relay8 = OutputDevice(24,active_high=False)
__relays = [
        __relay0,
        __relay1,
        __relay2,
        __relay3,
        __relay4,
        __relay5,
        __relay6,
        __relay7,
        __relay8
        ]

def init():
    logging.info("modac_initOutputDevices")
    allOff()
    update()
    
def update():
    moData.update(keyForBinaryOut(), asArray())
    pass

def count():
    return len(__relays)

def asArray():
    a = []
    for r in __relays:
        a.append(r.value)
    return a

def asDict():
    return {keyForBinaryOut():asArray()}

def on(deviceId):
    # good place for an assert()
    if deviceId < 0 or deviceId > 8:
        logging.error("binaryOut_on Range error for device id {0}".format(deviceId))
        #raise Exception("Unknown OutputDeviceId" +str(deviceId))
        return
    logging.debug("binaryOut ON "+str(deviceId))
    this.__relays[deviceId].on()
    update()
    
def off(deviceId):
    if deviceId < 0 or deviceId > 8:
        logging.error("binaryOut_off Range error for device id {0}".format(deviceId))
        #raise Exception("Unknown OutputDeviceId" +str(deviceId))
        return
    logging.debug("binaryOut OFF "+str(deviceId))
    this.__relays[deviceId].off()
    update()

def setOutput(channel, onoff):
    if onoff:
        this.on(channel)
    else:
        this.off(channel)

def allOn():
    logging.debug("binaryOut allOn ")
    for i in range(0,len(__relays)):
        this.on(i)

def allOff():
    logging.debug("binaryOut allOff")
    for i in range(0,len(__relays)) : #range(0,8):
        this.off(i)

def powerOutlet_on():
    logging.debug("binaryOut powerOutlet On ")
    this.on(0)
    update()
    
def powerOutlet_off():
    logging.debug("binaryOut powerOutlet Off ")
    this.off(0)
    update()



