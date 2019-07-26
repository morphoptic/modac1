# modac.ad16 : 16 bit Analog-Digital Inputs
# built on ADS1115 adafruit library 16bit i2c A/D module
# initial version supports single ADS1115.
# future will need to configure multiple but still collect them all in one shot

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

#from . import moduleName
from .moKeys import *
from . import moData

#for AD1115 support
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
__ad16_i2c = None 

# Create the ADC objects using the I2C bus and deviceAddresses
# for each device enter its address in this array
# default is one at 72
__ad16devAddr = [72]
__ad16dev = None

# Define channels of single-ended inputs
# each entry of array is a Dict that specifies
#  * the device index (used for the __ad16dev arrays),
#  * the channel on device,
#  * slot for the Analog() object
__ad16chan = [
    { devIdx=0, devChan=ADS.P0, adsChan=None}
    { devIdx=0, devChan=ADS.P1, adsChan=None}
    { devIdx=0, devChan=ADS.P2, adsChan=None}
    { devIdx=0, devChan=ADS.P3, adsChan=None}
]

def init():
    # init the adafruit i2c bus
    this.__ad16_i2c = busio.I2C(board.SCL, board.SDA)
    # init each defined device
    for idx in range(len(this.__ad16devAddr)):
        dev = ADS.ADS1015(this.__ad16_i2c, address=this.__ad16devAddr[idx])
        this.__ad16dev[i] = dev
    # init each channel
    for idx in range(len(this.__ad16chan)):
        chan = AnalogIn(this.__ad16chan[idx].devIdx, this.__ad16chan[idx].devChan)
        this.__ad16chan[idx].adsChan = chan
        
    this.update()
    
def update():
    logging.debug("ad16 update()")
    # currently crude get all 8 with same default configutatoin
    raw = this.__ads1256.ADS1256_GetAll()
    for i in range(len(raw)):
        this.__adsRaw[i] = raw[i]
        this.__ads0to5[i] = raw[i] * this.__adsRawToV
    moData.update(keyForAD24(), all0to5Array())


#
#print("{:>5}\t{:>5}".format('raw', 'v'))
#
#while True:
#    print("{:>5}\t{:>5.3f}".format(chan.value, chan.voltage))
#    time.sleep(0.5)
