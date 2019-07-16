# modac_AD24Bit

import logging, logging.handlers
import sys
from time import sleep
import time
from waveshareADAC import ADS1256

__ads1256 = None #ADS1256.ADS1256()
__adsRaw = [0,0,0,0,0,0,0,0]
__ads0to5 = [0,0,0,0,0,0,0,0]
__adsRawToV = (5.0/0x7fffff)

def init():
    global __ads1256
    logging.debug("ad24Bit init()")
    __ads1256 = ADS1256.ADS1256()
    __ads1256.ADS1256_init()

    
def update():
    global __ads1256,__adsRaw,__ads0to5,__adsRawToV
    logging.debug("ad24Bit update()")
    raw = __ads1256.ADS1256_GetAll()
    for i in range(len(raw)):
        __adsRaw[i] = raw[i]
        __ads0to5[i] = raw[i] * __adsRawToV
   
def getRaw():
    return __adsRaw

def getAll0To5():
    global __ads0to5
    return __ads0to5

def doTest():
    data = []
    for repeatCount in range(60):
        update()
        ADC_Value = getAll0To5()
        print(getRaw())
        print(ADC_Value)
        for i in range(len(ADC_Value)):
            print ("%d %d ADC = %lf"%(repeatCount, i, ADC_Value[i]))
            

if __name__ == "__main__":
    print("MorpOptics 24Bit AD Sensor class stand alone test")
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)#, format=logFormatStr)
    logging.captureWarnings(True)
    logging.info("Logging Initialized for MO 24Bit AD  main unitTest")
    init()
    update()
    doTest()
    
