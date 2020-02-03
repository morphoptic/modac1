# moJSON - save moData to json text file

import sys
this = sys.modules[__name__]

import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from .moKeys import *
from . import moData

# locally required for this module
import datetime, json

__jsonFile = None

def startJsonLog(baseName = "modacJSON"):
    now = datetime.datetime.now()
    nowStr = now.strftime("%Y%m%d_%H%M")
    filename = baseName+ "_" + nowStr + ".json"
    this.__jsonFile = open(filename, "w")
    startLine = "modac data " + filename + " started " + nowStr
    jDict = {"_comment":startLine}
    log.info("Start Json log " + json.dumps(jDict))
    json.dump(jDict, this.__jsonFile)
    this.__jsonFile.flush()    
    
def snapshot():
    if this.__jsonFile == None:
        log.error("no json file for snapshot")
        return
    dataSnap = moData.asDict()
    tmpDict = { keyForModacCmd():dataSnap}
    print("json.snapsot :" + json.dumps(tmpDict))
    json.dump(tmpDict, this.__jsonFile)
    this.__jsonFile.write("\n")
    this.__jsonFile.flush()

def closeJsonLog():
    now = datetime.datetime.now()
    nowStr = now.strftime("%Y%m%d_%H%M")
    endLine = "{ _comment: end modac JSON "+nowStr + " }"
    json.dump(endLine, this.__jsonFile)
    this.__jsonFile.flush()    
    this.__jsonFile.close()
    this.__jsonFile = None
