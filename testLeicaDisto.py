# testLeicaDisto
"""
Modac testLeicaDisto: unit test for Modac LeicaDisto device in Server
"""
import sys
import logging
from time import sleep
from modac import leicaDisto, moData

def testAll():
    moData.init()
    leicaDisto.init()
    sleepDelay = 2 # delay in seconds
    logging.info("leicaDisto delay= " +str(sleepDelay))
    print("moDataDict:",moData.rawDict())
    
    logging.info("startread Leica loop")
    for i in range(0,60):#in range(0,8):
        print("loop %d:"%i)
        leicaDisto.update()
        print("moDataDict:",moData.rawDict())
        if leicaDisto.distance() < 0:
            print("Negative, stopping")
            return
        sleep(sleepDelay)

    logging.info("test leicaDisto complete")
     
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

