# moData = common data repo under mordac
# Other modules include this but this doesnt include them

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

from enum import Enum
class moDataStatus(Enum):
    Shutdown = -1
    Startup = 0
    Initialized = 0
    Running = 2

__moDataDictionary = {}

# number of sensors of each type
# we need this early in Client startup
# but wont have actual data until receive from Server
# TODO: set this with config shared with server (original concept of Channels)
# num of entries should be matched in their init and raise error/assert if not same
def numKType():
    return 8
def numBinaryOut():
    return 12
def numAD24():
    return 8
def numAD16():
    return 4

__nursery = None
def setNursery(nursery=None):
    log.debug("setNursery %r"%(nursery))
    this.__nursery = nursery
def getNursery():
    return this.__nursery

def shutdown():
    __moDataDictionary = {keyForStatus():moDataStatus.Shutdown.name}

def init(client=False):
    # here we dont init hardware, only data collection
    # initial data values required, empty arrays and filled in dict
    # initial values for hardware
    # TODO: ideally it could ask each hardware module but Client wont have hardware
    # so need alternative... perhaps a local function deviceInitValue()
    # that would return the initial value,
    # devices could use moData.deviceInitValue() to initialize internal values
    update(keyForStatus(),moDataStatus.Startup.name)
    update(keyForTimeStamp(),"No Data Yet")
    
    # in server individual devices will post their own init values
    # client needs to fake em - which may be maintance issue to keep consistent
    if client == True:
        def_env = {keyForTimeStamp():"No Data Yet",
         keyForHumidity():0,
         keyForTemperature():0,
         keyForPressure():0
         }
        update(keyForEnviro(), def_env)
        update(keyForBinaryOut(), [0]*this.numBinaryOut())
        update(keyForAD24(), [0.0]*this.numAD24())
        update(keyForAD16(), [0.0]*this.numAD16())
        update(keyForKType(), [0.0]*this.numKType())
        def_leica = {keyForTimeStamp():"No Data Yet", keyForDistance():-1}
        update(keyForLeicaDisto(), def_leica)
        def_kiln = {
            keyForState(): 'Closed',
            keyForTimeStep(): 1,
            keyForRuntime(): 0,
            keyForKilnTemps(): [0.0,0.0,0.0,0.0],
            keyForTargetTemp(): 0,
            keyForStartTime(): "Not Started",
            keyForTargetDisplacement(): -1,
            keyForMaxTime(): 0,
            keyForStartDist(): 0,
            keyForCurrDisplacement(): 0,
            keyForTargetDist(): 0,
            keyForKilnHeaters(): [False,False,False,False],
            keyForKilnHeaterCmd(): [False,False,False,False],
        }
        update(keyForKilnStatus(), def_kiln)

        log.info("moData.init = "+asJson())
    
    # modac_BLE_Laser.init()
    pass

def setStatusInitialized():
    update(keyForStatus(),moDataStatus.Initialized.name)

def setStatusRunning():
    update(keyForStatus(),moDataStatus.Running.name)

def updateTimestamp():
    update(keyForTimeStamp(), datetime.datetime.now())
    
def update(key,value):
    if key == keyForTimeStamp():
        if isinstance(value, datetime.datetime):
            value = value.strftime("%Y-%m-%d %H:%M:%S%Z")
    this.__moDataDictionary[key] = value
    # modac_BLE_Laser.update()
    pass

def asDict():
    return __moDataDictionary

def asJson():
    return json.dumps(asDict(), indent=4)

def isValidKey(key):
    if key in __moDataDictionary:
        return True
    return False

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
    if isValidKey(keyForEnviro()):
        env = this.getValue(keyForEnviro())
        a.append(env[keyForTemperature()])
        a.append(env[keyForHumidity()])
        a.append(env[keyForPressure()])
    
    if isValidKey(keyForLeicaDisto()):
        leica = this.getValue(keyForLeicaDisto())
        a.append(leica[keyForDistance()])
    
    if isValidKey(keyForAD24()):
        a += this.getValue(keyForAD24())
    if isValidKey(keyForAD16()):
        a += this.getValue(keyForAD16())
    if isValidKey(keyForKType()):
        a += this.getValue(keyForKType())
    if isValidKey(keyForBinaryOut()):
        a += this.getValue(keyForBinaryOut())
    return a

def __appendAName(key):
    #print("__appendAName key:", key)
    cPrefix = key
    a = this.getValue(key)
    #print("__appendAName a:", a)
    assert isinstance(a, list)
    for i in range(len(a)):
        s = cPrefix+"_"+str(i)
        this.__namesOfColumns.append(s)

def arrayColNames():
    log.debug("modData.arrayColNames - for moCSV")
    if not this.__namesOfColumns == None:
        return this.__namesOfColumns
    this.__namesOfColumns = []
    this.__namesOfColumns.append(keyForTimeStamp())
    if isValidKey(keyForTemperature()):
        this.__namesOfColumns.append(keyForTemperature())
    if isValidKey(keyForHumidity()):
        this.__namesOfColumns.append(keyForHumidity())
    if isValidKey(keyForPressure()):
        this.__namesOfColumns.append(keyForPressure())
    if isValidKey(keyForDistance()):
        this.__namesOfColumns.append(keyForDistance())
    if isValidKey(keyForAD24()):
        this.__appendAName(keyForAD24())
    if isValidKey(keyForAD16()):
        this.__appendAName(keyForAD16())
    if isValidKey(keyForKType()):
        this.__appendAName(keyForKType())
    if isValidKey(keyForBinaryOut()):
        this.__appendAName(keyForBinaryOut())
    log.debug("col names: %r"%(__namesOfColumns))
    return this.__namesOfColumns

def arrayNameOnlyAD24():
    log.debug("modData.arrayNameOnlyAD24 - for testAD24")
    if not this.__namesOfColumns == None:
        log.error("moData columns already named")
        return this.__namesOfColumns
    this.__namesOfColumns = []
    this.__namesOfColumns.append(keyForTimeStamp())
    this.__appendAName(keyForAD24())
    log.debug("col names: %r"%(__namesOfColumns))
    return this.__namesOfColumns

    