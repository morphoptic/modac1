# MODAC keywords
# common file to hold data name keys and convert them to topics and labeled JSON data, also ties to GUI builder

# topics are UTF8 encoded arrays
def moKeyToTopic(key):
    assert isinstance(key,str)

    return key.encode('utf8')
def keyForTimeFormat():
    return "%Y-%m-%d %H:%M:%S%Z"

def keyForNotStarted(): return "NotStarted"

# at this point we are really only using AllData and Cmd for net comms
# but other keys are used for getting data from the moData active data repository
def keyForAllData(): return "allData"
def keyForShutdown():   return "shutdown"

# generic keys used by various components
# timestamp key used for all data, enviro and leicaDisto
def keyForTimeStamp(): return "timestamp"
# Generic keywords for State, etc used by any state machine in its own context
def keyForState(): return 'State'
def keyForStatus(): return "Status"
def keyForScript(): return "Script"
def keyForIndex(): return "Index"

# these are data from Enviro Sensor (BMEchip)
def keyForEnviro(): return "enviro"
def keyForHumidity(): return "humidity"
def keyForTemperature(): return "temperature"
def keyForPressure(): return "pressure"

# array of Binary Outputs - relays etc 
def keyForBinaryOut(): return "binaryOut"

# Two types of AnalogDigital Converters, with minimal control provided
# AD16 holds array of 16bit AD input channels  generally 0-5v measure
def keyForAD16(): return "ad16"
def keyForAD16Raw(): return "ad16Raw"

# AD24 holds array of 24bit input channels  generally 0-5v measure
def keyForAD24(): return "ad24"
def keyForAD24Raw(): return "ad24Raw"
def keyForAD24v05(): return "ad24v05"

# array of K Type Thermocouple channels DegC units
def keyForKType(): return "kType"

# Leica Disto D1 distance sensor
def keyForLeicaDisto(): return "leicaD1"
def keyForDistance(): return "distance"

def keyForBaumerOM70(): return "BaumerOM70"
# some combined keys
def keyForAD16Status() : return keyForAD16()+ "_" + keyForStatus()
def keyForKTypeStatus() : return keyForKType()+ "_" + keyForStatus()

#keys for commands from clients
def keyForHello() : return "Hello"
def keyForGoodbye() : return "Goodbye"
def keyForShutdown(): return "Shutdown"

def keyForModacCmd(): return "modac"
def keyForBinaryCmd(): return "binaryCmd"
def keyForAllOffCmd(): return "allOff"
def keyForResetLeica(): return "leicaReset"

# kiln commands, status, state stuff
## start/abort cmd == btn name but be kinda explicit
def keyForStartKilnProcess(): return "StartKilnProcess"
def keyForEndKilnProcess(): return "EndKilnProcess"
# start, end a script
def keyForRunKilnScript(): return "RunKilnScript"
def keyForStopKilnScript(): return "StopKilnScript"
def keyForKilnScriptEnded(): return "KilnScriptEnded"
# for kiln panel buttons
def keyForLoadKilnScript(): return "LoadKilnScript"
def keyForSaveKilnScript(): return "SaveKilnScript"

# kiln data
def keyForKilnStatus(): return "KilnStatus"  # full status of kiln data, hierarchial dict
def keyForKilnScriptStatus(): return "KilnScriptStatus"  # full status of kiln data, hierarchial dict
# kilnState uses keyForState() but add special so we can CSV easy
def keyForKilnState(): return "KilnState";
def keyForKilnScriptState(): return "KilnScriptState";
def keyForKilnRuntime(): return 'KilnProcessRuntime'
def keyForKilnStartTime(): return 'KilnScriptStartTime'

def keyForScriptName(): return "ScriptName"
def keyForScriptDescription(): return "ScriptDescription"

def keyForScriptSegments(): return "ScriptSegments"

# kiln Script Segment Control Data
def keyForTargetTemp(): return 'KilnTargetTemp'
def keyForKilnHoldTimeMin(): return 'KilnHoldTimeMin'
def keyForKilnHoldTimeSec(): return 'KilnHoldTimeSec'
def keyForTargetDisplacement():return 'KilnTargetDisplacement'
def keyForPIDStepTime(): return "PIDStepTime"
def keyForExhaustFan(): return "ExhaustFan"
def keyForSupportFan(): return "SupportFan"
def keyFor12vRelay(): return "12vRelay"
def keyForSegmentIndex(): return 'SegmentIndex'

# TODO not sure what this is anymore
def keyForMaxTime():return 'KilnMaxTime'

# kiln Script runtime data
def keyForScriptRuntimeData() : return "ScriptRuntimeData"
def keyForScriptCurrentSegmentIdx(): return "CurrentSegmentIdx"
def keyForStartDistance():return 'Kiln Start Distance'
def keyForCurrentDistance(): return "Kiln Current Distance"
def keyForCurrentDisplacement():return 'KilnCurrentDisplacement'

def KilnStartTime():return 'KilnStartTime'
def keyForKilnTimeInHoldMinutes(): return 'KilnTimeInHoldMinutes'
def keyForKilnTimeInHoldSeconds(): return 'KilnTimeInHoldSeconds'
def keyForKilnHoldStartTime(): return "KilnHoldStartTime"
def keyForKilnHeaters(): return 'KilnHeatersReported'
def keyForKilnHeaterCommanded(): return 'KilnHeaterCommanded'
def keyForKilnTemperatures(): return 'KilnTemps'

def keyForKilnSupportFanActual() : return 'KilnSupportFanActual'
def keyForKilnSupportFanCommanded() : return 'KilnSupportFanCommanded'
def keyForKilnExhaustFanActual() : return 'KilnExhaustFanActual'
def keyForKilnExhaustFanCommanded() : return 'KilnExhaustFanCommanded'

def keyForSimulate(): return 'KilnSimulate'
def keyForEmergencyOff(): return 'EmergencyOff'
