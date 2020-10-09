# kType - convert AD Inputs of thermocouple readings to temperatures
#
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

#import rest of modac
from .moKeys import *
from . import moData
from .moStatus import *
# should revise this so it gets direct from moData rather than having knowledge of other device api?
#from . import ad24, enviro
# locally required for this module

from thermocouples_reference import thermocouples
# only looking at kType thermocouples
__typeK = thermocouples['K']

# cant dunder kTypeIdx 'cause its used in Simulator
status = moStatus.Default

# ktypes in use are White, Green, Yellow (not blue) from amp box
# amp-connector & pi-connector order is Green-White-Yellow-Blue
# this bit ref's 24bit AD which is not being used in later part of PoC project
# see bit below for the AD16
# two 4 chan amps are available, 1st connects AD-2 AD-3, while AD-0 is pot, AD-1=photoSense
# kTypeIdx is indicies into AD array for k-type thermocouple
# Note length must match moData value returned by
#kTypeIdx= [0,1,2,3,4,5,6,7]
#kTypeIdx= [2,3,4,5,6,7]
#kTypeIdx= [3,4,5,6]
kTypeIdx= [4,5,6]

# mods to support data from 16bit AD instead
_use16BitDA = True
if _use16BitDA:
    kTypeIdx = [0,1,2]

ampGain = 122.4 # from ad8495 spec sheet
adOffset = 0.0  #magic offset subtracted from adValue, based on roomtemp reading by ktype

simulation = False
simulator = None

# only looking at kType thermocouples
__kTypeLookup = thermocouples['K']

def adOverGain(adValue):
    return float(adValue - adOffset)/ampGain

def mVToC(mV,tempRef=0.0):
    _mV = mV #fnMagic(mV)
    retVal = __kTypeLookup.inverse_CmV(_mV, Tref=tempRef)
    return retVal

def adToC(adRead,tempRef=0.0):
    try:
        v = adOverGain(adRead)
        #print("adOverGain ad v: ", adRead, v)
    except ValueError:
        log.error("adToC Value error in adOverGain", exc_info=True)

    mv = v*1000.0
    c = 0
    try:
        c = mVToC(mv, tempRef)
    except ValueError:
        log.error("adToC Value error in mVToC", exc_info=True)
    #print ("ad v mv c: ", adRead, v, mv, c)
    return c

def testCalc(mV):
    c0 = mVToC(mV, 0.0)
    c25 = mVToC(mV, 25.0)
    msg = "Temp at mv "+ str(mV) + " = (0):" + str(c0) + " (25):" + str(c25)
    print(msg)
    #log.debug(msg)
    
# inverse_CmV
def calc0_100_300():
    log.debug("CALC REF mV")
    mv = 0.0
    testCalc(mv)
    mv = 1.0
    testCalc(mv)
    mv = 4.096
    testCalc(mv)
    mv = 12.209
    testCalc(mv)
    mv = 0.004037344783333*1000.0
    testCalc(mv)

#this can vary as we develop and test
    # but it doesent help gui so not really useful
def getNumKType():
    num = len(kTypeIdx)
    moData.setNumKType(getNumKType)
    return num

def init():
    this.simulator = None
    this.getNumKType()
    calc0_100_300()
    this.status = moStatus.Initialized
    update()
    pass

def update():
    #assert not moData.getValue(keyForAD24()) is None
    #assert not moData.getValue(keyForEnviro()) is None
    if not this.simulation:
        # not a simulation=  watch for sensor errors (done in asArray)
        moData.update(keyForKType(), asArray())
    else:
        assert not this.simulator is None
        #print("\n\n************\n")
        this.status = moStatus.Simulated
        this.simulator.update()
    moData.update(keyForKTypeStatus(), this.status.name)
    moData.update(keyForKType() + keyForTimeStamp(), moData.generateTimestampStr())

def asArray():
    assert not this.simulation
    ktypeData = []
    # retrieve the ad as 0-5V values
    if _use16BitDA:
        # check for error
        if moData.getValue(keyForAD16Status()) == moStatus.Error.name:
            ktypeData = [0]* len(kTypeIdx)
            this.status = moStatus.Error
            return ktypeData
        else:
            ad16Record = moData.getValue(keyForAD16())
            adArray = ad16Record[keyForAD16()]
        #print("adArray from 16bit ", adArray)
    else:
        adArray = ad24.all0to5Array()
    #print("adArray: ", adArray)
    
    # these are in 0-5v, need in mV range for use with conversion library
    # it is not clear if we should be using the roomTemp as zero point
    # that might need to be a constant from testing with ice water
    #roomTemp = enviro.degC()
    # only look at the ad24 that are identified by the kTypeIdx array
    for adIdx in kTypeIdx:
        t= 0
        try:
            #log.warning("Convert AD idx %d, %d"%(adIdx, adArray[adIdx]))
            t = this.adToC(adArray[adIdx])#roomTemp)
            #print("asArray adidx, v, c",adIdx, adArray[adIdx], t)
        except ValueError:
            log.error("ValueError converting adIdx "+str(adIdx)+ "=> "+str(adArray[adIdx]), exc_info=True)
            t = 0
        except IndexError:
            log.error("IndexError adIdx "+str(adIdx)+ " "+str(adArray), exc_info=True)
        except:
            log.exception("exception in kType asArray()")
            break
        ktypeData.append(t)
    #print ("KType as array", ktypeData)
    return ktypeData

def asDict():
    return {keyForKType(): asArray() }

from kilnControl.kilnConfig import *
from kilnControl import kilnState
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
        # TODO This should be a KilnState. kilnStatus doent index keyForState; because it became an array not dictj  kilnState = kilnStatus[keyForState()]
        binOut = moData.getValue(keyForBinaryOut())
        sum = 0.0
        log.info("\n************\nSIMULATED KTYPE")
        log.info("update simulated ktypes, len " + str(len(self.ktypeData)))
        for i in range(1,len(heaters)):
            heaterOn = binOut[heaters[i]]
            print("Heater ",i, heaters[i], "is ", heaterOn)
            if heaterOn:
                self.ktypeData[i-1] += self.increaseRate *random()
            else:
                self.ktypeData[i-1] -= self.decreseRate *random()
            if binOut[fan_exhaust]:
                self.ktypeData[i-1] -= self.decreseRate *2*random()
            if self.ktypeData[i-1] < 20:
                self.ktypeData[i-1] = 20 # dont let it go below
            sum += self.ktypeData[i-1]
        self.ktypeData[0] = sum/3

        #post updated values to moData
        log.debug("updated Simulated KType data: "+ str( self.ktypeData))
        moData.update(keyForKType(), self.ktypeData)
        
def setSimulate(onOff = True):
    this.simulation = onOff
    if onOff:
        log.info("Simulation of KType is ON")
        this.simulator = SimulateKtypes()
    else:
        log.info("Simulation of KType is OFF")
        this.simulator = None
    log.info("KType values: " +str(moData.getValue(keyForKType())))

if __name__ == "__main__":
    print("modac.kType has no self test")
    exit(0)
  
