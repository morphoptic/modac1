# modac Kiln Simulator, built on generic modac data acq & control (modac_server)
#  modac server but only for simulating kiln control, no other devices
#  should work in place of modac_server for unit testing (unproven 7May2020)
#
#  Orig Pid etc is based on Oven code found in several github projects.
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

secondsToRunTest = 20

async def simulateKiln():
    print("simulate kiln")
    async with trio.open_nursery() as nursery:
        moData.setNursery(nursery)
        
        await kiln.startKilnControlProcess()
        print("after spawn kiln")
        
        #await kiln.spawnSchedule(5)
        
        print("after spawnSchedule, sleep for ")
        await trio.sleep(secondsToRunTest)
        
        # now end it
        
        kiln.endKilnControlProcess()
        #kiln.loadAndRun()#"kilnControl/testSchedule.csv")
        print("simulateKiln awaiting nursery")
    print("end of simulateKiln")
        
# main for testing
if __name__ == "__main__":
    #log.error("kiln.kiln has no self test")
    print("kiln self test")
    log.info("kiln self test")
    signal.signal(signal.SIGINT, signalExit)
    moData.init(True) # pretend we are a client to get moData initialized
    try:
        print ("try simulate kiln")
        trio.run(simulateKiln)
    except Exception as e:
        print("Exception somewhere in modac_io_server. see log files")
        log.error("Exception happened", exc_info=True)
        log.exception("huh?")
    finally:
        print("end main")
    


