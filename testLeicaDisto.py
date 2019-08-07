# testLeicaDisto
"""
Modac testLeicaDisto: unit test for Modac LeicaDisto device in Server
"""
import sys
import logging
from time import sleep

from modac.moKeys import *
from modac import moData
from modac import leicaDistoAsync as leicaDisto

# for Async we try using trio
import trio

async def startLeica(nursery):
    logging.debug("startLeica")
    leicaDisto.init()
    logging.debug("fork off Leica update")
    nursery.start_soon(updateLeica, nursery)
    pass

async def updateLeica(nursery):
    while True:
        leicaDisto.update()
        await trio.sleep(1)
        if not leicaDisto.isRunning():
            break
    pass

async def printMoData():
    print("leicaData:",moData.getValue(keyForLeicaDisto()))
    pass

async def asyncServerLoop():
    sleepDelay = 2 # delay in seconds
    logging.info("asyncServerLoop  loopdelay= " +str(sleepDelay))
    #print("moDataDict:",moData.rawDict())
    
    logging.info("startread Leica loop")
    for i in range(numberTestIterations):
        print("loop %d:"%i)
        printMoData()
        if not leicaDisto.isRunning():
            logging.error("Leica not running, end process")
            #leicaDisto.shutdown()
            break
        await trio.sleep(sleepDelay)

    logging.info("test leicaDisto complete")
    leicaDisto.shutdown()

numberTestIterations = 1200

async def testAll():
    print("testAll")
    async with trio.open_nursery() as n:
        moData.init()
        print("tell nursery to start leica soon")
        n.start_soon(leicaDisto.initAsync, n)
        
        # wait for it
        for s in range(10):
            await trio.sleep(1)
        
        print("now start asyncServerLoop soon")
        n.start_soon(asyncServerLoop)
             
if __name__ == "__main__":
    print("Start Modac testLeicaDisto stand alone test")
    
    logFormatStr = "%(asctime)s [%(levelname)-5.5s] %(message)s"
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=logFormatStr)
    
    logging.info("testLeicaDisto.py unit test")
    
    try:
        trio.run(testAll)
    except KeyboardInterrupt:
        print("Keyboard Interrupt in trio")
    except:
        print("MAIN Exception somewhere in leicaDisto. see log files")
        logging.error("Exception happened in leicaDisto", exc_info=True)
    print("end Modac testLeicaDisto")
    sys.exit(0)

