# modac_OutputDevices
# module to hold and control GPIO OutputDevices
# only those low level ones directly to GPIOZero
# other output/input devices by separate modules
#
# initial version is hard coding crude, later should develop object/class/config channel stuff
# july 14 2019
from gpiozero import OutputDevice
import logging
import sys
from time import sleep


modac_relay0 = OutputDevice(5,active_high=True) # 0 is power outlet
# 1-8 are relay board
modac_relay1 = OutputDevice(21,active_high=False)
modac_relay2 = OutputDevice(20,active_high=False)
modac_relay3 = OutputDevice(16,active_high=False)
modac_relay4 = OutputDevice(12,active_high=False)
modac_relay5 = OutputDevice(7,active_high=False)
modac_relay6 = OutputDevice(8,active_high=False)
modac_relay7 = OutputDevice(25,active_high=False)
modac_relay8 = OutputDevice(24,active_high=False)
modac_relays = [
        modac_relay0,
        modac_relay1,
        modac_relay2,
        modac_relay3,
        modac_relay4,
        modac_relay5,
        modac_relay6,
        modac_relay7,
        modac_relay8
        ]

def outputDevice_init():
    logging.info("modac_initOutputDevices")
    outDevice_allOff()
    
def outDevice_on(deviceId):
    # good place for an assert()
    if deviceId < 0 or deviceId > 8:
        logging.error("outDevice_on Range error for device id {0}".format(deviceId))
        #raise Exception("Unknown OutputDeviceId" +str(deviceId))
        return
    logging.debug("outDev ON "+str(deviceId))
    modac_relays[deviceId].on()
    
def outDevice_off(deviceId):
    if deviceId < 0 or deviceId > 8:
        logging.error("outDevice_off Range error for device id {0}".format(deviceId))
        #raise Exception("Unknown OutputDeviceId" +str(deviceId))
        return
    logging.debug("outDev OFF "+str(deviceId))
    modac_relays[deviceId].off()
    
def outDevice_allOn():
    logging.debug("outDev allOn ")
    for i in range(0,len(modac_relays)):
        outDevice_on(i)

def outDevice_allOff():
    logging.debug("outDev allOff")
    for i in range(0,len(modac_relays)) : #range(0,8):
        outDevice_off(i)

def powerOutlet_on():
    logging.debug("outDev powerOutlet On ")
    outDevice_on(0)
    
def powerOutlet_off():
    logging.debug("outDev powerOutlet Off ")
    outDevice_off(0)

def outDevice_testAll():
    sleepDelay = 0.5 # delay in seconds
    logging.info("outDev outDevice_testAll delay= " +str(sleepDelay))
    
    logging.info("power Outlet on/off")
    powerOutlet_on()
    sleep(sleepDelay)
    powerOutlet_off()
    sleep(sleepDelay)
    
    logging.info("Step each on off w delay")
    for i in range(0,len(modac_relays)):#in range(0,8):
        outDevice_on(i)
        sleep(sleepDelay)
        outDevice_off(i)
        
    logging.info("All on then off w delay")
    outDevice_allOn()
    sleep(sleepDelay)
    outDevice_allOff()

    logging.info("***test catch out of bounds request")
    try:
        for i in range(-5,10):
            print("try ", i)
            outDevice_on(i)
    except IndexError:
        logging.info("caught IndexError in outDevice_testAll()")
    finally:
        print("finally - i get here")
    print("*** and after try/except")
    logging.info("last test = all On Off")
    logging.info("All on then off w delay")
    outDevice_allOn()
    sleep(sleepDelay)
    outDevice_allOff()
    
    logging.info("outDev outDevice_testAll complete")
     

if __name__ == "__main__":
    print("Start Modac OutputDevices stand alone test")
    
    logFormatStr = "%(asctime)s [%(levelname)-5.5s] %(message)s"
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=logFormatStr)
    
    logging.info("modac_OutputDevices.py self test")
    num_relays = len(modac_relays)
    logging.info("modac_outputDevices count is " + str( num_relays))
    
    try:
        outDevice_testAll()
    except Exception as e:
        print("MAIN Exception somewhere in outDevice_testAll. see log files")
        logging.error("Exception happened in outDevice_testAll", exc_info=True)
    

