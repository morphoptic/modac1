# moData = common data repo under mordac
if __name__ == "__main__":
    print("moData has no self test")
    exit(0)
    
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
#import rest of modac
from . import enviro, ad24, kType, binaryOutputs

# locally required for this module

__key = "moData"
def key():
    return key;

def topic():
    return __key.encode() # encode as binary UTF8 bytes

def init():
    enviro.init()
    binaryOutputs.init()
    ad24.init()
    kType.init()
    # modac_BLE_Laser.init()
    pass

def update():
    enviro.update()
    binaryOutputs.update()
    ad24.update()
    kType.update()
    # modac_BLE_Laser.update()
    pass

def asDict():
    moData = {
        enviro.key():enviro.asDict(),
        ad24.key():ad24.all0to5Array(),
        kType.key():kType.asArray(),
        binaryOutputs.key():binaryOutputs.asArray()
        }    
    return moData

def allOff():
    binaryOutputs.allOff()
    

