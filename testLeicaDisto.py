# testLeicaDisto
"""
Modac testLeicaDisto: unit test for Modac LeicaDisto device in Server
"""
import sys
import logging
from time import sleep
from modac import moLogger
if __name__ == "__main__":
    moLogger.init("testLeica")
    
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


from modac.moKeys import *
from modac import moData
from modac import leicaDistoAsync as leicaDisto

# for Async we try using trio
import trio

async def startLeica(nursery):
    logging.debug("startLeica")
    # leica distance sensor needs to run its own thread/process
    leicaDisto.init()
    nursery.start_soon(leicaDisto.runLoop)
    pass

async def updateLeica(nursery):
    leicaLoopCount =0
    print("UpdateLeica = begin forever loop")
    while True:
        leicalLoopCount += 1
        print("Leica Loop %d"%leicaLoopCount)
        leicaDisto.update()
        await trio.sleep(1)
        if not leicaDisto.isRunning():
            break
    print("end updateLeica")
    pass

def printMoData():
    print("leicaData:",moData.getValue(keyForLeicaDisto()))
    pass

async def asyncServerLoop():
    sleepDelay = 2 # delay in seconds
    logging.info("asyncServerLoop  loopdelay= " +str(sleepDelay))
    #print("moDataDict:",moData.rawDict())
    
    logging.info("start Server loop")
    await trio.sleep(sleepDelay)
    for i in range(numberTestIterations):
        leicaDisto.update()
        log.info("Server loop %d:"%i)
        printMoData()
        if not leicaDisto.isRunning():
            logging.error("Leica not running, end process")
            #leicaDisto.shutdown()
            break
        await trio.sleep(sleepDelay)

    logging.info("test leicaDisto complete")
    leicaDisto.shutdown() #shutdown here in nursery process then die

numberTestIterations = 1200

async def testAll():
    print("testAll")
    moData.init()

    async with trio.open_nursery() as n:
        print("tell nursery to startleica and wait for it to get going")
        await startLeica(n)
        
        # wait for it
        for s in range(10):
            await trio.sleep(1)
        
        print("now start asyncServerLoop soon")
        n.start_soon(asyncServerLoop)
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

