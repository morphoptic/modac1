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

# modac stuff
from modac import moData, moClient, moLogger,moCSV
import logging
moLogger.init("netLogger")
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


mainLoopDelay = 2 # seconds for sleep at end of main loop

def modac_exit():
    log.info("modacExit")
    if moCSV.isOpen():
        moCSV.close()
    moClient.shutdownClient()
    #sys.exit(0)
    
def modac_init():
    # setup MODAC data/networking
    moData.init()
    log.debug("try startClient()")
    moClient.startClient()
    log.debug("client started")

def modac_SubscriberEventLoop():

    print("modac_SubscriberEventLoop Loop")
    log.info("Enter Event Loop")
    for i in range(90): #currently only do a few while we get it running
        log.debug("modac_SubscriberEventLoop - loop %d"%(i))
        if moClient.clientReceive():
            #client received something
            log.debug("should log what was received")
        sleep(mainLoopDelay)

def log_data():
    moDict = moData.asDict()
    print("moData:",moDict)
    moJson = json.dumps(moDict, indent=4)
    print(moJson)
    log.info(moJson)
    
def modac_netLogger():
    log.info("start modac_netLogger()")
    # run hardware tests
    # initialize message passing, network & threads
    try:
        #   run event loop
        modac_SubscriberEventLoop()
    except Exception as e:
        print("Exception somewhere in modac_netLogger event loop. see log files")
        log.error("Exception happened", exc_info=True)
        log.exception("Exception Happened")
    
    modac_exit()


if __name__ == "__main__":
    try:
        modac_init()
        modac_netLogger()
    except Exception as e:
        print("Exception somewhere in modac_netLogger. see log files")
        log.error("Exception happened", exc_info=True)
        log.exception("huh?")
    finally:
        print("end main of modac_netLogger")
    modac_exit()
    

