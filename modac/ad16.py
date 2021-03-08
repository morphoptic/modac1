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

import sys
from time import sleep
import time

#from . import moduleName
from .moKeys import *
from . import moData
from .moStatus import *
from .moFilteredChannel import FilteredChannel

#for AD1115 support using adafruit circuitplayground code
# correction - this uses the old Adafruit_Python_ADS1x15 library
# https://github.com/adafruit/Adafruit_Python_ADS1x15
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
#import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

__isAlive = False
__status = moStatus.Default

#7Sept2020 reduce to only one device w 4 channels on default channel
__values = [0,0,0,0]
__volts  = [0.0, 0.0, 0.0, 0.0]
__numChannels = len(__volts)
__fChannels = [FilteredChannel(),FilteredChannel(),FilteredChannel(),FilteredChannel()]
__moAD16Device = None
__chan0 = None
__chan1 = None
__chan2 = None
__chan3 = None
__channels = []

adsGain = 2/3
#adsGain = 1

def readChans():
    i = 0
    for c in this.__channels:
        print(i,": {:>5}\t{:>5.3f}".format(c.value, c.voltage))
        i +=1
    #print("1: {:>5}\t{:>5.3f}".format(this.__chan1.value, this.__chan1.voltage))
    #print("2: {:>5}\t{:>5.3f}".format(this.__chan2.value, this.__chan2.voltage))
    #print("3: {:>5}\t{:>5.3f}".format(this.__chan3.value, this.__chan3.voltage))

def init():
    log.warning("initialize AD16 - 16bit A-D converter")
    # init the adafruit i2c bus
    ad16_i2c = busio.I2C(board.SCL, board.SDA)
    if ad16_i2c is None:
        log.error("error getting i2c bus for AD16")
        this.__status = moStatus.Error
        moData.update(keyForAD16(), createUpdateRecord()) #this.__values)
        #moData.update(keyForAD16(), this.__values)
        return
    print("Create ADS1115")
    try:
        this.__moAD16Device = ADS.ADS1115(ad16_i2c)
        this.__moAD16Device.gain = adsGain
        print("ADS1115 Gain: ", this.__moAD16Device.gain)
    except (ValueError, OSError) as e:
        log.error(" Cant create ad16", exc_info=True)
        this.__status = moStatus.Error
        raise e
        exit(0)

    if this.__status == moStatus.Error:
        log.error("some error initializing ad16")
        __isAlive = False
        if this.__status == moStatus.Error:
            this.__values = [0] * this.__numChannels
            this.__volts  = [0.0] * this.__numChannels
        #
        moData.update(keyForAD16(), createUpdateRecord()) #this.__values)
        moData.update(keyForAD16Raw(), this.__values)
        moData.update(keyForAD16Status(), this.__status.name)
        print("Bad Values "+str(this.__values))
        return

    print("Initialized AD16 devices, create 4 channels ")
        
    # init each channel
    try:
        this.__chan0 = AnalogIn(this.__moAD16Device, ADS.P0)
        this.__channels.append(this.__chan0)
        this.__chan1 = AnalogIn(this.__moAD16Device, ADS.P1)
        this.__channels.append(this.__chan1)
        this.__chan2 = AnalogIn(this.__moAD16Device, ADS.P2)
        this.__channels.append(this.__chan2)
        this.__chan3 = AnalogIn(this.__moAD16Device, ADS.P3)
        this.__channels.append(this.__chan3)
        readChans()
    except OSError as e:
        log.error("error creating channels", exc_info=True)
        raise e
    this.__isAlive = True
    
    # now get initial values
    for i in range(10): # load up filtered channels
        this.update()

    for f in this.__fChannels:
        print(f)
        log.info("AD16 chan initialized "+str(f))
    this.__status = moStatus.OK

def createUpdateRecord():
    updateRecord = {
        keyForStatus(): this.__status.name,
        keyForTimeStamp(): moData.generateTimestampStr(),
        keyForAD16(): this.__volts
    }
    return updateRecord

def update():
    # feb23 2021 dont disable device on read error.  Might allow several?
    # if this.__isAlive == False:
    #     this.__status = moStatus.Error
    #     moData.update(keyForAD16Status(), this.__status.name)
    #     return

    try:
        i = 0
        for c in this.__channels:
            v = c.value # reads AD
            try:
                this.__fChannels[i].addValue(v)
                this.__values[i] = v # passed filter, add it, and voltage
                this.__volts[i] = c.voltage
                #msg = f"XXad16 chan{i} v:{v} {this.__fChannels[i]}"
                #log.debug(msg)
            except ValueError as e:
                msg = f"ad16 chan {i} valueError {e}"
                log.error(msg)
            i +=1

        this.__status = moStatus.OK
    except:
        log.error(" Error reading AD16 values, not disabled", exc_info=True)
        this.__status = moStatus.Error
        # need to put at least one record in moData
        moData.update(keyForAD16(), createUpdateRecord()) #this.__values)
        this.__ad16_i2c = None
        # dont
        #this.__isAlive = False
        this.__status = moStatus.Error

    # force error values
    if this.__status == moStatus.Error:
        this.__values = [0]* len(this.__values)
        this.__volts = [0.0] * this.__numChannels
    #
    moData.update(keyForAD16Status(), this.__status.name)
    moData.update(keyForAD16(), createUpdateRecord())
    moData.update(keyForAD16Raw(), this.__values)
    moData.update(keyForAD16Status(), this.__status.name)


def values():
    #print("ad16 has",len(__ad16chanConfig),"channels and ", len(this.__values),"values")
    #print (this.__values)
    return this.__values

def volts():
    return this.__volts

def shutdown():
    #hmm release all the channels?
    this.__ad16dev = []
    this.__channels = []
    this.__values = []    

# these two checks have slightly different meanings.  Alive may be ok until an error occurs
def isError():
    if this.__status == moStatus.Error:
        return True
    return False

def isAlive():
    return this.__isAlive()

def status():
    return this.__status
