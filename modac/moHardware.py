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
from . import moData, enviro, ad16, kType, binaryOutputs
from BaumerOM70 import modacBaumerClient
#from modac import leicaDistoAsync as leicaDisto

# locally required for this module
import trio
import datetime

__initialized = False # : return

__nursery = None
async def init(nursery, nosensors = False):
    this.__nursery = nursery
    binaryOutputs.init()
    try:
        await modacBaumerClient.start(nursery)
        enviro.init()
        # ad24.init()
        ad16.init()
        kType.init()
        # leica distance sensor needs to run its own thread/process
        #support noLeica cli option?
        #leicaDisto.init()
        #nursery.start_soon(leicaDisto.runLoop)
    except (ValueError, OSError) as e:
        log.error("Error starting sensors ", exc_info=True)
        if not nosensors:
            #need to re-raise that
            raise e
    this.__initialized = True  # : return
    moData.setStatusInitialized()
    # force at least one update so moData is populated
    if not this.update():
        log.error("Failed to update on init")
        this.__initialized = False
        moData.setStatusError()
    log.debug("moData initialized")


def update():
    if not __initialized == True: return

    try:
        # get our own timestamp
        # TODO: trio locks
        moData.updateTimestamp()
        binaryOutputs.update()
        # ad24.update()
        ad16.update()
        kType.update()
        modacBaumerClient.update()
        #leicaDisto.update()
        enviro.update()
        return True
    except:
        log.error("Exception in MoHardware Update", exc_info=True)
        #exc = traceback.format_exc()
        #log.error("Traceback is: " + exc)
        moData.setStatusError()
        return False

def updateKilnSensors():
    if not __initialized == True: return

    try:
        # get our own timestamp
        moData.updateTimestamp()
        binaryOutputs.update()
        ad16.update()
        kType.update()
        enviro.update()
        return True
    except:
        log.error("Exception in MoHardware Update", exc_info=True)
        #exc = traceback.format_exc()
        #log.error("Traceback is: " + exc)
        moData.setStatusError()
        return False


#    if not leicaDisto.isRunning():
#        #leicaDisto.update() # leica updates happen in other thread
#        # but if it is dead, try again
#        resetLeicaCmd()

def shutdown():
    this.allBinaryOffCmd()
    enviro.shutdown()
    # ad24.shutdown()
    ad16.shutdown()
    binaryOutputs.shutdown()
    modacBaumerClient.shutdown()
    #leicaDisto.shutdown()
    __initialized = False
    log.debug("shutdown hardware")

def allBinaryOffCmd():
    binaryOutputs.allOff()

def binaryCmd(channel,onoff):
    log.info("Binary cmd chan %d onOff %r"%(channel,onoff))
    binaryOutputs.setOutput(channel,onoff)

def resetLeicaCmd():
    if this.__nursery is None:
        return
    # dont block like in init(), do it async
    # if leicaDisto.isRunning():
    #     leicaDisto.close()
    # leicaDisto.reset()
    # this.__nursery.start_soon(leicaDisto.runLoop)
    pass

def simulateKiln(onOff=True):
    kType.setSimulate(onOff)
    # leica simulation - done inside kiln
    from kilnControl import kiln
    kiln.setSimulation(onOff)

def EmergencyOff():
    from kilnControl import kiln
    log.warning("EMERGENCY OFF tiggered")
    moData.setStatusError()
    kiln.emergencyShutOff()
