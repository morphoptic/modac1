# kType
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

#import rest of modac
from .moKeys import *
from . import moData
# should revise this so it gets direct from moData rather than having knowledge of other device api?
from . import ad24, enviro
# locally required for this module

from thermocouples_reference import thermocouples

# only looking at kType thermocouples
__typeK = thermocouples['K']

# cant dunder kTypeIdx 'cause its used in Simulator
# list 4 but only use idx 1-3 so it matches kilnHeaters etc 
kTypeIdx= [0,5,6,7] # indicies into AD24Bit array for k-type thermocouple

simulation = False
simulator = None

def mVToC(mV,tempRef=0):
    return __typeK.inverse_CmV(mV, Tref=tempRef)

def init():
    this.simulator = None
    update()
    pass

def update():
    #assert not moData.getValue(keyForAD24()) == None
    #assert not moData.getValue(keyForEnviro()) == None
    if not this.simulation:
        moData.update(keyForKType(), asArray())
    else:
        assert not this.simulator == None
        print("\n\n************\n")
        print("SIMULATED KTYPE")
        print("************\n")
        this.simulator.update()
    pass

def asArray():
    assert not this.simulation
    ktypeData = []
    # retrieve the ad as 0-5V values
    adArray = ad24.all0to5Array()
    # it is not clear if we should be using the roomTemp as zero point
    # that might need to be a constant from testing with ice water
    roomTemp = enviro.degC()
    # only look at the ad24 that are identified by the kTypeIdx array
    for i in kTypeIdx:
        t = this.mVToC(adArray[i],roomTemp)
        #print("ktype", i, t)
        ktypeData.append(t)
    return ktypeData

def asDict():
    return {keyForKType(): asArray() }

from kilnControl.kilnConfig import *
from kilnControl.kiln import KilnState
from random import random

class SimulateKtypes:
    startTemp = 0
    increaseRate = 5.0 # degC per update
    decreseRate = 5.5 # degC per update
    ktypeData = []

    def __init__(self):
        self.ktypeData = moData.getValue(keyForKType())
        print("Simulated KType initial data: ", self.ktypeData)

    def update(self):
        '''simulate KType temps: if heat on/off incr/decr
            by rates * random() '''
        kilnStatus = moData.getValue(keyForKilnStatus())
        kilnState = kilnStatus[keyForState()]
        binOut = moData.getValue(keyForBinaryOut())
        sum = 0.0
        for i in range(1,len(heaters)):
            heaterOn = binOut[heaters[i]]
            if heaterOn:
                print("Heater ",i, heaters[i], "is On")
                self.ktypeData[i] += self.increaseRate *random()
            if binOut[fan_exhaust]:
                self.ktypeData[i] -= self.decreseRate *random()
            sum += self.ktypeData[i]
        self.ktypeData[0] = sum/3

        #post updated values to moData
        print("Simulated KType data: ", self.ktypeData)
        moData.update(keyForKType(), self.ktypeData)
        
def setSimulate(onOff = True):
    this.simulation = onOff
    if onOff:
        log.info("Simulation of KType is ON")
        this.simulator = SimulateKtypes()
    else:
        log.info("Simulation of KType is OFF")
        this.simulator = None

if __name__ == "__main__":
    print("modac.kType has no self test")
    exit(0)
  
