# moData = common data repo under mordac
if __name__ == "__main__":
    print("moHardware has no self test")
    exit(0)
    
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
#import rest of modac
from .moKeys import *
from . import moData, enviro, ad24, kType, binaryOutputs

# locally required for this module

def init():
    enviro.init()
    binaryOutputs.init()
    ad24.init()
    kType.init()
    # modac_BLE_Laser.init()
    # force at least one update so moData is populated
    update()
    pass

def update():
    enviro.update()
    binaryOutputs.update()
    ad24.update()
    kType.update()
    # modac_BLE_Laser.update()
    #moData.update(keyForAllData(), asDict())
    pass

def asDict():
    moHW = {
        keyForEnviro():enviro.asDict(),
        keyForAD24():ad24.all0to5Array(),
        keyForKType():kType.asArray(),
        keyForBinaryOut():binaryOutputs.asArray()
        }    
    return moHW

def allOff():
    binaryOutputs.allOff()
    

