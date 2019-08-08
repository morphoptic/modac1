# modac.ad24 : 24 bit Analog-Digital Inputs
# built on waveshareADAC and ADS1256 chip
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]

#import rest of modac
#from . import 
# locally required for this module

import logging, logging.handlers
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

import sys
from time import sleep
import time

#print("importing waveshare")
#if __name__ == "__main__":
#    print("__main__ import from same dir")
#    from waveshareADAC import ADS1256
#else:
#    print("module import from this")
#    from waveshareADAC import ADS1256
from waveshareADAC import ADS1256
    
#from . import moduleName
from .moKeys import *
from . import moData

__ads1256 = None #ADS1256.ADS1256()
__adsRaw = [0,0,0,0,0,0,0,0]
__ads0to5 = [0,0,0,0,0,0,0,0]
__adsRawToV = (5.0/0x7fffff) # magic number to convert raw ADS1256 to 0-5Vdc

__key = "ad24"

def init():
    log.debug("ad24Bit init()")
    this.__ads1256 = ADS1256.ADS1256()
    this.__ads1256.ADS1256_init()
    this.update()
    
def update():
    log.debug("ad24Bit update()")
    # currently crude get all 8 with same default configutatoin
    raw = this.__ads1256.ADS1256_GetAll()
    for i in range(len(raw)):
        this.__adsRaw[i] = raw[i]
        this.__ads0to5[i] = raw[i] * this.__adsRawToV
    moData.update(keyForAD24(), all0to5Array())

def allRawArray():
    return this.__adsRaw

def all0to5Array():
    return this.__ads0to5

def asDict():
    return { keyForAD24(): this.all0to5Array() }

