# modac_netLogger v0.
# first client of pub/sub modac_io_server
# subscribes to pub channel
# logs any messages to file
#
import datetime
from time import sleep
import sys
this = sys.modules[__name__]
import os
import argparse
import json
import signal
import trio #adding async functions use the Trio package
import logging, logging.handlers, traceback

# modac stuff
from modac import moData, moClient, moLogger,moCSV
# moLogger is our frontend/startup to usual Python logging
# we want it to run in main()__main__ before any libraries might
# or they may capture the first call to logging.xxConfig()
# and our main needs priority

if __name__ == "__main__":
    moLogger.init()

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)

mainLoopDelay = 2 # seconds for sleep at end of main loop

def modacExit():
    log.info("modacExit")
    if moCSV.isOpen():
        moCSV.close()
    moClient.shutdownClient()
    #sys.exit(0)

def log_data():
    moDict = moData.asDict()
    print("moData:", moDict)
    moJson = json.dumps(moDict, indent=4)
    print(moJson)
    log.info(moJson)

def signalExit(*args):
    print("signal exit! someone hit ctrl-C?")
    log.error("signal exit! someone hit ctrl-C?")
    modacExit()

def modac_ClientEventLoop():
    log.info("Enter modac_ClientEventLoop")
    for i in range(90): #currently only do a few while we get it running
        log.debug("modac_SubscriberEventLoop - loop %d"%(i))
        if moClient.clientReceive():
            #client received something
            log.debug("should log what was received")
            log_data()
        sleep(mainLoopDelay)
    log.info("modac_ClientEventLoop ended")

def synch_NetLogger():
    # nonNsync Version
    log.info("start modac_netLogger()")
    # initialize message passing, network & threads
    try:
        #   run event loop
        modac_ClientEventLoop()
    except Exception as e:
        print("Exception somewhere in modac_netLogger event loop. see log files")
        log.error("Exception happened", exc_info=True)
        log.exception("Exception Happened")

    modacExit()()

async def modac_asyncClientEventLoop():

    print("modac_SubscriberEventLoop Loop")
    log.info("Enter Event Loop")
    for i in range(90): #currently only do a few while we get it running
        log.debug("modac_SubscriberEventLoop - loop %d"%(i))
        try:
            rcvd = await moClient.asyncClientReceive()
            #client received something. log it?
            if rcvd == True:
                log_data()
        except trio.Cancelled:
            log.debug("Trio Cancelled")
            return
        await trio.sleep(this.mainLoopDelay)
        # skipping try/except and pushing that off on calling routine

async def modacAsyncLogger():
    log.info("start modacLogger()")
    moData.init()
    log.debug("start Nursery startClient()")

    async with trio.open_nursery() as nursery:
        moData.setNursery(nursery)
        moClient.startClient() # open the hailing frequencies
        try:
            #   run event loop
            await modac_asyncClientEventLoop()
        except trio.Cancelled:
           log.warning("***Trio propagated Cancelled to modac_asyncServer, time to die")
        except:
            log.error("Exception caught in the nursery loop: "+str( sys.exc_info()[0]))
            exc = traceback.format_exc()
            log.error("Traceback is: "+exc)
            # TODO need to handle Ctl-C on server better
            # trio has ways to catch it, then we need to properly shutdown spawns
            print("Exception somewhere in modac_io_server event loop.")
            print(exc)
            #traceback.print_exc()#sys.exc_info()[2].print_tb()
    moData.setNursery(None)
    log.debug("modac nursery try died");
    log.error("Exception happened?", exc_info=True)
    modacExit()
    log.debug("client started")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signalExit)

    #from server ...
    # try:
    #    trio.run(modac_asyncServer)
    #except trio.Cancelled:
    #    log.warning("Trio Cancelled - ending server")
    #except Exception as e:
    #    print("Exception somewhere in modac_io_server. see log files")
    #    log.error("Exception happened", exc_info=True)
    #finally:

    try:
        trio.run(modacAsyncLogger)
    except trio.Cancelled:
        log.warning("Trio Cancelled - ending server")
    except Exception as e:
        print("Exception somewhere in modac_netLogger. see log files")
        log.error("Exception happened", exc_info=True)
        log.exception("huh?")
    finally:
        log.warning("end main of modac_netLogger")
    modacExit()
    print("ThThThats All Folks")


