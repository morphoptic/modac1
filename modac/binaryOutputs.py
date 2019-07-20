# binaryOutputs = module to hold and control binary gpio output
# uses gpiozero OutputDevice

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
#import rest of modac
#from . import module name

# locally required for this module
from gpiozero import OutputDevice
import logging
from time import sleep

__key = "binaryOut"
def key():
    return __key;

def topic():
    return __key.encode() # encode as binary UTF8 bytes


__relay0 = OutputDevice(5,active_high=True) # 0 is power outlet
# 1-8 are relay board
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
    
def update():
    pass

def asArray():
    a = []
    for r in __relays:
        a.append(r.value)
    return a

def asDict():
    return {__key():asArray()}
    
def on(deviceId):
    # good place for an assert()
    if deviceId < 0 or deviceId > 8:
        logging.error("outDevice_on Range error for device id {0}".format(deviceId))
        #raise Exception("Unknown OutputDeviceId" +str(deviceId))
        return
    logging.debug("outDev ON "+str(deviceId))
    this.__relays[deviceId].on()
    
def off(deviceId):
    if deviceId < 0 or deviceId > 8:
        logging.error("outDevice_off Range error for device id {0}".format(deviceId))
        #raise Exception("Unknown OutputDeviceId" +str(deviceId))
        return
    logging.debug("outDev OFF "+str(deviceId))
    this.__relays[deviceId].off()
    
def allOn():
    logging.debug("outDev allOn ")
    for i in range(0,len(__relays)):
        this.on(i)

def allOff():
    logging.debug("outDev allOff")
    for i in range(0,len(__relays)) : #range(0,8):
        this.off(i)

def powerOutlet_on():
    logging.debug("outDev powerOutlet On ")
    this.on(0)
    
def powerOutlet_off():
    logging.debug("outDev powerOutlet Off ")
    this.off(0)

def testAll():
    sleepDelay = 0.5 # delay in seconds
    logging.info("outDev outDevice_testAll delay= " +str(sleepDelay))
    
    logging.info("power Outlet on/off")
    this.powerOutlet_on()
    sleep(sleepDelay)
    this.powerOutlet_off()
    sleep(sleepDelay)
    
    logging.info("Step each on off w delay")
    for i in range(0,len(__relays)):#in range(0,8):
        this.on(i)
        sleep(sleepDelay)
        this.off(i)
        
    logging.info("All on then off w delay")
    this.allOn()
    sleep(sleepDelay)
    this.allOff()

    logging.info("***test catch out of bounds request")
    try:
        for i in range(-5,10):
            print("try ", i)
            this.on(i)
    except IndexError:
        logging.info("caught IndexError in outDevice_testAll()")

    logging.info("last test = all On Off")
    logging.info("All on then off w delay")
    this.allOn()
    sleep(sleepDelay)
    this.allOff()
    
    logging.info("outDev outDevice_testAll complete")
     

if __name__ == "__main__":
    print("Start Modac OutputDevices stand alone test")
    
    logFormatStr = "%(asctime)s [%(levelname)-5.5s] %(message)s"
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=logFormatStr)
    
    logging.info("modac_OutputDevices.py self test")
    num_relays = len(__relays)
    logging.info("modac_outputDevices count is " + str( num_relays))
    
    try:
        this.testAll()
    except Exception as e:
        print("MAIN Exception somewhere in outDevice_testAll. see log files")
        logging.error("Exception happened in outDevice_testAll", exc_info=True)
    this.allOff()

