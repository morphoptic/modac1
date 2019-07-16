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
runTests = True

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
        
#def testBME280():
#    logging.info("test BME temp, pressure, humidity sensor")
#    print("test BME temp, pressure, humidity sensor")
#    for i in range(0,60):
#        modac_BME280.update()
#        hStr = 'Humidity: %0.3f %%rH '% modac_BME280.humidity()
#        tStr = 'Temp: %0.3f °C '% modac_BME280.temperature()
#        pStr = 'Pressure: %0.3f hPa' % modac_BME280.pressure()
#        timeStr = timestamp().strftime("%Y-%m-%d %H:%M:%S.%f%Z : ")
#        msg = timeStr + hStr+tStr+pStr
#        print(msg)
#        logging.info(msg)
#        #print("alt :", bme)
#        sleep(1)

def modac_io_server():
    logging.info("start modac_io_server()")
    # modac_testLogging()
    # load config files
    modac_loadConfig()
    # argparse ? use to override config files
    modac_argDispatch()
    # initialize data structures
    # initialize GPIO channels
    modac_initHardware()

    # run hardware tests
    # initialize message passing, network & threads
    try:
        if runTests == True:
            modac_OutputDevices.outDevice_testAll()
            for i in range(0,6):
                modac_BME280.testBME280()
                
        #   run event loop
        print("event Loop")
    except Exception as e:
        print("Exception somewhere in modac_io_server event loop. see log files")
        logging.error("Exception happened", exc_info=True)
        logging.exception("Exception Happened")
    
    modac_exit()
    
__modac_argparse = argparse.ArgumentParser()
__modac_args = None

def modac_initHardware():
    """ modac_initHardware: Initialize Hardware Drivers based on config structures and hard coded stuff,"""
    logging.info("modac_initHardware")
    # init digital I/O
    modac_OutputDevices.outputDevice_init()
    # init SPI 1&2 (AD/DA HAT)
    # init I2C
    #    BME280
    modac_BME280.init()
    #    not oled, that is other tool
    # modac_BLE_Laser.init()   
    
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

def modac_loadConfig():
    logging.info("modac_loadConfig")

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
    print("logging init in main, should see info")
    try:
        modac_io_server()
    except Exception as e:
        print("Exception somewhere in modac_io_server. see log files")
        logging.error("Exception happened", exc_info=True)
        logging.exception("huh?")
    finally:
        print("end main")
    modac_exit()
    

