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
__kTypeIdx= [4,5,6,7] #indexs into AD24Bit array for k-type thermocouple
# TODO - expand to AD16 as well

def mVToC(mV,tempRef=0):
    return __typeK.inverse_CmV(mV, Tref=tempRef)

def init():
    update()
    pass

def update():
    assert not moData.getValue(keyForAD24()) == None
    assert not moData.getValue(keyForEnviro()) == None
    moData.update(keyForKType(), asArray())
    pass

def asArray():
    ktypeData = []
    adArray = ad24.all0to5Array()
    roomTemp = enviro.degC()
    for i in __kTypeIdx:
        t = this.mVToC(adArray[i],roomTemp)
        #print("ktype", i, t)
        ktypeData.append(t)
    return ktypeData

def asDict():
    return {keyForKType(): asArray() }

if __name__ == "__main__":
    print("modac.kType has no self test")
    exit(0)
  
