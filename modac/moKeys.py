# MODAC keywords
# common file to hold data name keys and convert them to topcis

# topics are UTF8 encoded arrays
def moKeyToTopic(key):
    assert isinstance(key,str)
    return key.encode('utf8')

def keyForAllData():
    return "moData"
def keyForTimeStamp():
    return "timestamp"
def keyForEnviro():
    return "enviro"
def keyForBinaryOut():
    return "binaryOut"
def keyForKType():
    return "kType"
def keyForAD24():
    return "ad24"
def keyForAD24Raw():
    return "ad24Raw"
def keyForAD24v05():
    return "ad24v05"
def keyForHumpidity():
    return "humidity"
def keyForTemperature():
    return "temperature"
def keyForPressure():
    return "pressure"


