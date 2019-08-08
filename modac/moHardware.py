# moData = common data repo under mordac
if __name__ == "__main__":
    print("moHardware has no self test")
    exit(0)
    
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
#import rest of modac
from .moKeys import *
from . import moData, enviro, ad24, ad16, kType, binaryOutputs
from modac import leicaDistoAsync as leicaDisto

# locally required for this module
import trio

__nursery = None
async def init(nursery):
    this.__nursery = nursery
    enviro.init()
    binaryOutputs.init()
    ad24.init()
    ad16.init()
    kType.init()
    await leicaDisto.initAsync(None, nursery)
    # force at least one update so moData is populated
    update()

def update():
    enviro.update()
    binaryOutputs.update()
    ad24.update()
    ad16.update()
    kType.update()
    if not leicaDisto.isRunning():
        #leicaDisto.update() # leica updates happen in other thread
        # but if it is dead, try again
        resetLeicaCmd()

def shutdown():
    this.allOff()
    leicaDisto.shutdown()

def allOff():
    binaryOutputs.allOff()
    
def binaryCmd(channel,onoff):
    binaryOutputs.setOutput(channel,onoff)

def allOffCmd():
    binaryOutputs.allOff()

def resetLeicaCmd():
    if this.__nursery == None:
        return
    # dont block like in init(), do it async
    this.__nursery.start_soon(leicaDisto.initAsync, None, this.__nursery)
 
 
 