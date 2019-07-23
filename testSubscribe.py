# modac_io_server v0.3
# replacing server2 from last git commit
# working now on pub/sub server later on the cmd back channel
# moNetwork is key, modac_netLogger is first client
import datetime
from time import sleep
import sys
import os
import logging, logging.handlers
import argparse
import json

# my stuff
from modac import moKeys, moData, moNetwork

loggerInit = False
runTests = False #True
mainLoopDelay = 2 # seconds for sleep at end of main loop

def modac_exit():
    logging.info("modac_exit")
    # anything else?
    exit()

def testSubscriberEventLoop():
    print("event Loop")
    print(moNetwork.subscribers)
    logging.info("Enter Event Loop")
    for i in range(30):
        #update inputs & run filters on data
        log_data()
        # run any filters
        #test_json(inputData)
        moNetwork.receive()
#        moNetwork.receive()        
        sleep(mainLoopDelay)

def log_data():
    moDict = moData.asDict()
    #print("moData:",moDict)
    moJson = json.dumps(moDict, indent=4)
    #print(moJson)
    logging.info(moJson)
    
def testSubscriber():
    logging.info("start testSubscriber()")
    # modac_testLogging()
    # load config files
    modac_loadConfig()
    # argparse ? use to override config files
    modac_argDispatch()
    # initialize data structures
    # initialize GPIO channels
    moData.init()
    moNetwork.startSubscriber()
    # run hardware tests
    # initialize message passing, network & threads
    try:
        #   run event loop
        print("modata:",moData.asDict())
        testSubscriberEventLoop()
    except Exception as e:
        print("Exception somewhere in modac_io_server event loop. see log files")
        logging.error("Exception happened", exc_info=True)
        logging.exception("Exception Happened")
    
    modac_exit()

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

def setupLogging():
    global loggerInit
    print("setupLogging")
    if loggerInit :
        logging.warn("Duplicate call to setupLogging()")
        return
    maxLogSize = (1024 *1000)
    # setup logger
    now = datetime.datetime.now()
    nowStr = now.strftime("%Y%m%d_%H%M%S")
    logName = "modac_"+nowStr+".log"
    logFormatStr = "%(asctime)s [%(threadName)-12.12s] [%(name)s] [%(levelname)-5.5s] %(message)s"
    # setup base level logging to stderr (console?)
    # consider using logging.config.fileConfig()
    # consider using log directory ./log
    logDirName = os.path.join(os.getcwd(),"logs")
    if os.path.exists(logDirName) == False:
        os.mkdir(logDirName)
        
    logName = os.path.join(logDirName, logName)
    print("print Logging to stderr and " + logName)
    
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format=logFormatStr)
    
    rootLogger = logging.getLogger()
    
    logFormatter = logging.Formatter(logFormatStr)
    #consoleHandler = logging.StreamHandler()
    #consoleHandler.setFormatter(logFormatter)
    #rootLogger.addHandler(consoleHandler);
    # chain rotating file handler so logs go to stderr as well as logName file
    fileHandler = logging.handlers.RotatingFileHandler(logName, maxBytes=maxLogSize, backupCount=10)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    
    logging.captureWarnings(True)
    logging.info("Logging Initialized")
    print("Logging Initialized? should have echo'd on line above")
    loggerInit = True
    
  
if __name__ == "__main__":
    modac_argparse() # capture cmd line args to modac_args dictionary for others
    setupLogging() # start logging (could use cmd line args config files)
    print("modac_nngPubSub testing nng publish-subscribe")
    try:
        testSubscriber()
    except Exception as e:
        print("Exception somewhere in modac_io_server. see log files")
        logging.error("Exception happened", exc_info=True)
        logging.exception("huh?")
    finally:
        print("end main")
    modac_exit()
    
