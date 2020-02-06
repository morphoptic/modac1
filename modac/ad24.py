# modac.ad24 : 24 bit Analog-Digital Inputs
# built on waveshareADAC and ADS1256 chip
# two arrays are kept by update() - raw and 0-5V
# only the 0-5V is reported to moData
#

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

# two 4 chan amps are available, 1st connects AD-2 AD-3, while AD-0 is pot, AD-1=photoSense

__ads1256 = None #ADS1256.ADS1256()
__adsRaw = [0,0,0,0,0,0,0,0]
__ads0to5 = [0,0,0,0,0,0,0,0]
__adsRawToV = (5.0/0x7fffff) # magic number to convert raw ADS1256 to 0-5Vdc

__key = "ad24"
__isAlive = False

def init():
    print("ad24Bit init() scaling 0-5V by %10.9f"%(__adsRawToV*1000))
    log.debug("ad24Bit init() ")
    this.__ads1256 = ADS1256.ADS1256()
    if this.__ads1256 == None:
        log.error("error creating ads1256 A-D Converter")
    else:
        initRet = this.__ads1256.ADS1256_init()
        if initRet > 0:
            this.__isAlive = True
        else:
            log.error("error initializing ADS1256 A-D Converter")
    this.update()
    log.debug("ad24Bit init() complete ... successs? = "+str(this.__isAlive))

    
def update():
    #log.debug("ad24Bit update()")
    # currently crude get all 8 with same default configutatoin
    if this.__ads1256 == None:
        log.error("No device present, maybe shutdown")
        return
    if this.__isAlive == False:
        return
    raw = this.__ads1256.ADS1256_GetAll()
    for i in range(len(raw)):
        this.__adsRaw[i] = raw[i]
        this.__ads0to5[i] = raw[i] * this.__adsRawToV
    moData.update(keyForAD24(), all0to5Array())
    moData.update(keyForAD24Raw(), allRawArray())

def allRawArray():
    return this.__adsRaw

def all0to5Array():
    '''return values scaled to 0-5V readings'''
    return this.__ads0to5

def asDict():
    return { keyForAD24(): this.all0to5Array() }

def shutdown():
    this.__ads1256 = None

