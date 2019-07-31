# testClientSender
# tool to test a MODAC Subscriber/ClientSender 
#
import datetime
from time import sleep
import sys
import os
import logging, logging.handlers
import argparse
import json

# my stuff
from modac import moData, moNetwork, moClient, moCommand, moLogger

loggerInit = False
runTests = False #True
mainLoopDelay = 2 # seconds for sleep at end of main loop

def modacExit():
    logging.info("modacExit")
    moClient.shutdownClient()
    exit()

def testClientSender_EventLoop():
    binState = False
    binOutIdx = 0
    print("testClientSender_EventLoop ")
    logging.info("Enter Event Loop")
    for i in range(30): #currently only do a few while we get it running
        logging.debug("testClientSender_EventLoop - iter %d"%(i))
        #update inputs & run filters on data
        # run any filters
        #test_json(inputData)
#        moNetwork.publish()
        moClient.clientReceive()
        if i%2 == 1:
            # even loops toggle BinaryOut 1 = outlet (makes click sound)
            print("Toggle binState: ",binState)
            if binState:
                # turn off
                binState = False
            else:
                # turn on
                binState = True
            moCommand.cmdBinary(binOutIdx, binState)
        sleep(mainLoopDelay)

def log_data():
    moDict = moData.asDict()
    print("moData:",moDict)
    moJson = json.dumps(moDict, indent=4)
    print(moJson)
    logging.info(moJson)
    
def testClientSender():
    logging.info("start testClientSender()")
    # modac_testLogging()
    # load config files
    modac_loadConfig()
    # argparse ? use to override config files
    modac_argDispatch()
    # initialize data structures
    # initialize GPIO channels
    moData.init()
    moClient.startClient()
    # run hardware tests
    # initialize message passing, network & threads
    try:
        #   run event loop
        testClientSender_EventLoop()
    except Exception as e:
        print("Exception somewhere in modac_netLogger event loop. see log files")
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

  
if __name__ == "__main__":
    modac_argparse() # capture cmd line args to modac_args dictionary for others
    moLogger.init("testClientSender") # start logging (could use cmd line args config files)
    print("testClientSender testing both pub/sub data and Pair1 cmd channels")
    try:
        testClientSender()
    except Exception as e:
        print("Exception somewhere in modac_netLogger. see log files")
        logging.error("Exception happened", exc_info=True)
        logging.exception("huh?")
    finally:
        print("end main of modac_netLogger")
    modacExit()
    

