# moData = common data repo under mordac

#### use this to get current and parent directories, and append parent to Python's import path
import sys, os
__dirName__ = os.path.dirname(os.path.abspath(__file__))
__parentDirName__ = os.path.dirname(os.path.abspath(__dirName__))
print("importing " + __dirName__)
print("parentImport " + __parentDirName__)
sys.path.append(__parentDirName__)
#### now we can reference sibling folders

from kilnControl import kilnState  # to get default, if works this is how hw should provide its default status

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Other modules include this but this doesnt include them
# number of sensors of each type
# we need this early in Client startup
# but wont have actual data until receive from Server

# TODO: set this with config shared with server (original concept of Channels)
# num of entries should be matched in their init and raise error/assert if not same
# really should come from some config file, with names too
# perhaps these need to be in the config.py files? moConfig kilnConfig
__numKType = 3
def setNumKType(num):
    __numKType = num
def numKType():
    return this.__numKType
def numBinaryOut():
    return 12
def numAD24():
    return 8
def numAD16():
    return 4

logAsJSON = True

#import rest of modac
from .moKeys import *

# locally required for this module
import datetime, json

from enum import Enum
class moDataStatus(Enum):
    Error = -2
    Shutdown = -1
    Startup = 0
    Initialized = 0
    Running = 2

__moDataDictionary = {}

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

    def_kilnStatus = kilnState.defaultKilnRuntimeStatus()
    update(keyForKilnState(),def_kilnStatus[keyForState()])
    update(keyForKilnScriptState(), def_kilnStatus[keyForKilnScriptState()])

    update(keyForKilnStatus(), def_kilnStatus)

    log.info("moData.init = "+asJson())
    
    # modac_BLE_Laser.init()
    pass

def setStatusInitialized():
    update(keyForStatus(),moDataStatus.Initialized.name)

def setStatusError():
    update(keyForStatus(),moDataStatus.Error.name)

def setStatusRunning():
    update(keyForStatus(),moDataStatus.Running.name)

def getStatus():
    statusName = getValue(keyForStatus())
    status = moDataStatus[statusName]
    return status

def updateTimestamp():
    update(keyForTimeStamp(), datetime.datetime.now())

def getTimeFormat():
    return "%Y-%m-%d %H:%M:%S%Z"

def update(key,value):
    if key == keyForTimeStamp():
        if isinstance(value, datetime.datetime):
            value = value.strftime(getTimeFormat())
    this.__moDataDictionary[key] = value
    # modac_BLE_Laser.update()
    pass

def getTimestamp():
    return getValue(keyForTimeStamp())

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
    #kilnstatus state and scriptState... TODO: do we really go this way with moData/moCSV
    return __moDataDictionary[key]

def rawDict():
    return __moDataDictionary

# use provided dictionary to update values in moData dictionary
# validity of keys is left to update function (if at all)
def updateAllData(d):
    assert isinstance(d, dict)
    #log.debug("updateAllData")
    for key, value in d.items():
        if key == keyForKilnStatus():
            # step thru kilnStatus values to keep order in OrderedDict
            kstatus = this.getValue(keyForKilnStatus())
            #log.debug("updating KilnStatus")
            for kkey in kstatus.keys():
                kstatus[kkey]=value[kkey]
        else:
            update(key,value)
    #this.logData()
    pass

def logData():
    json = this.asJson()
    log.info(json)    

######  for CSV
__namesOfColumns = None
# do this manually or using names?
# bit too complex for dictwriter, given many entries are complex
def __appendArray(key,targetArray):
    a = this.getValue(key)
    targetArray + a
    
def asRowArray():
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
    
    # if isValidKey(keyForAD24Raw()):
    #     a += this.getValue(keyForAD24Raw())
    # if isValidKey(keyForAD24()):
    #     a += this.getValue(keyForAD24())
    if isValidKey(keyForAD16()):
        a += this.getValue(keyForAD16())
    if isValidKey(keyForKType()):
        a += this.getValue(keyForKType())
    if isValidKey(keyForBinaryOut()):
        a += this.getValue(keyForBinaryOut())
    if isValidKey(keyForKilnState()):
        ks = this.getValue(keyForKilnState())
        a.append(ks)
        # this gives string value vs numeric; but thats ok
#        log.debug("addKilnState to row %r"%ks)
    if isValidKey(keyForKilnScriptState()):
        ks = this.getValue(keyForKilnScriptState())
        a.append(ks)
    if isValidKey(keyForIndex()):
        ks = this.getValue(keyForIndex())
        a.append(ks)
#    log.debug("addKilnScriptState to row %r" % ks)
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
    pass

def arrayColNames():
    log.debug("modData.arrayColNames - for moCSV")
    if not this.__namesOfColumns == None:
        return this.__namesOfColumns
    this.__namesOfColumns = []
    this.__namesOfColumns.append(keyForTimeStamp())
    if isValidKey(keyForEnviro()):
        # note: this may cause issues with CSV as Enviro is dict
        #this.__namesOfColumns.append(keyForEnviro())
        this.__namesOfColumns.append(keyForTemperature())
        this.__namesOfColumns.append(keyForHumidity())
        this.__namesOfColumns.append(keyForPressure())
    if isValidKey(keyForTemperature()):
        this.__namesOfColumns.append(keyForTemperature())
    if isValidKey(keyForHumidity()):
        this.__namesOfColumns.append(keyForHumidity())
    if isValidKey(keyForPressure()):
        this.__namesOfColumns.append(keyForPressure())
#    if isValidKey(keyForDistance()):
    if isValidKey(keyForLeicaDisto()):
         this.__namesOfColumns.append(keyForDistance())
    # if isValidKey(keyForAD24Raw()):
    #     this.__appendAName(keyForAD24Raw())
    # if isValidKey(keyForAD24()):
    #     this.__appendAName(keyForAD24())
    if isValidKey(keyForAD16()):
        this.__appendAName(keyForAD16())
    if isValidKey(keyForKType()):
        this.__appendAName(keyForKType())
    if isValidKey(keyForBinaryOut()):
        this.__appendAName(keyForBinaryOut())

    if isValidKey(keyForKilnStatus()):
        # kiln data at top so it gets to CSV
        this.__namesOfColumns.append(keyForKilnState())
        this.__namesOfColumns.append(keyForKilnScriptState())
        this.__namesOfColumns.append(keyForIndex())
    #     log.info("kilnstatus state scriptState added to moData")
    # else:
    #     log.error("Kiln status not found, kilnScriptState not in moData?")
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

# TODO: self test only works with moKeys not .moKeys import at top
if __name__ == "__main__":
    print("moData Self test")
    print("NumKtype: ", numKType())
    print("numBinaryOut: ", numBinaryOut())
    print("numAD24: ", numAD24())
    print("numAD16: ", numAD16())
    this.init(False)
    this.logData()
    exit(0)

