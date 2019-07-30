# moData = common data repo under mordac
if __name__ == "__main__":
    print("moData has no self test")
    exit(0)
    
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]

import logging, logging.handlers, traceback
#import rest of modac
from .moKeys import *

# locally required for this module
import datetime, json

__moDataDictionary = {}

def init():
    # here we dont init hardware, only data collection
    update(keyForBinaryOut(),None)
    update(keyForEnviro(), None)
    update(keyForAD24(),None)
    update(keyForAD16(), None)
    update(keyForKType(), None)
    update(keyForLeicaDisto(), None)
    print("Initialized moData",rawDict())
    
    # modac_BLE_Laser.init()
    pass

def update(key,value):
    if key == keyForTimeStamp():
        if isinstance(str, datetime.datetime):
            value = value.strftime("%Y-%m-%d %H:%M:%S.%f%Z : ")
    __moDataDictionary[key] = value
    # modac_BLE_Laser.update()
    pass

def asDict():
#    moData = {
#        keyForEnviro():enviro.asDict(),
#        keyForAD24:ad24.all0to5Array(),
#        keyForKType:kType.asArray(),
#        keyForBinaryOutKey.key():binaryOutputs.asArray()
#        }    
    return __moDataDictionary

def asJson():
    return json.dumps(asDict(), indent=4)
                      
def getValue(key):
    # will throw KeyError if key is not in dictionary
    return __moDataDictionary[key]

def rawDict():
    return __moDataDictionary

def updateAllData(d):
    assert isinstance(d, dict)
    for key, value in d.items():
        update(key,value)
    print("Updated: ", asJson())

def logData():
    logging.info(this.asJson())
    

######  for CSV
__namesOfColumns = None
# do this manually or using names?
# bit too complex for dictwriter, given many entries are complex
def __appendArray(key,targetArray):
    a = this.getValue(key)
    targetArray + a
    
def asArray():
    a = []
    a.append(this.getValue(keyForTimeStamp()))
    env = this.getValue(keyForEnviro())
    a.append(env[keyForTemperature()])
    a.append(env[keyForHumidity()])
    a.append(env[keyForPressure()])
    a.append(this.getValue(keyForLeicaDisto()))
    
    a += this.getValue(keyForAD24())
    a += this.getValue(keyForAD16())
    a += this.getValue(keyForKType())
    a += this.getValue(keyForBinaryOut())
    return a

def __appendAName(key):
    print("__appendAName key:", key)
    cPrefix = key
    a = this.getValue(key)
    print("__appendAName a:", a)
    assert isinstance(a, list)
    for i in range(len(a)):
        s = cPrefix+"_"+str(i)
        this.__namesOfColumns.append(s)

def arrayColNames():
    if not this.__namesOfColumns == None:
        return this.__namesOfColumns
    this.__namesOfColumns = []
    this.__namesOfColumns.append(keyForTimeStamp())
    this.__namesOfColumns.append(keyForTemperature())
    this.__namesOfColumns.append(keyForHumidity())
    this.__namesOfColumns.append(keyForPressure())
    this.__namesOfColumns.append(keyForLeicaDisto())
    this.__namesOfColumns.append(keyForTemperature())
    this.__appendAName(keyForAD24())
    this.__appendAName(keyForAD16())
    this.__appendAName(keyForKType())
    this.__appendAName(keyForBinaryOut())
  
    return this.__namesOfColumns
