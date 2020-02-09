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

def isOpen():
    if this._csvWriter == None:
        return False
    return True

def init(filename="modacDataLog.csv"):
    print("moCSV file: ",filename)
    this._csvFile = open(filename, "w")
    this._csvWriter = csv.writer(this._csvFile)
    names = moData.arrayColNames() # arrayNameOnlyAD24
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

def addRow():
    if this.isOpen():
        # gets everything in order
        row = moData.asArray()
        print("csvRow:",row)
        this._csvWriter.writerow(row)
        this._csvFile.flush()

### start of a class that would write desired Named Data in moData to a csv
class modacCSVWriter:
    csvFile = None
    csvWriter = None
    names = []
    
    def __init__(self,filename="modacDataLog.csv",names=None):
        print("moCSV file: ",filename, " names:",names)
        self.csvFile = open(filename, "w")
        self.csvWriter = csv.writer(this._csvFile)
        if self.names == None:
            self.names = moData.arrayColNames()
        print("moCSV columNames ",filename, names)
        self.csvWriter.writerow(names)
        pass

    def close(self):
        if self._csvFile == None:
            return
        self.csvFile.close()
        del self._csvFile
        self.csvFile = None

    def addRow(self):
        if self.isOpen():
            ## select names from moData? how?
            # perhaps do this after create named Channels
            # gotta be some commercial package that uses Channels
            row = moData.asArray()
            #print("logRow:",row)
            self.csvWriter.writerow(row)
            self.csvFile.flush()
        
