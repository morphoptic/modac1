# modac_io_server v0
import datetime
from time import sleep
import sys
import os
import logging, logging.handlers
import argparse
import gpiozero
#others
import modac_OutputDevices
import modac_BME280

loggerInit = False

def modac_exit():
    logging.info("modac_exit")
    #gpioZero takes care of this: GPIO.cleanup()
    # anything else?
    exit()
    
def modac_testLogging():
    for i in range(100):
        #print(i)
        logging.info("I is now %s",i)
        sleep(0.05)
        
def modac_io_server():
    logging.info("start modac_io_server()")
    # modac_testLogging()
    # load config files
    modac_loadConfig()
    # argparse ? use to override config files
    modal_argDispatch()
    # initialize data structures
    # initialize GPIO channels
    modac_OutputDevices.outputDevice_init()
    modac_OutputDevices.outDevice_testAll()
    # initialize message passing, network & threads
    # try
    #   run event loop
    # catch
    #  handle exceptions
    modac_exit()
    
__modac_argparse = argparse.ArguementParser()
__modac_args = None

def modac_initHardware():
    """ modac_initHardware: Initialize Hardware Drivers based on config structures and hard coded stuff,"""
    logging.info("modac_initHardware")
    # init digital I/O
    outputDevice_init()
    # init SPI 1&2 (AD/DA HAT)
    # init I2C
    #    BME280
    #    not oled, that is other tool
    
    
def modac_argparse():
    """ parse command line arguments into global __modac_args """
    logging.info("modac_argparse")
    # add command line arg definitions here
    # then call the parser to shift them into modac_args for later routines.
    __modac_args = __modac_argparse.parse_args()

def modal_argDispatch():
    logging.info("modal_argToConfig")
    # assumes config files & structures are loaded
    # dispatches actions requested by

def modac_loadConfig():
    logging.info("modac_loadConfig")

def setupLogging():
    global loggerInit
    if loggerInit :
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
    print("Logging to stderr and " + logName)
    
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
    
  
if __name__ == "__main__":
    modac_argparse() # capture cmd line args to modac_args dictionary for others
    setupLogging() # start logging (could use cmd line args config files)
    try:
        modac_io_server()
    except Exception as e:
        print("Exception somewhere in modac_io_server. see log files")
        logging.error("Exception happened", exc_info=True)
    modac_exit()
    

