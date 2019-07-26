# moData = common data repo under mordac
if __name__ == "__main__":
    print("moData has no self test")
    exit(0)
    
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
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
    update(keyForKType(), None)
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
    
def binaryCmd(channel, onOff):
    print("binaryCmd %d", channel)
    print(onOff)
    
