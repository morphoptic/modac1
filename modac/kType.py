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
# ktypes in use are White, Green, Yellow (not blue) from amp box
# amp-connector & pi-connector order is Green-White-Yellow-Blue
# two 4 chan amps are available, 1st connects AD-2 AD-3, while AD-0 is pot, AD-1=photoSense
#kTypeIdx= [0,1,2,3,4,5,6,7] # indicies into AD24Bit array for k-type thermocouple
kTypeIdx= [2,3,4,5,6,7] # indicies into AD24Bit array for k-type thermocouple

ampGain = 122.4 # from ad8495 spec sheet
# offset at Zero calculated by average of 3 sensors run over 1min
offsetAt0C = 0.645016706666667
offsetAt0C = 0.131  # value of shorted amp 
offsetAt0C = 0.03331469 # kiln couple in ice Dec3

#offsetAt0C = 0.13412795
#medianAtRoom = 0.23279848

offsetAt0COverGain = offsetAt0C/ampGain

simulation = False
simulator = None

def mvOverGain(readMV):
    return readMV/ampGain

def fnMagic(readMV):
    ### convert readMV into proper mV for mvToC
    # values from calibration runs.
    # noted significant variation by sensor and channel
    # but for simplicity now we use simple offset
    # median ad0-5 at 0C = 0.13412795V
    # median ad0-5 at room 25.539 = 0.23279848V
    mV = (readMV - offsetAt0C)/ ampGain
    #print("fnMagic %8.5f => %8.5f"%(readMV,mV))
    return mV

    # vOut = T*5mV = T* 0.005V
    # T = vOut / 0.005 + magic
    # table says 0C is 0.000 (3deg is 0.119mV)
    # table says 25 is 1.0000mV = 0.001V
    #magicNumber = (0.001f)/0.23279848f
    #print("fnMagic ", magicNumber)
    

def mVToC(mV,tempRef=0):
    _mV = fnMagic(mV)
    return __typeK.inverse_CmV(_mV, Tref=tempRef)

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
    # these are in 0-5v, need in mV range for use with conversion library
    # it is not clear if we should be using the roomTemp as zero point
    # that might need to be a constant from testing with ice water
    roomTemp = enviro.degC()
    # only look at the ad24 that are identified by the kTypeIdx array
    for i in kTypeIdx:
        # really crude T=(Vout-1.25)/0.005
        t= (adArray[i]-1.25)/0.005
        #t = this.mVToC(adArray[i]) #,roomTemp)
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
  
