# modac_io_server testbed for MODAC hardware server
# connects hardware to data and network
# provides pyNNG pubSub publishing of data (see moNetwork)
# provides pyNNG Pair1 command pairing with clients
# note the interfacing is dealt with in the modac modules moData, moNetwork/moCommand, moHardware
import datetime
from time import sleep
import sys
import os
import logging, logging.handlers, traceback
import argparse
import gpiozero
import json
import signal

# my stuff
from modac import moKeys, moData, moHardware, moNetwork, moServer, moCSV, moLogger

loggerInit = False
runTests = False #True
mainLoopDelay = 2 # seconds for sleep at end of main loop

def modacExit():
    logging.info("modacExit shutting down")
    moHardware.shutdown()  # turns off any hardware
    #gpioZero takes care of this: GPIO.cleanup()
    moCSV.close()
    moServer.shutdownServer()
    exit()

def modac_ServerEventLoop():
    print("event Loop")
    logging.info("Enter Event Loop")
    for i in range(300):
        #update inputs & run filters on data
        moHardware.update()
        moData.logData()
        moCSV.addRow()
        # run any filters
        #test_json(inputData)
        moServer.publish()
        moServer.serverReceive()
        sleep(mainLoopDelay)

def modac_io_server():
    logging.info("start modac_io_server()")
    # modac_testLogging()
    # load config files
    modac_loadConfig()
    # argparse ? use to override config files
    modac_argDispatch()
    # initialize data structures
    # initialize GPIO channels
    moData.init()
    moHardware.init()
    moCSV.init()

    
    # we are The Server, theHub, theBroker
    moServer.startServer()
    
    try:
        #   run event loop
        print("modata:",moData.rawDict())
        modac_ServerEventLoop()
    except Exception as e:
        print("Exception somewhere in modac_io_server event loop. see log files")
        print("caught something", sys.exc_info()[0])
        traceback.print_exc()#sys.exc_info()[2].print_tb()
        logging.error("Exception happened", exc_info=True)
        logging.exception("Exception Happened")
    
    modacExit()

# if we decide to use cmd line args, its 2 step process parsing and dispatch
# parsing happens early to grab cmd line into argparse data model
# dispatching converts the parse tree into modac data/confi settings

__modac_argparse = argparse.ArgumentParser()
__modac_args = None
  
def modac_argparse():
    """ parse command line arguments into global __modac_args """
    #logging.info("modac_argparse")
    # add command line arg definitions here
    # then call the parser to shift them into modac_args for later routines.
    __modac_args = __modac_argparse.parse_args()

def modac_argDispatch():
    logging.info("modac_argDispatch")
    # assumes config files & structures are loaded
    # dispatches actions requested by
    pass

def modac_loadConfig():
    logging.info("modac_loadConfig")
    pass

def signalExit(*args):
    print("signal exit! someone hit ctrl-C?")
    modacExit()
    
if __name__ == "__main__":
    modac_argparse() # capture cmd line args to modac_args dictionary for others
    moLogger.init() # start logging (could use cmd line args config files)
    print("modac_io_server testbed for MODAC hardware server")
    signal.signal(signal.SIGINT, signalExit)
    try:
        modac_io_server()
    except Exception as e:
        print("Exception somewhere in modac_io_server. see log files")
        logging.error("Exception happened", exc_info=True)
        logging.exception("huh?")
    finally:
        print("end main")
    modacExit()
    

