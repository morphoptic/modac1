# moCSV = writes moData to a CSV file

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from .moKeys import *
from . import moData

# locally required for this module
import datetime, csv

__csvFile = None
__csvWriter = None

def isOpen():
    if this.__csvWriter == None:
        return False
    return True

def init(filename="modacDataLog.csv"):
    this.__csvFile = open(filename, "w")
    this.__csvWriter = csv.writer(this.__csvFile)
    names = moData.arrayColNames()
    print("moCSV col Names", names)
    this.__csvWriter.writerow(names)
    pass

def close():
    if this.__csvFile == None:
        return
    this.__csvFile.close()
    del this.__csvFile
    this.__csvFile = None

def addRow():
    if this.isOpen():
        row = moData.asArray()
        #print("logRow:",row)
        this.__csvWriter.writerow(row)
        this.__csvFile.flush()

