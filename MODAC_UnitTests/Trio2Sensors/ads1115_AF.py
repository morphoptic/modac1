# modac.ad16 : 16 bit Analog-Digital Inputs
# built on ADS1115 adafruit library 16bit i2c A/D module
# initial version supports single ADS1115.
# future will need to configure multiple but still collect them all in one shot

# cute hack to use module namespace this.fIO this.value should work
import sys
this = sys.modules[__name__]

import logging, logging.handlers, traceback
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from time import sleep
import time

#for AD1115 support using adafruit circuitplayground code
# correction - this uses the old Adafruit_Python_ADS1x15 library
# https://github.com/adafruit/Adafruit_Python_ADS1x15
# might be best to drop this for smbus2 version
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
#import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


#7Sept2020 reduce to only one device w 4 channels on default channel
__values = [0,0,0,0]
__volts  = [0.0, 0.0, 0.0, 0.0]
__numChannels = len(__volts)

__moAD16Device = None
__chan0 = None
__chan1 = None
__chan2 = None
__chan3 = None

adsGain = 2/3
#adsGain = 1

def readChans():
    print("0: {:>5}\t{:>5.3f}".format(this.__chan0.value, this.__chan0.voltage))
    print("1: {:>5}\t{:>5.3f}".format(this.__chan1.value, this.__chan1.voltage))
    print("2: {:>5}\t{:>5.3f}".format(this.__chan2.value, this.__chan2.voltage))
    print("3: {:>5}\t{:>5.3f}".format(this.__chan3.value, this.__chan3.voltage))

def init():
    log.warning("initialize AD16 - 16bit A-D converter")
    # init the adafruit i2c bus
    ad16_i2c = busio.I2C(board.SCL, board.SDA)
    if ad16_i2c is None:
        log.error("error getting i2c bus for AD16")
        return
    print("Create ADS1115")
    try:
        this.__moAD16Device = ADS.ADS1115(ad16_i2c)
        this.__moAD16Device.gain = adsGain
        print("ADS1115 Gain: ", this.__moAD16Device.gain)
    except (ValueError, OSError) as e:
        log.error(" Cant create ad16", exc_info=True)
        raise e
      return

    print("Initialized AD16 devices, create 4 channels ")
        
    # init each channel
    try:
        this.__chan0 = AnalogIn(this.__moAD16Device, ADS.P0)
        this.__chan1 = AnalogIn(this.__moAD16Device, ADS.P1)
        this.__chan2 = AnalogIn(this.__moAD16Device, ADS.P2)
        this.__chan3 = AnalogIn(this.__moAD16Device, ADS.P3)
        readChans()
    except OSError as e:
        log.error("error creating channels", exc_info=True)
        raise e

    # now get initial values
    this.update()

def update():
    # feb23 2021 dont disable device on read error.  Might allow several?
    # if this.__isAlive == False:
    #     this.__status = moStatus.Error
    #     moData.update(keyForAD16Status(), this.__status.name)
    #     return

    #log.debug("ad16 update()")
    #print("ad16 has",len(__ad16chanConfig),"channels and ", len(this.__values),"values")
    #print (this.__values)
    # currently crude get all 8 with same default configutation
    try:
        this.__values[0] = this.__chan0.value
        this.__values[1] = this.__chan1.value
        this.__values[2] = this.__chan2.value
        this.__values[3] = this.__chan3.value

        this.__volts[0] = this.__chan0.voltage
        this.__volts[1] = this.__chan1.voltage
        this.__volts[2] = this.__chan2.voltage
        this.__volts[3] = this.__chan3.voltage
    except:
        this.__values = [0]* len(this.__values)
        this.__volts = [0.0] * this.__numChannels
        log.error(" Error reading AD16 values, not disabled", exc_info=True)

    log.info("Ad16 volts "+str(this.__volts))

def values():
    #print("ad16 has",len(__ad16chanConfig),"channels and ", len(this.__values),"values")
    #print (this.__values)
    return this.__values

def volts():
    return this.__volts

def shutdown():
    #hmm release all the channels?
    __moAD16Device = None
    this.__ad16dev = []
    this.__channels = []
    this.__values = []    
