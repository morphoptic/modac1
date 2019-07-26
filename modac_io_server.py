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
import gpiozero
import json

# my stuff
from modac import moKeys, moData, moHardware, moNetwork

loggerInit = False
runTests = False #True
mainLoopDelay = 2 # seconds for sleep at end of main loop

def modac_exit():
    logging.info("modac_exit")
    moHardware.allOff()
    #gpioZero takes care of this: GPIO.cleanup()
    moNetwork.shutdownNet()
    exit()

def modac_ServerEventLoop():
    print("event Loop")
    logging.info("Enter Event Loop")
    for i in range(300):
        #update inputs & run filters on data
        moHardware.update()
        log_data()
        # run any filters
        #test_json(inputData)
        moNetwork.publish()
        moNetwork.serverReceive()
        sleep(mainLoopDelay)

def test_json(inputData):
    print("------------ write JSON File modacData.json --------")
    with open("modacData.json",'w') as jsonFile:
        json.dump(inputData, jsonFile, indent=4)
        
    print("------------ read JSON File modacData --------")
    with open("modacData.json",'r') as jsonFile:
        data = json.load(jsonFile)
        print("Read: ", data)
        print("asJson: ", json.dumps(data, indent=4))

def log_data():
    moDict = moData.asDict()
    #print("moData:",moDict)
    moJson = json.dumps(moDict, indent=4)
    #print(moJson)
    logging.info(moJson)
    
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
    
    # we are The Server, theHub, theBroker
    moNetwork.startServer()
    
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
        modac_io_server()
    except Exception as e:
        print("Exception somewhere in modac_io_server. see log files")
        logging.error("Exception happened", exc_info=True)
        logging.exception("huh?")
    finally:
        print("end main")
    modac_exit()
    

