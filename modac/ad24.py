# modac.ad24 : 24 bit Analog-Digital Inputs
# built on waveshareADAC and ADS1256 chip
# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]

#import rest of modac
#from . import 
# locally required for this module

import logging, logging.handlers
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

__ads1256 = None #ADS1256.ADS1256()
__adsRaw = [0,0,0,0,0,0,0,0]
__ads0to5 = [0,0,0,0,0,0,0,0]
__adsRawToV = (5.0/0x7fffff) # magic number to convert raw ADS1256 to 0-5Vdc

__key = "ad24"
__key_ad24Raw = "ad24Raw"
__key_ad24v05 = "ad24v05"

def key():
    return __key;

def topic():
    return __key.encode() # encode as binary UTF8 bytes

def keyRaw():
    return __key_ad24Raw;

def topicRaw():
    return __key_ad24Raw.encode() # encode as binary UTF8 bytes

def keyV05():
    return __key_ad24v05;

def topicVv05():
    return __key_ad24v05.encode() # encode as binary UTF8 bytes

def init():
    logging.debug("ad24Bit init()")
    this.__ads1256 = ADS1256.ADS1256()
    this.__ads1256.ADS1256_init()
    
def update():
    logging.debug("ad24Bit update()")
    # currently crude get all 8 with same default configutatoin
    raw = this.__ads1256.ADS1256_GetAll()
    for i in range(len(raw)):
        this.__adsRaw[i] = raw[i]
        this.__ads0to5[i] = raw[i] * this.__adsRawToV
   
def allRawArray():
    return this.__adsRaw

def all0to5Array():
    return this.__ads0to5

def asDict():
    return { __key : this.all0to5Array() }

def doTest():
    data = []
    for repeatCount in range(60):
        this.update()
        ADC_Value = this.all0to5Array()
        print(this.allRawArray())
        print(ADC_Value)
        for i in range(len(ADC_Value)):
            print ("%d %d ADC = %lf"%(repeatCount, i, ADC_Value[i]))
        print("asDict", this.asDict())
        
if __name__ == "__main__":
    print("MorpOptics 24Bit AD Sensor class stand alone test")
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)#, format=logFormatStr)
    logging.captureWarnings(True)
    logging.info("Logging Initialized for MO 24Bit AD  main unitTest")
    init()
    update()
    doTest()
    