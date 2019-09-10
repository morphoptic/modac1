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

# kiln state
def keyForRunKilnCmd(): return "runKiln"
def keyForKilnAbortCmd(): return "abortKiln"

def keyForKilnStatus(): return "KilnStatus"
def keyForRuntime(): return 'runtime'
def keyForTargetTemp(): return 'targetTemp'
def keyForState(): return 'state'
def keyForTotalTime():return 'totaltime'
def keyForStartTime():return 'start_time'
def keyForDeflectionDist():return 'deflectionDist'
def keyForMaxTime():return 'maxTime'
def keyForStartDist():return 'startDist'
def keyForCurrDeflection():return 'currDeflection'
def keyForTargetDist():return 'targetDist'
def keyForTimeStep(): return"time_step"
