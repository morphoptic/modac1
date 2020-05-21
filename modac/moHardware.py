# moData = common data repo under mordac
if __name__ == "__main__":
    print("moHardware has no self test")
    exit(0)
    
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from .moKeys import *
from . import moData, enviro, ad24, ad16, kType, binaryOutputs
from modac import leicaDistoAsync as leicaDisto

# locally required for this module
import trio
import datetime

__initialized = False # : return

__nursery = None
async def init(nursery):
    this.__nursery = nursery
    enviro.init()
    binaryOutputs.init()
    ad24.init()
    ad16.init()
    kType.init()
    leicaDisto.init()
    nursery.start_soon(leicaDisto.runLoop)
    moData.setStatusInitialized()
    # force at least one update so moData is populated
    update()
    log.debug("moData initialized")


def update():
    if not __initialized == True: return

    # get our own timestamp
    moData.updateTimestamp()
    enviro.update()
    binaryOutputs.update()
    ad24.update()
    ad16.update()
    kType.update()
    leicaDisto.update()
#    if not leicaDisto.isRunning():
#        #leicaDisto.update() # leica updates happen in other thread
#        # but if it is dead, try again
#        resetLeicaCmd()

def shutdown():
    this.allOff()
    enviro.shutdown()
    ad24.shutdown()
    ad16.shutdown()
    binaryOutputs.shutdown()
    leicaDisto.shutdown()
    __initialized = False
    log.debug("shutdown hardware")

# TODO should not have two of these!
def allOff():
    binaryOutputs.allOff()    
def allOffCmd():
    binaryOutputs.allOff()

def binaryCmd(channel,onoff):
    log.info("Binary cmd chan %d onOff %r"%(channel,onoff))
    binaryOutputs.setOutput(channel,onoff)

def resetLeicaCmd():
    if this.__nursery == None:
        return
    # dont block like in init(), do it async
    if leicaDisto.isRunning():
        leicaDisto.close()
    leicaDisto.reset()
    this.__nursery.start_soon(leicaDisto.runLoop)

def simulateKiln(onOff=True):
    kType.setSimulate(onOff)
    # leica simulation - done inside kiln
    from kilnControl import kiln
    kiln.setSimulation(onOff)
    
def EmergencyOff():
    from kilnControl import kiln
    log.warn("EMERGENCY OFF tiggered")
    kiln.emergencyShutOff()
