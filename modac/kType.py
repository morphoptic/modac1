# kType
if __name__ == "__main__":
    print("modac.kType has no self test")
    exit(0)
  
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]
#import rest of modac
from . import ad24, enviro
# locally required for this module
import logging, logging.handlers

from thermocouples_reference import thermocouples

__key = "kType"
def key():
    return __key;

def topic():
    return __key.encode() # encode as binary UTF8 bytes

__typeK = thermocouples['K']
__kTypeIdx= [4,5,6] #indexs into AD24Bit array for k-type thermocouple
# todo - convert this to channels ad24.a0() or something better

def mVToC(mV,tempRef=0):
    return __typeK.inverse_CmV(mV, Tref=tempRef)

def init():
    pass

def update():
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
    return {__key : asArray() }
