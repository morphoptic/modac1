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
    _mV = mV #fnMagic(mV)
    return __kTypeLookup.inverse_CmV(_mV, Tref=tempRef)

def testCalc(mV):
    c0 = mVToC(mV, 0.0)
    c25 = mVToC(mV, 25.0)
    msg = "Temp at mv"+ str(mV) + " = (0):" + str(c0) + " (25):" + str(c25)
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
    mv =     0.004037344783333*1000.0
    testCalc(mv)


if __name__ == "__main__":
    #    
    print("MorpOptics 24bAD Ktype Calibration Test")
#    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)#, format=logFormatStr)
#    logging.captureWarnings(True)
#    logging.info("Logging Initialized for MO 24Bit AD  main unitTest")
    #
    calc0_100_300()
