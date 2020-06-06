# moCSV = writes moData to a CSV file

# cute hack to use module namespace this.  this.value should work
import sys
this = sys.modules[__name__]

import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from .moKeys import *
from . import moData

# locally required for this module
import datetime, csv

_csvFile = None
_csvWriter = None

timeKey = "time"
timeFormat = "%I:%M:%S%p"

def isOpen():
    if this._csvWriter == None:
        return False
    return True

def init(filename="modacDataLog.csv"):
    print("moCSV file: ",filename)
    this._csvFile = open(filename, "w")
    this._csvWriter = csv.writer(this._csvFile)
    # names = [timeKey] +  moData.arrayColNames() # this was for some odd test
    names =  moData.arrayColNames() # arrayNameOnlyAD24
    #names = moData.arrayNameOnlyAD24()
    print("moCSV col Names", names)
    this._csvWriter.writerow(names)
    this._csvFile.flush()
    pass

def close():
    if this._csvFile == None:
        return
    this._csvFile.close()
    del this._csvFile
    this._csvFile = None
    this._csvWriter = None


def addTimeToRow(row):
    ### add a time column formatted like KISS does its time
    # strptime should be exact opposite of strftime given same format str
    # but apparently it doesnt work on pi
    # but does work later in decimate.csv.py on mac
    dtStr = moData.getTimestamp()
    dt = datetime.datetime.strptime(dtStr, keyForTimeFormat())
    timeStr = datetime.datetime.strftime(dt, timeFormat)
    row[timeKey] = timeStr
    
def addRow():
    if this.isOpen():
        # gets everything in order
        row = moData.asArray()
        #addTimeToRow(row)
        #log.debug("moCSV.addRow: %r" % row)
        this._csvWriter.writerow(row)
        this._csvFile.flush()

