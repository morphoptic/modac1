# MODAC keywords
# common file to hold data name keys and convert them to topics and labeled JSON data, also ties to GUI builder

# topics are UTF8 encoded arrays
def moKeyToTopic(key):
    assert isinstance(key,str)
    return key.encode('utf8')

def keyForNotStarted():
    return "NotStarted"

# at this point we are really only using AllData and Cmd for net comms
# but other keys are used for getting data from the moData active data repository
def keyForAllData():
    return "allData"
def keyForShutdown():
    return "shutdown"

# generic keys used by various components
# timestamp key used for all data, enviro and leicaDisto
def keyForTimeStamp():
    return "timestamp"
# Generic key for State used by any state machine in its own context
def keyForState():
    return 'State'
def keyForStatus():
    return "Status"
def keyForScript():
    return "Script"
def keyForIndex():
    return "Index"

# these are data from Enviro Sensor (BMEchip)
def keyForEnviro():
    return "enviro"
def keyForHumidity():
    return "humidity"
def keyForTemperature():
    return "temperature"
def keyForPressure():
    return "pressure"

# array of Binary Outputs - relays etc 
def keyForBinaryOut():
    return "binaryOut"

# Two types of AnalogDigital Converters, with minimal control provided
# AD16 holds array of 16bit AD input channels  generally 0-5v measure
def keyForAD16():
    return "ad16"

# AD24 holds array of 24bit input channels  generally 0-5v measure
def keyForAD24():
    return "ad24"
def keyForAD24Raw():
    return "ad24Raw"
def keyForAD24v05():
    return "ad24v05"

# array of K Type Thermocouple channels DegC units
def keyForKType():
    return "kType"

# Leica Disto D1 distance sensor
def keyForLeicaDisto():
    return "leicaD1"
def keyForDistance():
    return "distance"

#keys for commands from clients
def keyForModacCmd():
    return "modac"
def keyForBinaryCmd():
    return "binaryCmd"
def keyForAllOffCmd():
    return "allOff"
def keyForResetLeica():
    return "leicaReset"

# kiln commands, status, state stuff
## start/abort cmd == btn name but be kinda explicit
def keyForStartKilnProcess(): return "StartKilnProcess"
def keyForEndKilnProcess(): return "EndKilnProcess"
# start, end a script
def keyForRunKilnScript(): return "RunKilnScript"
def keyForStopKilnScript(): return "StopKilnScript"

# kiln data
def keyForKilnStatus(): return "KilnStatus"  # full status of kiln data, hierarchial dict
# kilnState uses keyForState()
def keyForKilnScriptState(): return "KilnScriptState";
def keyForKilnRuntime(): return 'KilnProcessRuntime'

# kiln Script controls
def keyForTargetTemp(): return 'KilnTargetTemp'
def keyForKilnHoldTime(): return 'KilnHoldTime'
def keyForTargetDisplacement():return 'KilnTargetDisplacement'
def keyForMaxTime():return 'KilnMaxTime'
def keyForTimeStep(): return "TimeStep"
def keyForSegmentIndex(): return 'SegmentIndex'

# kiln Script segment status entries
def keyForStartDistance():return 'Kiln Start Distance'
def keyForCurrentDistance(): return "Kiln Current Distance"
def keyForCurrentDisplacement():return 'KilnCurrentDisplacement'

def KilnStartTime():return 'KilnStartTime'
def keyForKilnTimeInHoldMinutes(): return 'KilnTimeInHoldMinutes'
def keyForKilnHoldStartTime(): return "KilnHoldStartTime"
def keyForKilnHeaters(): return 'KilnHeatersReported'
def keyForKilnHeaterCommanded(): return 'KilnHeaterCommanded'
def keyForKilnTemperatures(): return 'KilnTemps'

def keyForKilnSupportFan() : return 'KilnSupportFan'
def keyForKilnSupportFanCommanded() : return 'KilnSupportFan'

def keyForSimulate(): return 'KilnSimulate'
def keyForEmergencyOff(): return 'EmergencyOff'
