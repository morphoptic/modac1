# modac_io_server testbed for MODAC hardware server
# connects hardware to data and network
# inits services and devices, runs update forever loop
# provides pyNNG pubSub publishing of data (see moNetwork)
# provides pyNNG Pair1 command pairing with clients
# note hw interfacing is dealt with in the modac modules moData, moNetwork/moCommand, moHardware
# Trio provides async data handling
# Some hardware, notably blutooth Leica Distance Sensor, require separate threads or processes
import sys
this = sys.modules[__name__]
import os
import logging, logging.handlers, traceback
import argparse
import gpiozero # basic rPi GPIO using gpiozero technique first
import json
import signal
import datetime

import trio #adding async functions use the Trio package

# moLogger is our frontend/startup to usual Python logging
# we want it to run in main()__main__ before any libraries might
# or they may capture the first call to logging.xxConfig()
# and our main needs priority
from modac import moLogger
if __name__ == "__main__":
    moLogger.init()
    
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# my stuff
from modac import moKeys, moData, moHardware, moNetwork, moServer, moCSV, moJSON
import kilnControl

runTests = False #True
#publishRate = 0.25 # seconds for sleep at end of main loop
publishRate = 60.0 # seconds for sleep at end of main loop
publishRate = 1.0 # seconds for sleep at end of main loop
publishRate30 = 30.0 # seconds for sleep at end of main loop

csvActive = True
jsonActive = True
startKilnOnStartup = True
okToRunMainLoop = False

def modacExit():
    log.info("modacExit shutting down")
    this.okToRunMainLoop = False
    kilnControl.kiln.endKilnControlProcess()
    moHardware.shutdown()  # turns off any hardware
    #gpioZero takes care of this: GPIO.cleanup()
    if csvActive:
        moCSV.close()
    if jsonActive:
        moJSON.closeJsonLog()
    moData.shutdown()
    moServer.shutdownServer()
    log.info("closed everything i think")
    #exit(0)

async def modac_ReadPubishLoop():
    #print("event Loop")
    log.info("\n\nEnter Modac ReadPublish Loop")
    #for i in range(300):
    moData.setStatusRunning()
    this.okToRunMainLoop = True
    moData.logData() # log info as json to stdOut/console + logfile
    while this.okToRunMainLoop: # hopefully CtrlC will kill it
        #update inputs & run filters on data
        log.debug("top forever read-publish loop")
        moHardware.update()
        # any logging?
        #moData.logData() # log info as json to stdOut/console + logfile
        # publish data
        moServer.publish()
        #moData.logData()
        if csvActive == True:
            #print("call csvAddRow")
            moCSV.addRow()
        if jsonActive == True:
            #print("call moJSON.snapshot")
            moJSON.snapshot()

        if moServer.receivedHello():
            #this.publishRate = this.publishRate30
            log.info("Someone is listening - set to slower rate " + str(this.publishRate))
        # log.debug("\n*****bottom forever read-publish loop")
        try:
            await trio.sleep(this.publishRate)
        except trio.Cancelled:
            log.warn("***Trio Cancelled caught in ReadPublish Loop")
            break
    # after Forever
    log.info("somehow we exited the ReadPublish Forever Loop")

async def modac_asyncServer():
    log.info("start modac_asyncServer()")
    modac_loadConfig()
    # initialize data blackboard on which data is written and read from
    moData.init(client=False)
    kilnControl.kiln.init() # init here so status gets into moData early; moHardware does lowlevel hw

    # Trio is our async multi-threaded system.
    # it uses the Nursery metaphor for spawning and controlling
    async with trio.open_nursery() as nursery:

        # save the nursey in moData for other modules
        moData.setNursery(nursery)
        
        # pass it nursery so it can start complex sensor monitors like Leica
        await moHardware.init(nursery)
        
        # start the CSV server logging
        if csvActive:
            now = datetime.datetime.now()
            nowStr = now.strftime("%Y%m%d_%H%M")
            outName = "logs/modacServerData_"+nowStr+".csv"
            moCSV.init(outName)
        
        if jsonActive:
            moJSON.startJsonLog("logs/modacServer")
            
        # we are The Server, theHub, theBroker
        # async so it can spawn CmdListener
        await moServer.startServer(nursery)
        
        # Start kiln now or on reciept of StartKiln?
        # start the kiln control process
        if startKilnOnStartup == True:
            await kilnControl.kiln.startKilnControlProcess(nursery)
        else:
            moData.update(moKeys.keyForKilnStatus(), moKeys.keyForNotStarted())

        try:
            #   run event loop
            #print("modata:",moData.rawDict())
            await modac_ReadPubishLoop()
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
    log.debug("nusery try died");
    log.error("Exception happened", exc_info=True)
    modacExit()

# if we decide to use cmd line args, its 2 step process parsing and dispatch
# parsing happens early to grab cmd line into argparse data model
# dispatching converts the parse tree into modac data/confi settings

def modac_loadConfig():
    log.info("modac_loadConfig")
    #TODO kiln_config has some other modules have magic words buried in em
    # come up with consistent way of loading?
    # configuration is done using python code/files
    # generally inline of the module that needs them
    # see modac/moData for things that should work for client and server
    # see kilnControl/kilnConfig for lots of things specific to kiln (also kiln.py)
    # see modacServer (main) for a few like PublishRate
    # see moGui for its publish/read rate
    # see moClient for client timeout on read
    # see moNetwork for addresses and timeouts
    pass

def signalExit(*args):
    print("signal exit! someone hit ctrl-C?")
    log.error("signal exit! someone hit ctrl-C?")
    # with moData.getNursery() as nursery:
    #     if nursery == None:
    #         log.info("signal exit, no nursery")
    #     else:
    #         print("nursery still contains ", nursery.child_tasks)
            
    modacExit()
    
if __name__ == "__main__":
    #modac_argparse() # capture cmd line args to modac_args dictionary for others
    moLogger.init() # start logging (could use cmd line args config files)
    log.info("that may be the 2nd logger init. not a problem")
    print("modac_io_server testbed for MODAC hardware server")
    signal.signal(signal.SIGINT, signalExit)
    try:
        trio.run(modac_asyncServer)
    except trio.Cancelled:
        log.warning("Trio Cancelled - ending server")
    except Exception as e:
        print("Exception somewhere in modac_io_server. see log files")
        log.error("Exception happened", exc_info=True)
    finally:
        print("end main")
    modacExit()
    

