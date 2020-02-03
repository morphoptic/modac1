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

__csvFile = None
__csvWriter = None

def isOpen():
    if this.__csvWriter == None:
        return False
    return True

def init(filename="modacDataLog.csv"):
    print("moCSV file: ",filename)
    this.__csvFile = open(filename, "w")
    this.__csvWriter = csv.writer(this.__csvFile)
    names = moData.arrayColNames() # arrayNameOnlyAD24
    #names = moData.arrayNameOnlyAD24()
    print("moCSV col Names", names)
    this.__csvWriter.writerow(names)
    this.__csvFile.flush()
    pass

def close():
    if this.__csvFile == None:
        return
    this.__csvFile.close()
    del this.__csvFile
    this.__csvFile = None

def addRow():
    if this.isOpen():
        # gets everything in order
        row = moData.asArray()
        #print("logRow:",row)
        this.__csvWriter.writerow(row)
        this.__csvFile.flush()

### start of a class that would write desired Named Data in moData to a csv
class modacCSVWriter:
    csvFile = None
    csvWriter = None
    names = []
    
    def __init__(self,filename="modacDataLog.csv",names=None):
        print("moCSV file: ",filename, " names:",names)
        self.csvFile = open(filename, "w")
        self.csvWriter = csv.writer(this.__csvFile)
        if self.names == None:
            self.names = moData.arrayColNames()
        print("moCSV columNames ",filename, names)
        self.__csvWriter.writerow(names)
        pass

    def close(self):
        if self.__csvFile == None:
            return
        self.__csvFile.close()
        del self.__csvFile
        self.__csvFile = None

    def addRow(self):
        if self.isOpen():
            ## select names from moData? how?
            # perhaps do this after create named Channels
            # gotta be some commercial package that uses Channels
            row = moData.asArray()
            #print("logRow:",row)
            self.__csvWriter.writerow(row)
            self.__csvFile.flush()
        
