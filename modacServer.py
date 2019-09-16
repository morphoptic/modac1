# modac_io_server testbed for MODAC hardware server
# connects hardware to data and network
# provides pyNNG pubSub publishing of data (see moNetwork)
# provides pyNNG Pair1 command pairing with clients
# note the interfacing is dealt with in the modac modules moData, moNetwork/moCommand, moHardware
import sys
import os
import logging, logging.handlers, traceback
import argparse
import gpiozero
import json
import signal

import trio #adding async

from modac import moLogger
if __name__ == "__main__":
    moLogger.init()
    
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# my stuff
from modac import moKeys, moData, moHardware, moNetwork, moServer, moCSV
import kilnControl

runTests = False #True
publishRate = 2 # seconds for sleep at end of main loop

csvActive = True

def modacExit():
    log.info("modacExit shutting down")
    kilnControl.kiln.endKiln()
    moHardware.shutdown()  # turns off any hardware
    #gpioZero takes care of this: GPIO.cleanup()
    moCSV.close()
    moData.shutdown()
    moServer.shutdownServer()
    log.info("closed everything i think")
    #exit(0)

async def modac_ReadPubishLoop():
    #print("event Loop")
    log.info("\n\nEnter Modac ReadPublish Loop")
    #for i in range(300):
    moData.setStatusRunning()
    while True: # hopefully CtrlC will kill it
        #update inputs & run filters on data
        log.debug("top forever read-publish loop")
        moHardware.update()
        # any logging?
        moData.logData() # log info as json
        if csvActive == True:
            moCSV.addRow()
        # publish data
        moServer.publish()
        log.debug("\n*****bottom forever read-publish loop")
        try:
            await trio.sleep(publishRate)
        except trio.Cancelled:
            log.warn("***Trio Cancelled caught in ReadPublish Loop")
            break
    # after Forever
    log.info("somehow we exited the ReadPublish Forever Loop")

async def modac_asyncServer():
    log.info("start modac_asyncServer()")
    modac_loadConfig()

    # Trio is our async multi-threaded system.
    # it uses the Nursery metaphor for spawning and controlling
    async with trio.open_nursery() as nursery:
        # initialize data blackboard on which data is written and read from
        moData.init(client=False) 
        
        # save the nursey in moData for other modules
        moData.setNursery(nursery)
        
        # pass it nursery so it can start complex sensor monitors like Leica
        await moHardware.init(nursery)
        
        # start the CSV server logging
        moCSV.init("modacServerData.csv")
        
        # we are The Server, theHub, theBroker
        # async so it can spawn CmdListener
        await moServer.startServer(nursery)
        
        # start the kiln control process
        await kilnControl.kiln.startKiln(nursery)
        
        try:
            #   run event loop
            #print("modata:",moData.rawDict())
            await modac_ReadPubishLoop()
        except trio.Cancelled:
           log.warning("***Trio propagated Cancelled to modac_asyncServer, time to die")
        except:
            log.error("Exception caught in the nursery loop: "+str( sys.exc_info()[0]))
            # TODO need to handle Ctl-C on server better
            # trio has ways to catch it, then we need to properly shutdown spawns
            print("Exception somewhere in modac_io_server event loop. see log files")
            print("caught something", sys.exc_info()[0])
            traceback.print_exc()#sys.exc_info()[2].print_tb()
    moData.setNursery(None)
    log.debug("nusery try died");
    log.error("Exception happened", exc_info=True)
    modacExit()

# if we decide to use cmd line args, its 2 step process parsing and dispatch
# parsing happens early to grab cmd line into argparse data model
# dispatching converts the parse tree into modac data/confi settings

def modac_loadConfig():
    log.info("modac_loadConfig")
    pass

def signalExit(*args):
    print("signal exit! someone hit ctrl-C?")
    log.error("signal exit! someone hit ctrl-C?")
    with moData.getNursery() as nursery:
        if nursery == None:
            log.info("signal exit, no nursery")
        else:
            print("nursery still contains ", nursery.child_tasks)
            
    modacExit()
    
if __name__ == "__main__":
    #modac_argparse() # capture cmd line args to modac_args dictionary for others
    moLogger.init() # start logging (could use cmd line args config files)
    print("modac_io_server testbed for MODAC hardware server")
    signal.signal(signal.SIGINT, signalExit)
    try:
        trio.run(modac_asyncServer)
    except Exception as e:
        print("Exception somewhere in modac_io_server. see log files")
        log.error("Exception happened", exc_info=True)
    finally:
        print("end main")
    modacExit()
    

