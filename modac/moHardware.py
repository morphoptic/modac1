# moData = common data repo under mordac
if __name__ == "__main__":
    print("moHardware has no self test")
    exit(0)
    
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
#import rest of modac
from .moKeys import *
from . import moData, enviro, ad24, ad16, kType, binaryOutputs, leicaDisto

# locally required for this module

def init():
    enviro.init()
    binaryOutputs.init()
    ad24.init()
    ad16.init()
    kType.init()
    leicaDisto.init()
    # modac_BLE_Laser.init()
    # force at least one update so moData is populated
    update()
    pass

def update():
    enviro.update()
    binaryOutputs.update()
    ad24.update()
    ad16.update()
    kType.update()
    leicaDisto.update()
    # modac_BLE_Laser.update()
    #moData.update(keyForAllData(), asDict())
    pass

def shutdown():
    this.allOff()
    leicaDisto.shutdown()


#def asDict():
#    moHW = {
#        keyForEnviro():enviro.asDict(),
#        keyForAD24():ad24.all0to5Array(),
#        keyForKType():kType.asArray(),
#        keyForBinaryOut():binaryOutputs.asArray()
#        }    
#    return moHW

def allOff():
    binaryOutputs.allOff()
    
def binaryCmd(channel,onoff):
    binaryOutputs.setOutput(channel,onoff)

def allOffCmd():
    binaryOutputs.allOff()

