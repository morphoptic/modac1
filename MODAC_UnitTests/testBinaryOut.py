# binaryOutput
import sys
import logging
from time import sleep
from modac import binaryOutputs, moData

if __name__ == "__main__":
    moLogger.init()
    
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def testAll():
    moData.init()
    sleepDelay = 0.5 # delay in seconds
    logging.info("binaryOut binaryOut_testAll delay= " +str(sleepDelay))
    print("moDataDict:",moData.rawDict())
    
    logging.info("power Outlet on/off")
    binaryOutputs.powerOutlet_on()
    sleep(sleepDelay)
    binaryOutputs.powerOutlet_off()
    sleep(sleepDelay)
    print("moDataDict:",moData.rawDict())

    logging.info("Test with on()/off")
    for i in range(0,binaryOutputs.count()):#in range(0,8):
        binaryOutputs.on(i)
        sleep(sleepDelay)
        binaryOutputs.off(i)
    print("moDataDict:",moData.rawDict())
        
    logging.info("Test setOutput")
    for i in range(0,binaryOutputs.count()):#in range(0,8):
        binaryOutputs.setOutput(i,True)
        sleep(sleepDelay)
        binaryOutputs.setOutput(i,False)
    print("moDataDict:",moData.rawDict())
        
    logging.info("All on then off w delay")
    binaryOutputs.allOn()
    sleep(sleepDelay)
    binaryOutputs.allOff()
    print("moDataDict:",moData.rawDict())

    logging.info("***test catch out of bounds request")
    try:
        for i in range(-5,10):
            print("try ", i)
            binaryOutputs.on(i)
    except IndexError:
        logging.info("caught IndexError in binaryOut_testAll()")

    logging.info("last test = all On Off")
    logging.info("All on then off w delay")
    binaryOutputs.allOn()
    sleep(sleepDelay)
    binaryOutputs.allOff()
    print("moDataDict:",moData.rawDict())
    
    logging.info("binaryOut binaryOut_testAll complete")
     

if __name__ == "__main__":
    print("Start Modac OutputDevices stand alone test")
    
    logFormatStr = "%(asctime)s [%(levelname)-5.5s] %(message)s"
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=logFormatStr)
    
    logging.info("modac_OutputDevices.py self test")
    num_relays = binaryOutputs.count()
    logging.info("modac_outputDevices count is " + str( num_relays))
    
    try:
        testAll()
    except Exception as e:
        print("MAIN Exception somewhere in binaryOut_testAll. see log files")
        logging.error("Exception happened in binaryOut_testAll", exc_info=True)
    binaryOutputs.allOff()

