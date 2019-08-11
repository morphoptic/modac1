# modac Kiln Controller, built on generic modac data acq & control
#
#  this is based on Oven code found in several github projects.
#  not sure which is the originator but these all seem to share very similar code
#     https://github.com/apollo-ng/picoReflow
#     https://github.com/jbruce12000/kiln-controller
#  this PID controller also looks really close to one in above projects
#     https://github.com/timdelbruegger/freecopter/blob/master/src/python3/pid.py
#  and is based on an article "Improving Beginners PID"
#     http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/
#
#  we link into the modac.moData blackboard of shared data for sensors
#  and can either use direct controls of the BinaryOutput/DA effectors
#  or use the pyNNG network commands, or perhaps the moHardware level commands
#  which would get the commands logged at that level
    
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import signal
#import rest of modac
#from modac.moKeys import *
#from modac import moData, moHardware

import trio

#import kilnControl.config as config
from modac import moLogger, moData
moLogger.init()

from kilnControl import kiln
print(" continue with kilnController")

def signalExit(*args):
    print("signal exit! someone hit ctrl-C?")
    exit(0)

async def simulateKiln():
    print("simulate kiln")
    async with trio.open_nursery() as nursery:
        moData.setNursery(nursery)
        kiln.startKiln()
        print("after spawn kiln")
        await kiln.spawnSchedule(5)
        print("after spawnSchedule, sleep for while")
        await trio.sleep(90)
        kiln.endKiln()
        #kiln.loadAndRun()#"kilnControl/testSchedule.csv")
        print("simulateKiln awaiting nursery")
    print("end of simulateKiln")
        
# main for testing
if __name__ == "__main__":
    #log.error("kiln.kiln has no self test")
    print("kiln self test")
    log.info("kiln self test")
    signal.signal(signal.SIGINT, signalExit)
    moData.init()
    try:
        print ("try simulate kiln")
        trio.run(simulateKiln)
    except Exception as e:
        print("Exception somewhere in modac_io_server. see log files")
        log.error("Exception happened", exc_info=True)
        log.exception("huh?")
    finally:
        print("end main")
    


