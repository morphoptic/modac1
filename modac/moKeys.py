# MODAC keywords
# common file to hold data name keys and convert them to topcis

# topics are UTF8 encoded arrays
def moKeyToTopic(key):
    assert isinstance(key,str)
    return key.encode('utf8')

# at this point we are really only using AllData and Cmd for net comms
# but other keys are used for getting data from the moData active data repository
def keyForAllData():
    return "allData"
def keyForShutdown():
    return "shutdown"

# timestamp key used for all data, enviro and leicaDisto
def keyForTimeStamp():
    return "timestamp"
def keyForStatus():
    return "status"

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

def keyForModacCmd():
    return "modac"
def keyForBinaryCmd():
    return "binaryCmd"
def keyForAllOffCmd():
    return "allOff"
def keyForResetLeica():
    return "leicaReset"

# kiln state stuff
## start/abort cmd == btn name but be kinda explicit
def keyForRunKiln(): return "RunKiln"
def keyForAbortKiln(): return "AbortKiln"
def keyForRunKilnCmd(): return keyForRunKiln()
def keyForKilnAbortCmd(): return keyForKilnAbort()

def keyForKilnStatus(): return "KilnStatus"
def keyForRuntime(): return 'Runtime'
def keyForTargetTemp(): return 'TargetTemp'
def keyForState(): return 'State'
def keyForStartTime():return 'StartTime'
def keyForTargetDisplacement():return 'TargetDisplacement'
def keyForMaxTime():return 'MaxTime'
def keyForStartDist():return 'StartDistance'
def keyForCurrDisplacement():return 'CurrentDisplacement'
def keyForTargetDist():return 'TargetDistance'
def keyForTimeStep(): return 'TimeStep'
def keyForKilnHeaters(): return 'KilnHeaters'
def keyForKilnHeaterCmd(): return 'KilnHeaterCmd'
def keyForKilnTemps(): return 'KilnTemps'

def keyForSimulate(): return 'Simulate'
def keyForEmergencyOff(): return 'EmergencyOff'
