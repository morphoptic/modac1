# testLeicaDisto
"""
Modac testLeicaDisto: unit test for Modac LeicaDisto device in Server
"""
import sys
import logging
from time import sleep
from modac import leicaDisto, moData
from modac.moKeys import *

numberTestIterations = 1200
def testAll():
    moData.init()
    leicaDisto.init()
    sleepDelay = 0.5 # delay in seconds
    logging.info("test leicaDisto  loopdelay= " +str(sleepDelay))
    #print("moDataDict:",moData.rawDict())
    
    logging.info("startread Leica loop")
    for i in range(numberTestIterations):
        print("loop %d:"%i)
        leicaDisto.update()
        print("leicaData:",moData.getValue(keyForLeicaDisto()))
        if not leicaDisto.isRunning():
            logging.error("Leica not running")
            leicaDisto.shutdown()
            return
        sleep(sleepDelay)

    logging.info("test leicaDisto complete")
    leicaDisto.shutdown()
     
if __name__ == "__main__":
    print("Start Modac testLeicaDisto stand alone test")
    
    logFormatStr = "%(asctime)s [%(levelname)-5.5s] %(message)s"
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=logFormatStr)
    
    logging.info("testLeicaDisto.py unit test")
    
    try:
        testAll()
    except Exception as e:
        print("MAIN Exception somewhere in leicaDisto. see log files")
        logging.error("Exception happened in leicaDisto", exc_info=True)
    print("end Modac testLeicaDisto")
    sys.exit(0)

