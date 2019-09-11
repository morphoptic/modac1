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

__typeK = thermocouples['K']
# cant dunder kTypeIdx 'cause its used in Simulator
kTypeIdx= [4,5,6,7] #indexs into AD24Bit array for k-type thermocouple

simulation = False
simulator = None

def mVToC(mV,tempRef=0):
    return __typeK.inverse_CmV(mV, Tref=tempRef)

def init():
    update()
    pass

def update():
    assert not moData.getValue(keyForAD24()) == None
    assert not moData.getValue(keyForEnviro()) == None
    if not this.simulation:
        moData.update(keyForKType(), asArray())
    else:
        assert not this.simulator == None
        this.simulator.update()
    pass

def asArray():
    ktypeData = []
    adArray = ad24.all0to5Array()
    roomTemp = enviro.degC()
    for i in kTypeIdx:
        t = this.mVToC(adArray[i],roomTemp)
        #print("ktype", i, t)
        ktypeData.append(t)
    return ktypeData

def asDict():
    return {keyForKType(): asArray() }

from kilnControl.kilnConfig import *
from kilnControl.kiln import KilnState

class SimulateKtypes:
    startTemp = 0
    increaseRate = 1.0 # degC per update
    decreseRate = 1.0 # degC per update
    ktypeData = []

    def __init__(self):
        self.startTemp = enviro.degC()
        for i in range(len(kTypeIdx)):
            self.ktypeData.append(self.startTemp)

    def update():
        kilnStatus = moData.getValue(keyForKilnStatus())
        kilnState = kilnStatus[getKeyForState()]
        
        if KilnState[kilnState] > KilnState.Idle:
            binOut = moData.getValue(keyForBinaryOut())
            heaterOn = binOut[heater_combined]
            if heaterOn:
                for d in self.ktypeData:
                    d += increaseRate
            exhaustOn = binOut[fan_exhaust]
            if exhaustOn:
                for d in self.ktypeData:
                    d -= decreseRate
        #post updated values to moData
        moData.update(keyForKType(), self.ktypeData)
        
def setSimulate(onOff = True):
    this.simulate = onOff
    if onOff:
        log.info("Simulation of KType is ON")
        this.simulator = SimulateKtypes()
    else:
        log.info("Simulation of KType is OFF")
        this.simulator = None

if __name__ == "__main__":
    print("modac.kType has no self test")
    exit(0)
  
