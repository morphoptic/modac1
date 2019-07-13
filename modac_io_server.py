# modac_io_server v0
import datetime
from time import sleep
import sys
import logging, logging.handlers
import gpiozero
#others

loggerInit = False

def setupLogging():
    global loggerInit
    if loggerInit :
        return
    maxLogSize = (1024 *1000)
    # setup logger
    now = datetime.datetime.now()
    nowStr = now.strftime("%Y%m%d_%H%M%S")
    logName = "modac_"+nowStr+".log"
    print(logName)
    # setup base level logging
    logFormatStr = "%(asctime)s [%(threadName)-12.12s] [%(name)s] [%(levelname)-5.5s] %(message)s"
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format=logFormatStr)
    
    rootLogger = logging.getLogger()
    logFormatter = logging.Formatter(logFormatStr)
    # chain rotating file handler so logs go to stderr as well as logName file
    fileHandler = logging.handlers.RotatingFileHandler(logName, maxBytes=maxLogSize, backupCount=10)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    logging.captureWarnings(True)
    logging.info("Logging Initialized")
    loggerInit = True
    
def modac_exit():
    logging.info("modac_exit")
    #gpioZero takes care of this: GPIO.cleanup()
    # anything else?
    exit()
    
def modac_io_server():
    logging.info("start modac_io_server()")
    # argparse
    # load config files
    # initialize data structures
    # initialize GPIO channels
    # initialize message passing, network & threads
    # try
    #   run event loop
    # catch
    #  handle exceptions
    for i in range(10000):
        #print(i)
        logging.info("I is now %s",i)
        sleep(0.05)
    modac_exit()
    
if __name__ == "__main__":
    setupLogging()
    try:
        modac_io_server()
    except Exception as e:
        print("Exception somewhere in modac_io_server. see log files")
        logging.error("Exception happened", exc_info=True)
    modac_exit()
    

