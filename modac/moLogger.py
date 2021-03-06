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
import logging, logging.handlers, traceback
#import colorlog


__loggerInit = False
def init(name="modac", level=logging.DEBUG):
    print("setupLogging")
    if this.__loggerInit :
        logging.warning("Duplicate call to setupLogging()")
        return
    # process any parameters ?
    #
    maxLogSize = (1024 *1000)
    # setup logger
    now = datetime.datetime.now()
    nowStr = now.strftime("%Y%m%d_%H%M%S")
    logName = name+nowStr+".log"
    logFormatStr = "%(asctime)s [%(threadName)-12.12s] [%(name)s %(funcName)s %(lineno)d] [%(levelname)-5.5s] %(message)s"
    # setup base level logging to stderr (console?)
    # consider using logging.config.fileConfig()
    # consider using log directory ./log
    logDirName = os.path.join(os.getcwd(),"logs")
    if os.path.exists(logDirName) == False:
        os.mkdir(logDirName)
        
    logName = os.path.join(logDirName, logName)
    print("print Logging to stderr and " + logName)
    
    logging.basicConfig(stream=sys.stderr, level=level, format=logFormatStr)
    
    rootLogger = logging.getLogger()
    
    logFormatter = logging.Formatter(logFormatStr)

    # tried to add colorlog but it seems to be not working right
    #handler = colorlog.StreamHandler()
    #handler = logging.StreamHandler()
    #handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s'+logFormatStr))
    #logging.StreamHandler().setFormatter(colorlog.ColoredFormatter('%(log_color)s'+logFormatStr))

    #consoleHandler = logging.StreamHandler()
    #consoleHandler.setFormatter(logFormatter)
    #rootLogger.addHandler(consoleHandler);

    # chain rotating file handler so logs go to stderr as well as logName file
    fileHandler = logging.handlers.RotatingFileHandler(logName, maxBytes=maxLogSize, backupCount=100)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    #rootLogger.addHandler(handler)

    logging.captureWarnings(True)
    logging.info("Logging Initialized")
    print("Logging Initialized? should have echo'd on line above")
    this.__loggerInit = True
