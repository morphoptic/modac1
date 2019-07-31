# moLogger  common logging for Modac
# uses python logging
# TODO: fix this up so it properly gives reports app, module, etc

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
# other system imports
import datetime
import sys
import os
import logging, logging.handlers

__loggerInit = False
def init(name="modac"):
    print("setupLogging")
    if this.__loggerInit :
        logging.warn("Duplicate call to setupLogging()")
        return
    maxLogSize = (1024 *1000)
    # setup logger
    now = datetime.datetime.now()
    nowStr = now.strftime("%Y%m%d_%H%M%S")
    logName = name+nowStr+".log"
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
    this.__loggerInit = True
