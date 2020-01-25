# convert kTypeTable
# reads csv table from NIST and converts to simpler table for mv->T lookup
import sys
this = sys.modules[__name__]

import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# locally required for this module
import datetime, csv

__csvInFile = None
__csvOutFile = None
__csvReader= None
__csvWriter = None
defaultInName = "type_k_NIST.csv"
#defaultInName = "type_k_NIST_Positive.csv"

def init(filename=defaultInName):
    print("infile: ",filename)
    this.__csvInFile = open(filename, "r")
    this.__csvReader = csv.reader(this.__csvInFile, quoting=csv.QUOTE_NONNUMERIC)
    this.__csvOutFile = open("k_type_Lookup.csv", "w")
    this.__csvWriter = csv.writer(this.__csvOutFile)
    names = ["mv", "degC"]
    print("col Names", names)
    this.__csvWriter.writerow(names)
    pass

def closeUp():
    this.__csvInFile.close()
    this.__csvOutFile.close()
    
def readWrite():
    # while lines available
    # read from In (C mv+0 mv+1 mv+2... mv+9 mv+10)
    inRowCount = 0
    for row in __csvReader:
        print(inRowCount, row)
        if row[0] < 0.0 or row[2] < 0.0:
            print(inRowCount," Ignore Negative Rows")
        inRowCount+=1
    
if __name__ == "__main__":
    #    
    print("MorpOptics convert NIST csv table")
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)#, format=logFormatStr)
    logging.captureWarnings(True)
    logging.info("Logging Initialized for convert NIST csv table")
    init()
    readWrite()
    closeUp()

