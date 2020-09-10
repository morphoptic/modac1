#testKtype
import sys
this = sys.modules[__name__]
import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from time import sleep
import datetime
import numpy as np

from thermocouples_reference import thermocouples

# only looking at kType thermocouples
__kTypeLookup = thermocouples['K']

def mVToC(mV,tempRef=0):
    print("mv:", mV)
    _mV = mV #fnMagic(mV)
    return __kTypeLookup.inverse_CmV(_mV, Tref=tempRef)

def testCalc(mV):
    c0 = mVToC(mV, 0.0)
    c25 = mVToC(mV, 25.0)
    msg = "Temp at mv"+ str(mV) + " = (0):" + str(c0) + " (25):" + str(c25)
    print(msg)
    return c0
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
    mv =     0.004037344783333*1000.0
    testCalc(mv)

ampGain = 122.4 # from ad8495 spec sheet
adOffset = 0.0  #magic offset subtracted from adValue, based on roomtemp reading by ktype

def adOverGain(adValue):
    return float(adValue - adOffset)/ampGain

def adToC(adRead,tempRef=0.0):
    v=0
    try:
        v = adOverGain(adRead)
        print("adOverGain ad v: ", adRead, v)
    except ValueError:
        log.error("adToC Value error in adOverGain", exc_info=True)

    mv = v *1000.0
    c = 0
    try:
        c = testCalc(mv) #mVToC(mv, tempRef)
    except ValueError:
        log.error("adToC Value error in mVToC", exc_info=True)
    #print ("ad v mv c: ", adRead, v, mv, c)
    return c

def calcAdValues():
    for advalue in np.arange(0.12, 0.2,0.01):
        try:
            adToC(advalue)
        except:
            log.error("error in adToC", exc_info=True)

if __name__ == "__main__":
    #    
    print("MorpOptics 24bAD Ktype Calibration Test")
#    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)#, format=logFormatStr)
#    logging.captureWarnings(True)
#    logging.info("Logging Initialized for MO 24Bit AD  main unitTest")
    #
    calc0_100_300()
    print("Now test with AD values")
    calcAdValues()
