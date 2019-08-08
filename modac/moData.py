# moData = common data repo under mordac
if __name__ == "__main__":
    print("moData has no self test")
    exit(0)
    
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

#import rest of modac
from .moKeys import *

# locally required for this module
import datetime, json

__moDataDictionary = {}

# number of sensors of each type
# we need this early in Client startup
# but wont have actual data until receive from Server
# TODO: set this with config shared with server (original concept of Channels)
def numKType():
    return 3
def numBinaryOut():
    return 9
def numAD24():
    return 8
def numAD16():
    return 4
 

def init():
    # here we dont init hardware, only data collection
    # initial data values required, empty arrays and filled in dict
    d = {keyForTimeStamp():"No Data Yet",
     keyForHumidity():0,
     keyForTemperature():0,
     keyForPressure():0
     }
    # initial values for hardware
    # TODO: ideally it could ask each hardware module but Client wont have hardware
    # so need alternative... perhaps a local function deviceInitValue()
    # that would return the initial value,
    # devices could use moData.deviceInitValue() to initialize internal values
    update(keyForTimeStamp(),"No Data Yet")
    update(keyForBinaryOut(), [0]*this.numBinaryOut())
    update(keyForEnviro(), d)
    update(keyForAD24(), [0.0]*this.numAD24())
    update(keyForAD16(), [0.0]*this.numAD16())
    update(keyForKType(), [0.0]*this.numKType())
    update(keyForLeicaDisto(), {keyForTimeStamp():"No Data Yet", keyForDistance():-1})
    log.info("moData.init = "+asJson())
    
    # modac_BLE_Laser.init()
    pass

def update(key,value):
    if key == keyForTimeStamp():
        if isinstance(str, datetime.datetime):
            value = value.strftime("%Y-%m-%d %H:%M:%S%Z : ")
    this.__moDataDictionary[key] = value
    # modac_BLE_Laser.update()
    pass

def asDict():
    return __moDataDictionary

def asJson():
    return json.dumps(asDict(), indent=4)
                      
def getValue(key):
    # will throw KeyError if key is not in dictionary
    return __moDataDictionary[key]

def rawDict():
    return __moDataDictionary

# use provided dictionary to update values in moData dictionary
# validity of keys is left to update function (if at all)
def updateAllData(d):
    assert isinstance(d, dict)
    for key, value in d.items():
        update(key,value)
    #print("Updated: ", asJson())

def logData():
    log.info(this.asJson())
    

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
    
    leica = this.getValue(keyForLeicaDisto())
    a.append(leica[keyForDistance()])
    
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
    this.__namesOfColumns.append(keyForDistance())
    this.__appendAName(keyForAD24())
    this.__appendAName(keyForAD16())
    this.__appendAName(keyForKType())
    this.__appendAName(keyForBinaryOut())
  
    return this.__namesOfColumns
