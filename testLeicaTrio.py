# testLeicaDisto
"""
Modac testLeicaDisto: unit test for Modac LeicaDisto device in Server
"""
import sys
import logging
from time import sleep
from modac import moLogger
if __name__ == "__main__":
    moLogger.init()
    
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


from modac.moKeys import *
from modac import moData
from modac import leicaDistoAsync as leicaDisto

# for Async we try using trio
import trio

def printMoData():
    print("leicaData:",moData.getValue(keyForLeicaDisto()))
    pass

numberTestIterations = 5
maxRestarts = 10
async def asyncServerLoop(nursery):
    sleepDelay = 5 # delay in seconds
    logging.info("asyncServerLoop  loopdelay= " +str(sleepDelay))
    #print("moDataDict:",moData.rawDict())
    restartCount = 0
    logging.info("start Server loop")
    #await trio.sleep(sleepDelay)
    for i in range(numberTestIterations):
        print("******Server loop %d:"%i)
        printMoData()
        if not leicaDisto.isRunning():
            if not leicaDisto.canRun():
                log.error("LeicaDisto in error state, end serverLoop")
            restartCount += 1
            if restartCount > maxRestarts:
                break
            # restart service
            log.debug("asyncServerLoop spawn runLoop")
            nursery.start_soon(leicaDisto.runLoop)
            # wait for it
            await trio.sleep(5)
        await trio.sleep(sleepDelay)
        while leicaDisto.isRunning():
            printMoData()
            await trio.sleep(sleepDelay)
        log.info("Reset Leica and try again")
        leicaDisto.reset()

    logging.info("test leicaDisto complete")
    leicaDisto.shutdown()

async def testAll():
    print("testAll")
    async with trio.open_nursery() as n:
        moData.init()
        leicaDisto.init()
        # wait for it
        
        print("now start asyncServerLoop soon")
        n.start_soon(asyncServerLoop, n)
        print("nursery running")
    print("testAll, after nursery block")
             
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

